# 02 — Work the partner pipeline to a signed agreement

**Pipeline A (Partner Pipeline) · Owner: Kate · 7–21 days per partner**

## The pitch

Don't open with "we do credit repair." Open with this:

> Your declined patients are treatment plans you've already diagnosed, presented, and lost. We work them and send them back approved.

The treatment coordinator's incentive is closed treatment plans. Your fee is a nice extra. The reason she'll change her behavior is that a $22,000 case she wrote off in March comes back in July. Pitch to that.

What an experienced person watches for:
- **The coordinator is the buyer. The dentist signs.** Dentists approve anything that doesn't cost chair time. Coordinators decide whether a single patient ever hears your name. Win the coordinator on the intro call, then get the dentist's signature.
- **"We already have a second-look lender."** Most offices do (Sunbit, Cherry, Proceed behind CareCredit). Answer: "Good. We take the ones your second look also declined." You don't compete with the lender stack. You're what comes after it.
- **The rep who introduced you is watching.** She's lending her credibility with 112 offices. A slow follow-up with one of her offices gets back to her within a week.

## Stage definitions: entry criteria, exit criteria, automation

A stage is a fact, not a feeling. If the exit criterion isn't met, the card doesn't move.

| Stage | Enters when | Leaves when | GHL automation |
|---|---|---|---|
| **Prospect** | Imported or added. Tagged `partner-prospect`. | A human at the office has responded (call, email, or in person). | None. **No automated SMS to cold prospects** (see the audit doc). |
| **Connected** | Two-way contact with a named person, not the front desk voicemail. | That person agrees to a conversation about declined patients. | Task for Kate: "Log name and title of contact." Fills `contact.job_title`. |
| **Conversation** | A real discussion of their decline volume has happened. | An intro call is on the calendar. | Send the intro-call booking link (Partner Intro Call calendar, 20 min). |
| **Intro Call Booked** | Appointment exists on **Partner Intro Call**. | Call happened and they said yes to seeing the agreement. | Workflow `P1` (below): confirmation, 24h/1h reminders, recording link and notes to the contact. |
| **Agreement Sent** | Document sent through GHL Documents & Contracts. | Countersigned. | Workflow `P2`: nudges at day 2 and day 5; task to Kate at day 7. |
| **Signed & Trained** | Signed **and** the 15-minute screen share is done. `contact.partner_trained_date` is set, and so are `partner_id`, the link, the QR code, and the keyword. | First patient submission carrying their ID. | Workflow `P3`: send the kit and start the 30-day dormancy timer. |
| **Producing** | Set **automatically** by `service/referral_sync.py` on first attributed submission. | 30 days with no attributed submission. | Workflow `P4`: every new referral resets the timer and sends a thank-you. |
| **Dormant** | 30 days with no submission. | A new attributed submission (auto back to Producing), or a kill decision at 60 days. | Workflow `P5`: re-engagement sequence. |

**Signed but not trained is Agreement Sent, not Signed & Trained.** Partners who were never shown what to say at the moment of decline send zero patients. The 15-minute training is the conversion event, not the signature.

## Workflows to build (GHL → Automation → Workflows)

GHL's public API can't create workflows, so these get built in the UI. Name them exactly as written so the scorecard filters work.

### `P1 · Partner intro call booked`
- **Trigger:** Appointment status is Confirmed, calendar = Partner Intro Call.
- Move the opportunity to Intro Call Booked.
- SMS and email confirmation, including the agenda: "20 minutes: how many patients you decline a month, what happens to them now, and how they'd come back."
- Wait until 24h before → reminder. Wait until 1h before → reminder.
- **Trigger 2:** Appointment status = Showed. Create a task for Kate: "Paste call notes and recording link into contact notes within 2 hours."
- **Trigger 3:** Appointment status = No-show. Send a reschedule link that same day, then add a task. Don't auto-send a second reschedule. Kate calls.

### `P2 · Agreement sent`
- **Trigger:** Documents & Contracts → Document sent (template "Partner Referral Agreement").
- Move the opportunity to Agreement Sent.
- Wait 2 days. If not signed, send SMS: "Any questions on the agreement? Happy to walk through it in 5 minutes."
- Wait 3 days. If not signed, send an email from Kate.
- Wait 2 days. If not signed, create a task: "Call. Something in the agreement is a blocker, find out what."
- **Trigger 2:** Document signed → set `contact.partner_signed_date`, add tag `signed-partner`, create task "Book 15-min training within 3 business days", and send the training calendar link.

### `P3 · Partner trained → kit + dormancy timer`
- **Trigger:** Tag added `partner-trained`. Kate adds this at the end of the screen share.
- Guard: if `contact.partner_id` is empty, stop and create a task: "Assign partner ID before training counts."
- Set `contact.partner_trained_date` = today.
- Move the opportunity to Signed & Trained.
- Send the kit email (template in `templates/partner-scripts.md`): their link, QR PDF, SMS keyword, rep-submit form link, and the one-card decline script.
- **Add to workflow** `P4 · Dormancy timer`.

### `P4 · Dormancy timer (resettable)`
This is the standard GHL pattern for "N days with no event," because there's no native trigger for it:
- **Trigger:** Added by `P3`, or re-added by `P4b`.
- Wait 30 days.
- If `contact.partner_last_referral_date` is before 30 days ago, move to Dormant, add tag `dormant-partner`, and add to `P5`.

### `P4b · Referral received (resets timer)`
- **Trigger:** Tag added `referral-received`. The sync service adds it.
- Remove the tag, so the next referral can add it again.
- **Remove from workflow** `P4`, then **Add to workflow** `P4`. This restarts the 30-day clock.
- Remove from `P5` if present.
- SMS to the partner: "Got {{patient first name}}, reaching out now. Thank you." Only if `contact.sms_permission_status` = granted.
  - Put first name only in the message, never a last name or a reason. That's a privacy habit worth keeping even where no law requires it.

### `P5 · Dormant re-engagement`
- Day 0: Kate calls personally (task). Don't open with "you haven't sent anyone." Open with a case: "We just got a patient from [nearby office] approved for a $14k implant case. Want me to show your new coordinator the script?" The most common cause of dormancy is **staff turnover**. The person you trained left.
- Day 7: email with one anonymized result.
- Day 21: task: "Visit or ask the rep to mention us on her next stop."
- Day 60 with no referral: task "Kill or coach decision." Kate either books a retraining or moves the card to Lost with reason `No production 60d`. Don't let dormant partners eat the week.

## The agreement: what it must say

Build it as a GHL Documents & Contracts template, with merge fields for office name, partner ID, comp structure, and comp rate. **Counsel drafts the operative language.** This is the checklist to give them:

1. **What we do:** credit education and dispute services for patients who choose to engage us directly. We don't provide dental financing and we don't guarantee approval.
2. **What the partner does:** hands the patient a card or link, or submits with the patient's documented permission. **The partner does not send us patient health or financial information.** The patient tells us themselves. This keeps the dental office clear of HIPAA disclosure problems (see doc 04).
3. **Handover:** the four attribution paths in doc 03, and what counts as an attributed referral.
4. **Compensation:** structure (flat monthly marketing fee **or** per-enrollment), rate, basis (collected revenue net of refunds and chargebacks), statement contents, pay date, and the clawback window. **Blank until counsel signs off.** See doc 12.
5. **Patient consent and privacy:** who may contact whom, and a no-texting-patients-on-our-behalf clause.
6. **Mutual 30-day termination without cause,** plus a clause that attribution for patients already submitted survives termination.
7. **No guarantees, no claims:** the partner may not tell patients we'll "fix their credit" or that they'll get approved. One coordinator ad-libbing "they'll get you approved in 30 days" is a UDAP/CROA exposure with your name on it.
8. **Agreement version** stored in `contact.agreement_version`.

## The 15-minute training (screen share)

Agenda, timed:
1. **(2 min)** What happens after they hand the card. Show the patient's first text so they know what the patient will receive.
2. **(5 min)** The decline-moment script. Role-play it once, with them saying it back. From `templates/partner-scripts.md`:
   > "I'm sorry, it didn't go through today. That doesn't mean no. It usually means something on your credit report is in the way, and a lot of the time it's fixable. We work with a team that helps patients in exactly this spot. Scan this or text APPROVE14 and they'll reach out today. Once you're ready, we'll re-run it and get you started."
3. **(3 min)** The four paths: card, link, keyword, and the rep-submit form for "she already left."
4. **(3 min)** What they'll see: the thank-you text on every referral, and a monthly statement.
5. **(2 min)** Where the cards live. Put them physically at the checkout or treatment-plan desk, not in a drawer. Ask them to show you where.

Close with Kate adding tag `partner-trained` while still on the call.

## Pacing: 7–21 days is realistic

| Day | What happens |
|---|---|
| 0 | Rep intro, or Kate's first call. |
| 1–3 | Conversation, then book the intro call. |
| 3–7 | Intro call. Send the agreement the same day, while they're warm. |
| 7–14 | Signature. Dentists sign between patients or on Friday afternoons. |
| 10–21 | Training. Don't let this slip past 3 business days after signing. Enthusiasm decays in about a week. |

At this pace one partner manager works about **15–20 active pipeline partners at once** without dropping follow-ups. Pilot with 10.
