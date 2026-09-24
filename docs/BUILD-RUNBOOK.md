# Build runbook: manual GHL builds (for a Claude in Chrome session)

The API work is done (see `docs/00-live-account-audit.md`). This runbook covers what GHL's API can't create: **forms, the funnel page, workflows, and Documents & Contracts templates**. It's written so a browser session can execute it step by step.

**Account:** Elevated Identities LLC · sub-account `Evfk5CgjxNHryw79uGDD` · app.gohighlevel.com (or your white-label domain)
**Source of truth for every ID:** `config/ghl-schema.json`

## Rules for the session doing the build

1. **Build everything as Draft.** Don't publish any workflow. A person reviews and publishes.
2. **Don't delete anything,** including the 6 snapshot draft workflows and the `OLD - …` fields. Those are for a human to decide.
3. **Never** send a test SMS or email to a real contact. Use a test contact named `ZZ Test Patient`, with the owner's own phone and email.
4. Before clicking any **Delete**, **Publish** or **Send**, stop and ask.
5. After each item, tick it here and note what was actually built if it differs.
6. **Order matters.** Forms come before workflows, because the workflow triggers reference the forms.

---

## Phase 0: settings (5 min)

- [ ] **Settings → Custom Fields → Ref Capture** → edit → **Query Key = `ref`** → save
- [ ] **Settings → Custom Fields → Ref Method Capture** → **Query Key = `src`** → save
- [ ] **Settings → Business Profile:** confirm the time zone is **America/New_York**
- [ ] **Calendars → Patient Credit Consult → Availability:** confirm the hours read Mon–Fri 10:00–20:00 and Sat 09:00–14:00 **Eastern**

## Phase 1: forms (Sites → Forms → Builder)

### Form 1: `Patient Intake`
Fields, in order (★ = required):

| # | Element | Maps to | Notes |
|---|---|---|---|
| 1 | First Name ★ | standard | |
| 2 | Last Name ★ | standard | |
| 3 | Phone ★ | standard | |
| 4 | Email | standard | |
| 5 | State ★ | custom `Patient State` | Label: "What state do you live in?" |
| 6 | Dropdown | custom `Decline Lender Patient` | Label: "Who declined the financing?" |
| 7 | Monetary | custom `Treatment Amount Patient` | Label: "About how much was the treatment plan?" |
| 8 | Dropdown ★ | custom `Office Dropdown` | Label: "Which dental office sent you?" |
| 9 | Hidden | custom `Ref Capture` | Pre-fills from `?ref=` |
| 10 | Hidden | custom `Ref Method Capture` | Pre-fills from `?src=` |
| 11 | Hidden | custom `Consent Language Version` | Default value `{{custom_values.consent_language_version}}` |
| 12 | Checkbox (**not** pre-checked, **not** required) | custom `SMS Permission Status` | Text below, "SMS consent" |
| 13 | Checkbox (**not** pre-checked, **not** required) | custom `Call Permission Status` | Text below, "Call consent" |

**SMS consent** (verbatim; counsel approves before go-live):
> I agree Elevated Identities may text me at the number above about my inquiry, including automated messages. Msg & data rates may apply; frequency varies. Reply STOP to opt out, HELP for help. Consent is not required to receive services.

**Call consent:**
> I agree Elevated Identities may call me at the number above, including with automated technology, about my inquiry.

Form settings: on submit, show message "Thanks. Someone from our team will reach out shortly. Check your texts." Turn **off** any "Terms & conditions" element the builder adds by default.

- [ ] Form 1 built. Form ID: `__________`

### Form 2: `Rep Submit`
| # | Element | Maps to |
|---|---|---|
| 1 | Hidden | `Ref Capture` (pre-fills from `?ref=`) |
| 2 | Single line ★ | "Your partner ID" → `Ref Capture` if the hidden field is empty (or make it visible text) |
| 3 | First Name ★ | standard ("Patient first name") |
| 4 | Phone ★ | standard ("Patient mobile") |
| 5 | Single line | "Best time to call" → contact note |
| 6 | Checkbox ★ | "The patient asked me to share their name and number with Elevated Identities." |

No treatment, lender or amount fields. **That's deliberate** (HIPAA, doc 04).
- [ ] Form 2 built. Form ID: `__________`

### Form 3: `Confirm Your Info`
A copy of Form 1 without the office dropdown. Fields pre-fill from the contact.
- [ ] Form 3 built. Form ID: `__________`

## Phase 2: funnel page

- [ ] **Sites → Funnels → New:** `Patient Start`. One step, path `/start`.
- [ ] Page: headline "Declined for dental financing? Let's see what's in the way." Two sentences of copy, **no claims or guarantees**, then embed **Patient Intake** natively (the form element, not an iframe).
- [ ] Domain: connect `elevatedid.com` (or the domain you actually own) in Settings → Domains. **Stop and ask the owner which domain.** DNS changes are theirs to make.
- [ ] Test (after owner approval): open `/start?ref=TEST-DEN-000&src=link`, submit as `ZZ Test Patient`, confirm Ref Capture = `TEST-DEN-000` on the contact.

## Phase 3: workflows (Automation → Workflows → Create → Start from scratch)

Save each one as **Draft**. Names must match exactly. Full logic is in the linked docs. This table covers triggers and the build-critical settings.

| Order | Workflow | Trigger(s) | Key actions | Doc |
|---|---|---|---|---|
| 1 | `B1 · Intake → opportunity` | Form submitted: Patient Intake / Rep Submit / Confirm Your Info | Set consent fields (timestamp = `{{right_now}}`, IP → `Consent IP`). If/else on `Ref First Touch` empty → copy `Ref Capture`. Create/Update Opportunity: **Patient Pipeline** (`J1HkoDLINqtOIovNPs46`), stage **New Referral**, Monetary Value = `{{contact.treatment_amount_patient}}`; copy the partner ID and today → `Referral Date`. Webhook → sync service (URL TBD, leave a placeholder). Branch: tag `manual-rep-submit` → call task only; else → add to B2. | 04 |
| 2 | `B2 · Speed to lead` | Added by B1 only | Guard: `Consent Confirmed By Patient` = Yes AND `SMS Permission Status` is not empty. SMS + email template **B2 · Speed to lead · 0 min** + call task (5 min). Then 5 min / 1 h / 24 h / day 3 / day 5 / day 8 per doc. Goal: appointment booked on **Patient Credit Consult** (`xjCUn38pxxI23KIDhTok`). Day 8 → stage Nurture + tag `nurture-30-60-90`. | 05 |
| 3 | `B3 · Consult booked` | Appointment booked, calendar Patient Credit Consult | Stage Consult Booked, tag `consult-booked`, confirmation, reminders at 24 h and 1 h, task "send personal 2-h text". | 05 |
| 4 | `B4 · No-show` | Appointment status = No-show | Tag `no-show`, stage Contacted, +10 min SMS, same-day call task. | 05 |
| 5 | `P1 · Partner intro call booked` | Appointment booked, calendar Partner Intro Call (**create after Kate is added**) | Stage Intro Call Booked, reminders, "paste notes" task. | 02 |
| 6 | `P2 · Agreement sent` | Documents & Contracts: sent / signed | Nudges at days 2, 5 and 7. On signed → `Partner Signed Date` = today, tag `signed-partner`. | 02 |
| 7 | `P3 · Partner trained` | Tag added `partner-trained` | Guard `Partner ID` not empty; `Partner Trained Date` = today; stage **Signed and Trained**; email template **P3 · Partner referral kit**; add to P4. | 02 |
| 8 | `P4 · Dormancy timer` | Added by P3 or P4b | Wait 30 days → if `Partner Last Referral Date` is more than 30 days ago → stage **Dormant**, tag `dormant-partner`, add to P5. | 02 |
| 9 | `P4b · Referral received` | Tag added `referral-received` | Remove tag; remove from P4, then add to P4; remove from P5; thank-you SMS (first name only). | 02 |
| 10 | `P5 · Dormant re-engagement` | Added by P4 | Day 0 call task; day 7 email template **P5 · Dormant partner · day 7** (**as a task to personalize, not an auto-send**); day 21 task; day 60 "kill or coach" task. | 02 |
| 11 | `B5 · Consult outcome` | Stage → Consult Attended | Disclosure → contract → card on file (no charge) → `Enrollment Date`, `Cancellation Window Ends` → wait → stage **Enrolled**. **Build, but leave the document steps empty until counsel-approved templates exist.** | 06 |
| 12 | `B6 · Nurture 30/60/90` | Tag added `nurture-30-60-90` | Messages at days 30, 60 and 90. | 06 |
| 13 | `F1 · Dispute Fox handoff` | Stage → Enrolled | 6-field task for the owner, due in 4 business hours. | 07 |
| 14 | `F2 · Unsynced enrolled check` | Tag `enrolled-client` + wait 1 business day | If there's no `disputefox-synced` → urgent task. | 07 |
| 15 | `R1 · Monthly update` | Stage → Enrolled, then every 30 days | Email template **R1 · Monthly client update**. | 08 |
| 16 | `R2 · Day-45 call` | Stage → Enrolled + wait 45 days | Call task (Rebecca). | 08 |
| 17 | `R3 · Failed payment` | Payment failed | Per doc. **No collections language.** | 08 |
| 18 | `R4 · Score moved` | Contact changed: `Current Score` or `Items Removed` | Increase → SMS; decrease → task only; `Current Score` ≥ `Target Credit Score` → tag `target-reached`. | 08 |
| 19 | `L1 · Target reached` | Tag added `target-reached` | Stage Improved and Ready to Reapply; ask the patient before notifying the office. | 09 |

Pipeline and stage IDs are in `config/ghl-schema.json → pipelines`.

## Phase 4: Documents & Contracts (after counsel)

- [ ] `Partner Referral Agreement`: merge fields for office, `{{contact.partner_id}}`, `{{contact.comp_structure}}`, `{{contact.comp_rate}}`. Compensation reads "per Schedule A" until counsel approves.
- [ ] `Client Disclosure: Consumer Credit File Rights` (CROA)
- [ ] `Client Services Agreement` + 3-day cancellation form

**Don't write the legal text in the browser session.** Paste in what counsel provides.

## Phase 5: verify

- [ ] End-to-end with `ZZ Test Patient`: link → form → B1 creates the opportunity with partner ID, date and amount → B2 fires the SMS to the owner's phone.
- [ ] Every workflow still in **Draft** except the ones the owner published.
- [ ] Log the form IDs and workflow IDs in `config/ghl-schema.json`.
