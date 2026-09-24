# 08 — Keep the client warm while the work is slow

**Fulfillment · Owner: Rebecca · Monthly**

Credit repair churns for one reason: **45 days of silence while the bureaus investigate.** The bureaus have 30 days (sometimes 45) to respond, then mail takes time, then the round gets built. From the client's side, they paid, and nothing happened. They cancel the card and tell the rep you took their money. The rep tells the office. The office stops sending.

Churn in this business isn't a billing problem. It's a communication problem that shows up in billing.

## Workflow `R1 · Monthly update` (automated)

**Trigger:** 30, 60, and 90 days after `enrollment_date`, and every 30 days after that while the stage is Enrolled.

Three short parts, plain language, no bureau jargon:
1. **What we sent:** "In October we disputed 4 items with Equifax, Experian and TransUnion."
2. **What came back:** "Experian removed the Midland collection. The other 3 are still being investigated."
3. **What's next:** "Round 2 goes out around Nov 18. You don't need to do anything. If you get mail from a bureau, snap a photo and text it to us."

Pull the numbers from the 3 mirrored fields. If the numbers didn't change, **say that honestly**: "No changes yet. Equifax hasn't responded, which is normal in the first 30 days." A clear "nothing yet, and here's why" beats a vague "we're working hard on your file."

## Day 45: a person calls (`R2`)

**Trigger:** 45 days after `enrollment_date` → task to Rebecca: "Check-in call."

That's when doubt peaks. Script outline:
- "I'm just checking in. No news needed from you. How are you feeling about it so far?"
- Let them talk. The real objection surfaces here ("my sister said this is a scam," "I saw my score go down").
- Explain the next date.
- Log the call outcome as a note.

A human voice at day 45 is worth more than all the automated messages combined.

## `R3 · Failed payment` (a churn event, not a billing event)

**Trigger:** Payment failed (GHL Payments / your processor integration).
- Hour 0: tag `payment-failed`, and SMS: "Your card on file didn't go through. Here's a link to update it. No rush on today, your file keeps moving."
- Day 2: call task for Rebecca. Most failed payments in this population are **overdraft timing**. Ask what day works better and move the billing date. A payment-date change saves more clients than any dunning email.
- Day 7: email.
- Day 14: task "Pause decision." Pause services (and don't bill for a paused month) rather than cancel.
- Don't threaten collections. You'd be a credit repair company sending a client to collections.

## `R4 · Score moved`

**Trigger:** `contact.current_score` or `contact.items_removed` changed.
- Any removal or any score increase → "Here's what changed" SMS, even when it's small. "+6 points" is news to someone who hasn't had good credit news in years.
- A score decrease → **no automated message**. Task for Rebecca: call and explain it (new inquiry, a utilization spike, a dispute notation). An automated "your score changed!" text on a drop is the worst message in this business.
- `current_score ≥ target_credit_score` → tag `target-reached` → doc 09.

## Retention numbers to watch (scorecard)

- Month-over-month cancellation rate by enrollment cohort
- Share of clients with a completed day-45 call (target 100%)
- Failed-payment recovery rate within 14 days
- Share of month-2 cancellations that happened **before** the first "what came back" message. If it's high, the update is too late.
