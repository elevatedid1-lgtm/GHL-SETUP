# 04 — Intake: the patient record that makes reporting possible

**Pipeline B · Owner: system**

## Fields set at creation and never left blank

Real keys and IDs are in `config/ghl-schema.json`. All of these exist in GHL as of 2026-09-24. Fields named `OLD - …` in GHL are retired: don't map forms or workflows to them.

| Spec name | GHL key | Set by |
|---|---|---|
| referral_partner_id | `contact.ref_first_touch` → `opportunity.referral_partner_id` | Workflow `B1` (first touch) |
| referral_office | `opportunity.referral_office` | `B1`, looked up from the partner |
| referral_rep | `opportunity.referral_representative` | `B1`, from the `parent_rep_id` prefix |
| referral_date | `opportunity.referral_date` (DATE) | `B1` = submission date |
| referral method | `opportunity.referral_method` | `link` / `qr` / `sms_keyword` / `office_dropdown` / `manual_rep_submit` |
| decline_lender | `contact.decline_lender_patient` → `opportunity.declined_lender` | Patient, on the form |
| decline_reason | `opportunity.decline_reason` | Patient ("I don't know" is allowed) |
| treatment_amount | `contact.treatment_amount_patient` → opportunity **Monetary Value** | Patient |
| target_score | `contact.target_credit_score` → `opportunity.target_score` (both NUMERICAL) | Consult (the patient rarely knows it) |
| patient state | `contact.patient_state` | Patient, on the form. **Required.** |
| consent_sms / consent_call | `contact.sms_permission_status`, `contact.call_permission_status` | Form checkbox |
| consent_timestamp | `contact.consent_datetime` | Workflow = submission timestamp |
| consent_ip | `contact.consent_ip` | Form hidden IP field (GHL records the submission IP; copy it) |
| consent language version | `contact.consent_language_version` | Hidden field, set from custom value `{{custom_values.consent_language_version}}` (currently `v2026-10-a`) |

**Put treatment amount in the opportunity's Monetary Value,** not only in a custom field. Pipeline value totals, the funnel report, and the opportunity card sort all run on Monetary Value, so you get "$ of declined treatment in the pipeline" for free. That number sells the next 300 reps.

Why it matters operationally: a $4,200 aligner case and a $38,000 full-arch case are different conversations. Routing rule in `B1`: Monetary Value ≥ $15,000 → tag `priority-a`, assign to Twin, and create the call task at 2 minutes instead of 5.

## Forms to build

### Form 1: `Patient Intake` (public, on `/start`)
Fields: first name, last name, mobile, email, state, who declined you (dropdown), roughly how much was the treatment plan, what were you hoping to get done (short text), office dropdown (fallback), and hidden `ref_capture`, `ref_method_capture`, `consent_language_version`.

Consent block, **as two separate, unchecked checkboxes** (never pre-checked, and never a condition of service):

> ☐ I agree Elevated ID may text me at the number above about my inquiry, including automated messages. Msg & data rates may apply; frequency varies. Reply STOP to opt out, HELP for help. Consent is not required to receive services.
>
> ☐ I agree Elevated ID may call me at the number above, including with automated technology, about my inquiry.

Have counsel approve the exact wording once. Then **freeze it and version it** (`v2026-10-a`). When a TCPA claim arrives 14 months later, the question is "what exact words did this person see on this date," and `consent_language_version` plus the timestamp and IP is the answer.

Keep the form short. Every field past 7 costs completions, and this person was embarrassed at a front desk an hour ago. Things you can learn on the phone (target score, decline reason detail) don't belong on the form.

### Form 2: `Rep Submit`
See doc 03. Tags `manual-rep-submit` and `consent-pending`.

### Form 3: `Confirm Your Info` (consent capture for rep-submitted patients)
The same consent block and fields, pre-filled from the contact. Sent **manually** by a human after a live conversation, as a one-to-one text from the Conversations tab ("Here's the link we just talked about"), never from an automated sequence.

## Consent has to come from the patient

A rep handing you a phone number is **not** consent to text or auto-dial that number. Rules built into the workflows:

1. `manual-rep-submit` contacts **don't enter** `B2` (the automated speed-to-lead sequence). They get a **call task** at 5 minutes. The call is placed by hand, not with a power dialer.
2. `consent_confirmed_by_patient` is set only when **the patient** submits Form 1 or Form 3.
3. Every automated SMS or call step in every workflow checks: `sms_permission_status = granted AND consent_confirmed_by_patient = Yes`. Put the check in the step itself, not only at the top of the workflow. People reuse workflows.
4. STOP is honored across every number and every workflow. GHL's DND does this per channel. Check that DND-SMS is set when STOP comes in, before launch.
5. Many states have their own texting laws stricter than federal (Florida, Oklahoma, Maryland and others). Consent from the patient's own submission is what covers you everywhere.

## The one that gets overlooked: HIPAA on the office side

The dental office is a HIPAA covered entity. "Maria Lopez, 555-0142, declined by CareCredit for a $22k implant case" is **protected health information**. If the office sends it to you without Maria's written authorization, the office has a problem, and so does your relationship with it.

The design above avoids it:
- **The patient** gives you her treatment amount and decline details. She can share her own information with anyone.
- Office staff hand a card, and the patient acts.
- The rep-submit form collects **name, phone, best time**, and a confirmation that the patient asked for it. No treatment details, no lender, no amount.

Tell partners this in training in one sentence: "Don't send us anything about the patient. Hand them the card and we'll ask them ourselves." Offices relax when they hear you've thought about it. It reads as competence.

## Workflow `B1 · Intake → opportunity`

- **Triggers:** Form submitted = Patient Intake; Form submitted = Confirm Your Info; Form submitted = Rep Submit.
- Set the consent fields (timestamp = now, IP, version). If the form is Intake or Confirm, set `consent_confirmed_by_patient = Yes`.
- First-touch attribution: if `ref_first_touch` is empty and `ref_capture` isn't empty, copy it. If `ref_capture` is empty and the office dropdown is set, copy the dropdown's partner ID and set method = `office_dropdown`. If there's a conflict → `attribution-conflict` tag and a task.
- **Create/Update Opportunity** in the Patient Pipeline, stage New Referral, Monetary Value = treatment amount. Copy the attribution fields onto the opportunity.
- If `ref_first_touch` isn't empty → **Webhook** POST to the sync service: `{"patient_contact_id": "{{contact.id}}", "partner_id": "{{contact.ref_first_touch}}"}`. That moves the partner to Producing and resets their dormancy timer.
- If `ref_first_touch` is still empty and the method isn't organic → tag `attribution-missing` and a task for Kate.
- Branch: `manual-rep-submit` → call task only. Else → add to `B2`.

Most CRM setups get attribution-missing wrong: a missing ID should be **a task for a human**, never a silent "organic." Every attribution-missing Kate resolves within 24 hours is a rep argument that never happens.
