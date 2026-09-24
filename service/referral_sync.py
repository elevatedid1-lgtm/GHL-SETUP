"""Patient referral -> partner record sync.

Why this exists: a GHL workflow runs on ONE contact. When a patient submits with
ref=CLRCH-DEN-014, the patient workflow cannot look up the partner contact that
owns CLRCH-DEN-014 and move that partner's opportunity to Producing. This
service is the bridge. The patient workflow's Webhook action POSTs here:

    {"patient_contact_id": "{{contact.id}}", "partner_id": "{{contact.ref_first_touch}}"}

It then, on the PARTNER record:
  * bumps the referral count and last-referral date,
  * adds the `referral-received` tag (the partner-side GHL workflow keys on it
    to reset the 30-day dormancy timer and send the "we got her" note),
  * moves the partner opportunity to Producing if it was Signed & Trained or Dormant.

Everything the team needs to see or change stays in GHL workflows. This only
does the cross-record lookup GHL can't.
"""

import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service.ghl import GHL  # noqa: E402

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "ghl-schema.json")

COUNTED_TAG = "referral-counted"
PRODUCING_FROM = {"signed_and_trained", "dormant"}
UNSIGNED_STAGES = {"prospect", "connected", "conversation", "intro_call_booked", "agreement_sent"}


def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)


def plan(partner_matches, partner_opps, patient_tags, partner_fields, stage_names, today):
    """Decide what to do. Pure function so it can be tested without the API.

    partner_matches: contacts whose partner_id equals the submitted ref
    partner_opps:    that partner's opportunities in the Partner Pipeline
    patient_tags:    tags currently on the patient contact
    partner_fields:  {field_key: current value} for the partner contact
    stage_names:     {stage_id: stage_key} for the Partner Pipeline
    """
    if not partner_matches:
        return {"patient_tags": ["attribution-missing"], "reason": "no partner owns this ID"}
    if len(partner_matches) > 1:
        return {"patient_tags": ["attribution-conflict"], "reason": "partner ID is not unique"}

    actions = {"partner_contact_id": partner_matches[0]["id"], "partner_fields": {}, "partner_tags": [],
               "patient_tags": [], "move": None}

    if COUNTED_TAG in patient_tags:
        actions["reason"] = "already counted (webhook retry)"
        return actions

    try:
        count = int(float(partner_fields.get("contact.partner_referral_count") or 0))
    except ValueError:
        count = 0
    actions["partner_fields"] = {
        "contact.partner_referral_count": count + 1,
        "contact.partner_last_referral_date": today.isoformat(),
    }
    actions["partner_tags"] = ["referral-received"]
    actions["patient_tags"] = [COUNTED_TAG]

    open_opps = [o for o in partner_opps if o.get("status") == "open"]
    if len(open_opps) == 1:
        stage = stage_names.get(open_opps[0]["pipelineStageId"])
        if stage in PRODUCING_FROM:
            actions["move"] = open_opps[0]["id"]
        elif stage in UNSIGNED_STAGES:
            # Referral arrived before the agreement is signed. Count it, never pay on it
            # until counsel-approved paper exists, and tell Kate the partner is warm.
            actions["partner_tags"].append("referral-before-signing")
    else:
        actions["partner_tags"].append("partner-opportunity-review")
    return actions


def run(patient_contact_id, partner_id, client=None, today=None):
    schema = load_schema()
    client = client or GHL()
    today = today or dt.date.today()
    partner_pipeline = schema["pipelines"]["partner"]
    stage_names = {v: k for k, v in partner_pipeline["stages"].items()}

    fields = {f["fieldKey"]: f["id"] for f in client.list_custom_fields()}
    partner_id_field = fields["contact.partner_id"]
    partner_id = (partner_id or "").strip().upper()

    patient = client.get_contact(patient_contact_id)
    matches = client.search_contacts_by_field(partner_id_field, partner_id) if partner_id else []

    partner_fields, opps = {}, []
    if len(matches) == 1:
        partner = client.get_contact(matches[0]["id"])
        by_id = {v: k for k, v in fields.items()}
        partner_fields = {by_id.get(cf["id"]): cf.get("value") for cf in partner.get("customFields", [])}
        opps = client.find_opportunities(partner["id"], partner_pipeline["id"])

    actions = plan(matches, opps, patient.get("tags", []), partner_fields, stage_names, today)

    if actions.get("partner_fields") or actions.get("partner_tags"):
        missing = [k for k in actions.get("partner_fields", {}) if k not in fields]
        if missing:
            raise RuntimeError(f"Custom fields not provisioned: {missing}. Run scripts/provision_fields.py.")
        client.update_contact(
            actions["partner_contact_id"],
            custom_fields={fields[k]: v for k, v in actions.get("partner_fields", {}).items()},
            tags=actions.get("partner_tags"),
        )
    if actions.get("move"):
        client.move_opportunity(actions["move"], partner_pipeline["stages"]["producing"])
    if actions.get("patient_tags"):
        client.update_contact(patient_contact_id, tags=actions["patient_tags"])
    return actions


def handler(event, context=None):
    """AWS Lambda / generic serverless entry point."""
    body = event.get("body", event)
    if isinstance(body, str):
        body = json.loads(body)
    result = run(body["patient_contact_id"], body.get("partner_id"))
    return {"statusCode": 200, "body": json.dumps(result)}


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("patient_contact_id")
    ap.add_argument("partner_id")
    ap.add_argument("--dry-run", action="store_true", help="read live data, print writes instead of sending them")
    a = ap.parse_args()
    print(json.dumps(run(a.patient_contact_id, a.partner_id, client=GHL(dry_run=a.dry_run)), indent=2))
