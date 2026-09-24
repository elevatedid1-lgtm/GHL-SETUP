"""Referral-network projections: conservative / realistic / aggressive.

Every number below is an ASSUMPTION, not data. The point of the pilot is to replace
these with measured rates from the Patient Pipeline, then re-run this script.
Potential exposure (112 offices, 300+ reps) is NOT revenue.

    python3 scripts/projections.py > docs/11-projections.md
"""

SCENARIOS = ("conservative", "realistic", "aggressive")

# fmt: off
A = {
    # Partner side
    "sign_rate":            (0.25, 0.40, 0.60),  # offices pitched that sign an agreement
    "active_rate":          (0.30, 0.45, 0.60),  # signed offices sending >=1 referral in a month
    "referrals_per_active": (1.5,  3.0,  6.0),   # referrals / active office / month
    # Patient funnel
    "contact_rate":         (0.70, 0.80, 0.90),  # reached by phone/SMS within 8 days
    "book_rate":            (0.35, 0.50, 0.60),  # of contacted, booked a consult
    "show_rate":            (0.55, 0.65, 0.75),  # of booked, attended
    "enroll_rate":          (0.25, 0.35, 0.45),  # of attended, signed + passed 3-day window
    # Money
    "program_fee":          (1500, 1500, 1500),  # contracted, billed after services performed
    "realization":          (0.65, 0.75, 0.85),  # share of contracted fee actually collected
    "processing_pct":       (0.050, 0.045, 0.040),  # high-risk merchant account, all-in
    "comp_pct_collected":   (0.10, 0.10, 0.10),  # PLACEHOLDER until counsel picks a structure
    "fulfillment_cost":     (350, 300, 260),     # per enrolled client, lifetime: DF seat share, letters, Hammock, IDIQ if absorbed
    "service_months":       (6, 6, 6),           # avg months a client stays active
    # Capacity (per full-time person)
    "leads_per_coord_day":  (25, 30, 35),        # speed-to-lead coordinator: new leads worked/day
    "consults_per_closer_wk": (20, 25, 30),
    "active_per_cs":        (200, 250, 300),     # client-success rep: active files kept warm
    "partners_per_pm":      (60, 75, 90),        # partner manager: signed partners actively coached
    "loaded_cost_per_fte_mo": (4500, 4500, 4500),
}
# fmt: on

PHASES = [
    ("Pilot (90 days)", "10 hand-picked offices from the rep's 112", lambda s: 10),
    ("Phase 2", "All 112 offices from the first rep pitched", lambda s: 112),
    ("Phase 3", "Network: reps who actually engage x offices each",
     lambda s: int(300 * (0.05, 0.10, 0.20)[s] * (10, 15, 25)[s])),
]
PHASE3_NOTE = ("Phase 3 assumes 5% / 10% / 20% of the 300 reps engage and each brings 10 / 15 / 25 offices. "
               "That's 150 / 450 / 1,500 offices pitched. The spread is huge because nobody has measured it yet.")


def model(offices_pitched, s):
    g = {k: v[s] for k, v in A.items()}
    signed = offices_pitched * g["sign_rate"]
    active = signed * g["active_rate"]
    leads = active * g["referrals_per_active"]
    contacted = leads * g["contact_rate"]
    booked = contacted * g["book_rate"]
    attended = booked * g["show_rate"]
    enrolled = attended * g["enroll_rate"]
    collected = enrolled * g["program_fee"] * g["realization"]  # steady-state monthly
    comp = collected * g["comp_pct_collected"]
    processing = collected * g["processing_pct"]
    fulfillment = enrolled * g["fulfillment_cost"]
    active_clients = enrolled * g["service_months"]
    fte = {
        "Speed-to-lead coordinators": leads / (g["leads_per_coord_day"] * 21.7),
        "Consult closers": booked / (g["consults_per_closer_wk"] * 4.33),
        "Client-success reps": active_clients / g["active_per_cs"],
        "Partner managers": signed / g["partners_per_pm"],
    }
    staff_cost = sum(max(v, 0.25) for v in fte.values()) * g["loaded_cost_per_fte_mo"]
    margin = collected - comp - processing - fulfillment - staff_cost
    return {
        "Offices pitched": offices_pitched, "Offices signed": signed, "Active offices / mo": active,
        "Leads / mo": leads, "Contacted": contacted, "Consults booked": booked, "Consults attended": attended,
        "Enrollments / mo": enrolled, "Active clients (steady state)": active_clients,
        "Collected / mo": collected, "Referral comp / mo": comp, "Processing / mo": processing,
        "Fulfillment / mo": fulfillment,
        "Contribution before staff / mo": collected - comp - processing - fulfillment,
        "Staff cost / mo": staff_cost, "Contribution / mo": margin,
        "Contribution margin": margin / collected if collected >= staff_cost else None,
        "Support contacts / mo (1.5 per active client)": active_clients * 1.5,
        **{f"FTE: {k}": v for k, v in fte.items()},
    }


def fmt(k, v):
    if "margin" in k:
        return "n/m (below staff cost)" if v is None else f"{v:.0%}"
    if any(w in k for w in ("Collected", "comp", "Processing", "Fulfillment", "cost", "Contribution")):
        return f"${v:,.0f}"
    if k.startswith("FTE"):
        return f"{v:.1f}"
    return f"{v:,.0f}" if v >= 10 else f"{v:,.1f}"


def main():
    out = ["# Projections: conservative, realistic, aggressive", "",
           "_Generated by `scripts/projections.py`. Every input is an assumption, listed at the bottom. "
           "Monthly figures are **steady state**, reached about 6 months after a phase starts, because "
           "fees are billed after services are performed and collections trail enrollments. "
           "The real rates come from pilot data._", "",
           "> **Billing-timing caveat:** these tables assume monthly-after-service billing. If counsel finds the "
           "Telemarketing Sales Rule applies (doc 12, B2), collections move out by 6+ months and cash needs "
           "change sharply, even if the steady-state numbers look similar.", ""]
    for name, desc, n in PHASES:
        rows = [model(n(i), i) for i in range(3)]
        out += [f"## {name}", "", f"_{desc}._", ""]
        if name == "Phase 3":
            out += [f"> {PHASE3_NOTE}", ""]
        out += ["| Metric | Conservative | Realistic | Aggressive |", "|---|---:|---:|---:|"]
        for k in rows[0]:
            out.append(f"| {k} | " + " | ".join(fmt(k, r[k]) for r in rows) + " |")
        out.append("")
    out += ["## Assumptions", "", "| Input | Conservative | Realistic | Aggressive |", "|---|---:|---:|---:|"]
    for k, v in A.items():
        out.append(f"| `{k}` | " + " | ".join(str(x) for x in v) + " |")
    out += ["", "FTE below 0.25 is costed at 0.25, because someone still owns that job part time. In the pilot, "
            "that minimum is the existing team's time (Kate, Rebecca, Twin), not new hires. "
            "Read *Contribution before staff* to see whether the unit economics work at all.", ""]
    print("\n".join(out))


if __name__ == "__main__":
    main()
