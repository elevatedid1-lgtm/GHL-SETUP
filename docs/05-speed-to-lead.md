# 05 — Speed to lead, then book the consult

**Pipeline B · Owner: Kate / Rebecca · Target: under 5 minutes**

This person was told "no" in a dental chair an hour ago, often in front of a coordinator and sometimes a spouse. Right now they're motivated and a little ashamed. By tomorrow the shame wins, and they've decided the veneers weren't meant to be. You're not selling. You're catching them before they talk themselves out of it.

## Workflow `B2 · Speed to lead`

**Entry:** from `B1` only, and only when `consent_confirmed_by_patient = Yes` and SMS permission is granted.

| When | Channel | Action |
|---|---|---|
| 0 min | SMS | Instant text with the consult link (copy in `templates/patient-messages.md`). |
| 0 min | Email | Same message, plus what to expect on the consult. |
| 0 min | Task / call | **Call connect**: GHL rings the assigned user, and when they pick up, it dials the patient. If you're not using call connect, create a task due in 5 minutes and assign by round robin (Kate / Rebecca). |
| 5 min | SMS | Only if not booked **and no reply**: "Tried calling. Here's the link again, or reply with a good time." |
| 1 hr | Call task | Second call attempt. |
| 24 hr | SMS + call | |
| Day 3 | SMS | Different angle: one line about what the consult is ("15 minutes, we look at the report together, you'll know what's in the way"). |
| Day 5 | Email + call | |
| Day 8 | SMS | Graceful close: "I'll stop reaching out. If you want to take another look, this link works any time." |
| Day 8+ | Move | To **Nurture**, stage Nurture, add to `B6` (30/60/90). **Never to Lost.** |

**Stop conditions, checked as workflow goals rather than if/else at each step:** appointment booked on Patient Credit Consult → jump to `B3`. Inbound reply → stop the sequence and create a task. A human conversation now beats a robot, and a robot talking over a human is the fastest way to look like a scam.

Increment `contact.consult_attempts` on every call task completed. Rebecca and Kate will swear they called 6 times, and the field will say 2.

### Business hours
A lead submitted at 9:40 pm gets the instant SMS and email, but the call task is due at 8:30 am. Use the workflow's time-window setting on call steps only. **Don't** delay the first text. People fill in this form at night, after the kids are down, and the ones who get an answer at 9:41 pm book.

## Workflow `B3 · Consult booked → show up`

- **Trigger:** Appointment booked, calendar = Patient Credit Consult.
- Move to **Consult Booked**, tag `consult-booked`.
- Confirmation SMS + email: time, the link, and **what to have ready** ("the email from the lender, if you have it; 15 minutes somewhere you can talk").
- Reminders at 24 hours and 1 hour, each with a reschedule link.
- **The 2-hour personal text** from the assigned consultant, sent by hand: "Looking forward to 3pm. I'm [Kate]." This single message cuts no-shows more than any automated reminder, because it tells them a real person is expecting them.

No-shows are the biggest single leak in this funnel, and they happen for a specific reason here. The patient fears the consult is where they get judged again. Every reminder should lower that fear ("no judgment, we see this every day"), not raise urgency.

## Workflow `B4 · No-show`

- **Trigger:** Appointment status = No-show.
- Tag `no-show`, move back to **Contacted**.
- 10 minutes after the missed start: "We missed you. No problem at all. Here's the link to grab another time."
- A call task for the same day.
- Day 2: one more SMS. Then into `B2` from the Day 3 step onward (using a "Go to" step or a sibling workflow).
- Track `no-show` separately in the scorecard. A partner whose patients no-show at 60% is usually one whose coordinator oversold ("they'll fix it"), which makes it a training problem.

## Stage moves

| Stage | Set by |
|---|---|
| New Referral | `B1` on submission |
| Contacted | First two-way contact: SMS reply, or a call marked connected (manual) |
| Consult Booked | `B3` |
| Consult Attended | Appointment status = Showed. The consultant marks it, and a workflow moves the card. |

## Reference ratios (for staffing, not promises)

These are assumptions, used in `scripts/projections.py`:
- One speed-to-lead coordinator can properly work about **25–35 new leads/day** (first touch plus follow-up load). Past that, speed-to-lead quietly slips from 5 minutes to 2 hours, and contact rate drops with it.
- The first thing to degrade under volume is the 1-hour and 24-hour call attempts. Watch `consult_attempts` per lead weekly. When the average drops below 3 for leads that never booked, you need another person.
