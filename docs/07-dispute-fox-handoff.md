# 07 — Hand off to Dispute Fox: once, cleanly

**Fulfillment · Owner: Kate → Hammock**

## The one-page split (print this, put it in Kate's SOP)

| | **GHL owns** | **Dispute Fox owns** |
|---|---|---|
| Who | The person: name, phone, email, address, consent, DND | A copy of identity data needed for letters (set once at handoff) |
| Money | Contract, disclosures, payment method, billing, failed payments, refunds, referral comp | Nothing |
| Conversation | Every SMS, email, call, and note with the client, the partner, and the rep | Nothing client-facing. Hammock's team doesn't message clients directly. |
| The file | Only 3 mirrored numbers: `round_number`, `items_removed`, `current_score` (NUMERICAL) | Report import, audit, items, letters, rounds, bureau responses, secondary-bureau sweeps |
| Pipeline | Stage, outcome, service stage | Its own client status |

**If a piece of data is in the wrong column, it gets deleted from that system, not maintained in both.** Two CRMs holding overlapping client data always drift apart. You find out the day a client says "your other person told me something different."

## Handoff procedure

**Trigger:** stage changes to Enrolled. Because of doc 06, that happens only after the 3-day window closes.

**Path A: integration.** If Dispute Fox exposes a webhook or Zapier action for "create client," a workflow `F1` fires it with the 6 fields below, then waits for Dispute Fox to call back with the client ID. Confirm with Dispute Fox support what's actually available on your plan. Don't build on an assumption.

**Path B: manual (start here).** `F1` creates a task for Kate, due in 4 business hours:

> **Create Dispute Fox client**: fixed checklist:
> 1. Legal first + last name (exactly as on the ID, not the nickname in GHL)
> 2. Current address + prior address if moved in the last 2 years
> 3. DOB
> 4. Last 4 SSN (full SSN goes directly into Dispute Fox from the client's IDIQ enrollment, **never through GHL notes or SMS**)
> 5. Email
> 6. Mobile
>
> Then paste the Dispute Fox client ID into `contact.dispute_fox_client_id` and add tag `disputefox-synced`.

That's a 4-minute task. It stays manual until volume justifies the integration. The breakpoint is about **40 enrollments a month**: at that point Kate spends 3+ hours a month on it, and one typo'd DOB costs more than that.

Link by ID, not name: `dispute_fox_client_id` goes on the GHL contact. "Maria Lopez" and "María López-Garcia" are the same client, and a name match will lose her.

**Guard:** workflow `F2` runs daily. Any contact tagged `enrolled-client` for more than 1 business day without `disputefox-synced` → urgent task to Kate. A client who paid and has no file is how a refund demand starts.

## After handoff: Hammock's lane

IDIQ pull → report import → audit → round 1 built. Hammock's team runs the rounds and secondary-bureau sweeps (LexisNexis, Innovis, SageStream and similar) with their own letters. LetterStream mails.

**Only three things come back into GHL:** `contact.round_number`, `contact.items_removed`, and `contact.current_score`, all NUMERICAL. The mechanism, in order of preference:
1. A Dispute Fox webhook or Zapier trigger on round completion → GHL inbound webhook workflow updates the 3 fields.
2. A weekly CSV export from Dispute Fox → import into GHL by `dispute_fox_client_id`.
3. Hammock's team updates the 3 fields directly in GHL. Give them a restricted GHL user that can edit those fields and nothing else.

When any of the three changes, the retention workflows in doc 08 fire. If this sync is late, the client gets silence, and silence is the churn driver.

## Monthly audit (15 minutes)

On the first Monday, Kate pulls **10 random enrolled clients** and checks:
- [ ] `dispute_fox_client_id` in GHL matches a real client in Dispute Fox
- [ ] Round number matches
- [ ] Items removed matches
- [ ] No client data is maintained on the wrong side (e.g. a phone number updated in Dispute Fox but not GHL)
- [ ] The last billing charge came **after** the last documented round

Log the result as a note on a "Fulfillment Audit" internal contact. Two months of clean audits → drop to 5 files. Any mismatch → back to 10, and fix the root cause, not the record.
