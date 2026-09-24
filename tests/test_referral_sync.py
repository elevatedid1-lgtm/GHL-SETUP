import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.provision_fields import key_from_name, missing_fields  # noqa: E402
from service.referral_sync import load_schema, plan  # noqa: E402

SCHEMA = load_schema()
STAGES = {v: k for k, v in SCHEMA["pipelines"]["partner"]["stages"].items()}
S = SCHEMA["pipelines"]["partner"]["stages"]
TODAY = dt.date(2026, 10, 1)
PARTNER = [{"id": "p1"}]


def opp(stage, status="open"):
    return {"id": "o1", "pipelineStageId": S[stage], "status": status}


class PlanTests(unittest.TestCase):
    def test_unknown_id_is_flagged_not_dropped(self):
        a = plan([], [], [], {}, STAGES, TODAY)
        self.assertEqual(a["patient_tags"], ["attribution-missing"])

    def test_duplicate_partner_id_is_a_conflict(self):
        a = plan([{"id": "a"}, {"id": "b"}], [], [], {}, STAGES, TODAY)
        self.assertEqual(a["patient_tags"], ["attribution-conflict"])

    def test_first_referral_moves_trained_partner_to_producing(self):
        a = plan(PARTNER, [opp("signed_and_trained")], [], {}, STAGES, TODAY)
        self.assertEqual(a["move"], "o1")
        self.assertEqual(a["partner_fields"]["contact.partner_referral_count"], 1)
        self.assertEqual(a["partner_fields"]["contact.partner_last_referral_date"], "2026-10-01")
        self.assertIn("referral-received", a["partner_tags"])

    def test_dormant_partner_is_revived(self):
        a = plan(PARTNER, [opp("dormant")], [], {"contact.partner_referral_count": "4"}, STAGES, TODAY)
        self.assertEqual(a["move"], "o1")
        self.assertEqual(a["partner_fields"]["contact.partner_referral_count"], 5)

    def test_producing_partner_stays_put(self):
        a = plan(PARTNER, [opp("producing")], [], {}, STAGES, TODAY)
        self.assertIsNone(a["move"])

    def test_unsigned_partner_counted_but_flagged(self):
        a = plan(PARTNER, [opp("conversation")], [], {}, STAGES, TODAY)
        self.assertIsNone(a["move"])
        self.assertIn("referral-before-signing", a["partner_tags"])

    def test_webhook_retry_does_not_double_count(self):
        a = plan(PARTNER, [opp("producing")], ["referral-counted"], {}, STAGES, TODAY)
        self.assertEqual(a["partner_fields"], {})
        self.assertIsNone(a["move"])

    def test_ambiguous_partner_opportunities_go_to_review(self):
        a = plan(PARTNER, [], [], {}, STAGES, TODAY)
        self.assertIn("partner-opportunity-review", a["partner_tags"])

    def test_garbage_count_does_not_crash(self):
        a = plan(PARTNER, [opp("producing")], [], {"contact.partner_referral_count": "n/a"}, STAGES, TODAY)
        self.assertEqual(a["partner_fields"]["contact.partner_referral_count"], 1)


class SchemaTests(unittest.TestCase):
    def test_every_new_field_key_matches_what_ghl_will_generate(self):
        for f in SCHEMA["customFields"]:
            if f["status"] == "create":
                self.assertEqual(key_from_name(f["model"], f["name"]), f["key"], f["name"])

    def test_missing_fields_skips_existing(self):
        live = [{"fieldKey": f["key"]} for f in SCHEMA["customFields"]]
        self.assertEqual(missing_fields(SCHEMA, live), [])

    def test_keys_unique(self):
        keys = [f["key"] for f in SCHEMA["customFields"]]
        self.assertEqual(len(keys), len(set(keys)))


if __name__ == "__main__":
    unittest.main()
