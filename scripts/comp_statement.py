"""Monthly referral-compensation statements, one per partner.

Inputs (CSV, rename headers after export from GHL so they match):
  referrals.csv  contact_id, patient_name, referral_partner_id, referral_date, stage, enrollment_date
  payments.csv   contact_id, date, amount        (refunds/chargebacks as negative amounts)
  partners.csv   partner_id, partner_name, comp_structure, comp_rate, w9_on_file   (optional;
                 overrides --structure/--rate per partner, which is how structure changes stay a setting)

Structures:
  pct_collected   rate x net collected this month from the partner's patients
  per_enrollment  rate x patients enrolled this month; minus rate for any of their patients
                  refunded this month within 90 days of enrollment (clawback)
  flat_monthly    rate, flat, if the partner had an active agreement this month

No partner gets paid without a W-9 on file. Their amount is held, not dropped.

    python3 scripts/comp_statement.py referrals.csv payments.csv --month 2026-11 \\
        --structure pct_collected --rate 0.10 --partners partners.csv --out statements/
"""

import argparse
import csv
import datetime as dt
import os
from collections import defaultdict

CLAWBACK_DAYS = 90
# Labels as they appear in the GHL contact.comp_structure dropdown.
STRUCTURE_LABELS = {
    "flat monthly marketing fee": "flat_monthly",
    "per enrollment": "per_enrollment",
    "percent of collected": "pct_collected",
    "none (relationship only)": "none",
    "pending counsel review": "none",
}


def parse_date(s):
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S", "%b %d %Y"):
        try:
            return dt.datetime.strptime(s[:19] if "T" in s else s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date: {s!r}")


def in_month(d, month):
    return d is not None and d.strftime("%Y-%m") == month


def display_name(full, fmt):
    if fmt == "full" or not full:
        return full
    parts = full.split()
    return parts[0] + (f" {parts[-1][0]}." if len(parts) > 1 else "")


def compute(referrals, payments, month, default_structure, default_rate, partners=None):
    partners = partners or {}
    pay_by_contact = defaultdict(list)
    for p in payments:
        pay_by_contact[p["contact_id"]].append((parse_date(p["date"]), float(p["amount"])))

    by_partner = defaultdict(list)
    for r in referrals:
        pid = (r.get("referral_partner_id") or "").strip().upper()
        if pid:
            by_partner[pid].append(r)

    statements = {}
    for pid in sorted(set(by_partner) | set(partners)):
        cfg = partners.get(pid, {})
        raw = (cfg.get("comp_structure") or "").strip()
        structure = STRUCTURE_LABELS.get(raw.lower(), raw) or default_structure
        rate = float(cfg.get("comp_rate") or default_rate)
        lines, total = [], 0.0
        for r in by_partner.get(pid, []):
            enrolled = parse_date(r.get("enrollment_date"))
            pays = [(d, a) for d, a in pay_by_contact.get(r["contact_id"], []) if in_month(d, month)]
            collected = sum(a for _, a in pays if a > 0)
            refunded = sum(a for _, a in pays if a < 0)
            comp = 0.0
            if structure == "pct_collected":
                comp = rate * (collected + refunded)
            elif structure == "per_enrollment":
                if in_month(enrolled, month):
                    comp += rate
                if refunded and enrolled and any(
                        a < 0 and (d - enrolled).days <= CLAWBACK_DAYS for d, a in pays):
                    comp -= rate
            total += comp
            lines.append({
                "patient": r.get("patient_name", ""), "referral_date": r.get("referral_date", ""),
                "stage": r.get("stage", ""), "enrollment_date": r.get("enrollment_date", ""),
                "collected": collected, "refunded": refunded, "comp": comp,
            })
        if structure == "flat_monthly":
            total = rate
        elif structure == "none":
            total = 0.0
        w9 = str(cfg.get("w9_on_file", "")).strip().lower() in ("yes", "true", "1")
        statements[pid] = {
            "partner_name": cfg.get("partner_name", pid), "structure": structure, "rate": rate,
            "lines": lines, "total": round(total, 2),
            "status": "payable" if w9 else "held: no W-9 on file",
        }
    return statements


def render(pid, st, month, name_fmt):
    out = [f"# Referral statement: {st['partner_name']} ({pid})", f"Period: {month}",
           f"Structure: {st['structure']} @ {st['rate']}", "",
           "| Patient | Referred | Stage | Enrolled | Collected | Refunds | Comp |",
           "|---|---|---|---|---:|---:|---:|"]
    for ln in sorted(st["lines"], key=lambda x: x["referral_date"]):
        out.append(f"| {display_name(ln['patient'], name_fmt)} | {ln['referral_date']} | {ln['stage']} | "
                   f"{ln['enrollment_date'] or '—'} | ${ln['collected']:,.2f} | ${ln['refunded']:,.2f} | "
                   f"${ln['comp']:,.2f} |")
    out += ["", f"**Total due: ${st['total']:,.2f}** ({st['status']})", "",
            "Every patient you referred is listed, including ones who didn't enroll or didn't get a result. "
            "Compensation is based on collected revenue only, net of refunds and chargebacks."]
    return "\n".join(out) + "\n"


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("referrals")
    ap.add_argument("payments")
    ap.add_argument("--month", required=True, help="YYYY-MM")
    ap.add_argument("--structure", choices=["pct_collected", "per_enrollment", "flat_monthly"], required=True)
    ap.add_argument("--rate", type=float, required=True)
    ap.add_argument("--partners")
    ap.add_argument("--names", choices=["initial", "full"], default="initial",
                    help="'full' only if client agreements authorize sharing names with partners")
    ap.add_argument("--out", default="statements")
    a = ap.parse_args()

    partners = {p["partner_id"].strip().upper(): p for p in read_csv(a.partners)} if a.partners else {}
    sts = compute(read_csv(a.referrals), read_csv(a.payments), a.month, a.structure, a.rate, partners)
    os.makedirs(a.out, exist_ok=True)
    for pid, st in sts.items():
        with open(os.path.join(a.out, f"{a.month}-{pid}.md"), "w") as f:
            f.write(render(pid, st, a.month, a.names))
        print(f"{pid:18} {st['structure']:15} ${st['total']:>10,.2f}  {st['status']}")


if __name__ == "__main__":
    main()
