# Live account audit: what's already in GHL

Read-only pull of sub-account `Evfk5CgjxNHryw79uGDD` on 2026-09-24, followed the same day by the fixes in the next section.

## Applied on 2026-09-24

| Fix | Status |
|---|---|
| 38 typed custom fields created (DATE / NUMERICAL / MONETORY / dropdowns), keys match `config/ghl-schema.json` | ✅ Done, verified by re-reading the live field list |
| 11 TEXT or typo'd fields replaced and renamed `OLD - …`. Keys unchanged; nothing deleted. | ✅ Done. Delete them in Settings → Custom Fields once you've confirmed nothing uses them. |
| Tag `dormat-partner` renamed to `dormant-partner`; contacts carrying it keep it | ✅ Done |
| Duplicate tag `linkedln` deleted (0 contacts had it) | ✅ Done |
| 14 lifecycle and attribution tags created | ✅ Done |
| Calendar **Patient Credit Consult**: round robin, Clifford (Twin); Mon–Fri 10–8, Sat 9–2; 30 min + 15 min buffer; 2-hour minimum notice | ✅ Done: `https://api.leadconnectorhq.com/widget/booking/xjCUn38pxxI23KIDhTok` |
| Custom values `consult_booking_link` and `consent_language_version` (`v2026-10-a`) | ✅ Done |
| Email templates: B2 speed-to-lead, P3 partner kit, P5 dormant day 7, R1 monthly update | ✅ Done (not attached to any workflow yet, so nothing sends) |
| Assign the 148 partner prospects to Kate | ⏸ Skipped for now: Kate isn't a GHL user yet |
| Partner Intro Call and Partner Training calendars | ⏸ Skipped for now: owner is Kate |
| Forms, workflows, Documents & Contracts templates | ❌ GHL's public API can't create these. Build them in the UI from docs 02–09. |
| Delete the 6 snapshot draft workflows | Left alone. They're drafts, so they never fire. |

## Original findings

## What's already right

- **Partner Pipeline** has all 8 stages in the right order: Prospect → Connected → Conversation → Intro Call Booked → Agreement Sent → Signed and Trained → Producing → Dormant.
- **Patient Pipeline** has New Referral → Contacted → Consult Booked → Consult Attended → Enrolled → Nurture → Improved and Ready to Reapply → Closed with No Result.
- **Attribution fields** exist on the opportunity: referral partner ID, rep, office, date, method, declined lender, decline reason, treatment amount, and target score.
- **Consent and fulfillment fields** exist on the contact: SMS and call permission, consent timestamp, Dispute Fox client ID, dispute round, items removed, current score.
- **Tags** cover the lifecycle: `partner-prospect`, `signed-partner`, `producing-partner`, `manual-rep-submit`, `enrolled-client`, and others.
- **148 partner prospects** are loaded. All are SC dental offices from web research (`sc-dental-batch2-2026-09`), and all sit at Prospect.

## What will break if it isn't fixed before the first partner signs

| # | Problem | Why it matters | Fix |
|---|---|---|---|
| 1 | **Every custom field is TEXT.** That includes dates (`date_signed`, `last_referral_date`, `referrral_date`), counts (`total_referrals`, `item_removed`), and money (`treatment_amount`). | GHL can't do "last referral more than 30 days ago", "treatment over $15k", or sum referrals on TEXT. Your dormancy trigger, your $-based routing, and half the scorecard depend on those. | `scripts/provision_fields.py` creates typed replacements (DATE, NUMERICAL, MONETARY). The Patient Pipeline is empty and no partner has signed, so there's nothing to migrate yet. This is the cheapest this fix will ever be. Delete the old TEXT fields once nothing references them. |
| 2 | **All 148 partner opportunities are unassigned.** | Tasks, round-robin and "assigned user" notifications all resolve to nobody. Kate's pipeline view filtered to "mine" shows 0. | Bulk-assign to Kate in Opportunities → select all → Assign. |
| 3 | **Typo'd field keys** `opportunity.referrral_date`, `opportunity.traget_credit_score`, and `contact.api_address` (meant: IP address). | Keys are permanent. Merge tags such as `{{opportunity.referrral_date}}` must be spelled wrong forever, or someone "fixes" them and breaks the workflow silently. | Rename the **display names** in the UI. `config/ghl-schema.json` documents the real keys, so nobody has to guess. |
| 4 | **Typo'd tag** `dormat-partner`, and a duplicate `linkedln` next to `linkedin-lead`. | A workflow triggered on `dormant-partner` never fires, because the tag being applied is `dormat-partner`. Nobody notices for months. | Create `dormant-partner`, retag, and delete the typo. |
| 5 | **Attribution fields live only on the opportunity.** GHL forms write **contact** fields. | The `?ref=` link can't land directly on an opportunity field, so your core attribution can't be captured the way it's built now. | Capture on the contact (`contact.ref_capture`, hidden, query key `ref`), then copy to the opportunity in the intake workflow. See `03-attribution-kit.md`. |
| 6 | **No partner-type or parent-rep field.** | With 300 reps each bringing offices, "which rep's network is producing" is the question that decides where Kate spends her week. Without `parent_rep_id`, you can't answer it. | Created by the provision script. |
| 7 | **All 6 workflows are snapshot drafts** ("Claim Offer", "New Sale - Send Review Request"). | They weren't written for this business. A review request fired at a credit-repair client on day 1 is a reputational own-goal. | Leave them off. Build the workflows in `05`–`09` fresh. |
| 8 | **No consult calendar.** Only "Schedule an Appointment" (Mon–Fri, 8–5) and two personal calendars exist. | Patients declined in the chair work day jobs, so a weekday 8–5 calendar produces no-shows. | Create the 3 calendars listed in `ghl-schema.json`. |
| 9 | **One form exists: the snapshot "Claim Offer" form.** | There's no patient intake form, rep-submit form, or consent-confirm form. | Build the forms in `04-intake-and-consent.md`. |

## About the 148 cold prospects

These are **not** the rep's 112 offices. They're a cold list, 74 of them phone-only. Two cautions:

1. **Don't put them in an automated SMS sequence.** A business listing's phone number is often a front-desk cell or a VoIP line forwarded to the dentist's mobile. Automated texts to a number that never opted in are a TCPA problem even when the recipient is a business. Call them, email the 26 that have email, or have the rep make the warm intro.
2. **The rep's warm offices will convert at several times the rate of this list.** Pilot on the warm ones. Work the cold list in parallel to learn the objections, not to hit numbers.
