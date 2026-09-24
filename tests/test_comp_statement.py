import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.comp_statement import compute, display_name, render  # noqa: E402

REFERRALS = [
    {"contact_id": "c1", "patient_name": "Maria Lopez", "referral_partner_id": "clrch-den-014",
     "referral_date": "2026-10-02", "stage": "Enrolled", "enrollment_date": "2026-11-03"},
    {"contact_id": "c2", "patient_name": "Dan Reed", "referral_partner_id": "CLRCH-DEN-014",
     "referral_date": "2026-10-05", "stage": "Closed with No Result", "enrollment_date": ""},
    {"contact_id": "c3", "patient_name": "Ana Cruz", "referral_partner_id": "CLRCH-DEN-015",
     "referral_date": "2026-09-01", "stage": "Enrolled", "enrollment_date": "2026-09-10"},
]
PAYMENTS = [
    {"contact_id": "c1", "date": "2026-11-20", "amount": "250"},
    {"contact_id": "c3", "date": "2026-11-12", "amount": "250"},
    {"contact_id": "c3", "date": "2026-11-25", "amount": "-250"},
    {"contact_id": "c3", "date": "2026-10-12", "amount": "250"},  # other month, ignored
]


class CompTests(unittest.TestCase):
    def test_pct_collected_nets_refunds(self):
        s = compute(REFERRALS, PAYMENTS, "2026-11", "pct_collected", 0.10)
        self.assertEqual(s["CLRCH-DEN-014"]["total"], 25.0)
        self.assertEqual(s["CLRCH-DEN-015"]["total"], 0.0)

    def test_every_referral_listed_even_without_revenue(self):
        s = compute(REFERRALS, PAYMENTS, "2026-11", "pct_collected", 0.10)
        self.assertEqual(len(s["CLRCH-DEN-014"]["lines"]), 2)

    def test_per_enrollment_with_clawback(self):
        s = compute(REFERRALS, PAYMENTS, "2026-11", "per_enrollment", 150)
        self.assertEqual(s["CLRCH-DEN-014"]["total"], 150.0)
        self.assertEqual(s["CLRCH-DEN-015"]["total"], -150.0)  # refunded within 90 days

    def test_partner_override_makes_structure_a_setting(self):
        partners = {"CLRCH-DEN-015": {"partner_id": "CLRCH-DEN-015", "comp_structure": "Flat Monthly Marketing Fee",
                                      "comp_rate": "500", "w9_on_file": "Yes"}}
        s = compute(REFERRALS, PAYMENTS, "2026-11", "pct_collected", 0.10, partners)
        self.assertEqual(s["CLRCH-DEN-015"]["total"], 500.0)
        self.assertEqual(s["CLRCH-DEN-015"]["status"], "payable")

    def test_pending_counsel_pays_nothing(self):
        partners = {"CLRCH-DEN-014": {"partner_id": "CLRCH-DEN-014", "comp_structure": "Pending Counsel Review",
                                      "comp_rate": "", "w9_on_file": "Yes"}}
        s = compute(REFERRALS, PAYMENTS, "2026-11", "pct_collected", 0.10, partners)
        self.assertEqual(s["CLRCH-DEN-014"]["total"], 0.0)

    def test_no_w9_holds_payment(self):
        s = compute(REFERRALS, PAYMENTS, "2026-11", "pct_collected", 0.10)
        self.assertTrue(s["CLRCH-DEN-014"]["status"].startswith("held"))

    def test_names_initialed_by_default(self):
        self.assertEqual(display_name("Maria Lopez Garcia", "initial"), "Maria G.")
        s = compute(REFERRALS, PAYMENTS, "2026-11", "pct_collected", 0.10)
        self.assertNotIn("Lopez", render("CLRCH-DEN-014", s["CLRCH-DEN-014"], "2026-11", "initial"))


if __name__ == "__main__":
    unittest.main()
