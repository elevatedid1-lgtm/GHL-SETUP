# 09 — Close the loop back to the office

**Pipeline B → Pipeline A · Owner: Kate**

Most referral programs skip this step, and it's the one that turns one rep into a network. The office gets back a case it had written off. That's the story the rep tells the other 300 reps, and it's worth more than anything you could write.

## `L1 · Target reached`

**Trigger:** tag added `target-reached` (from `R4`), or a manual stage move to Improved and Ready to Reapply.

1. Move to **Improved and Ready to Reapply**.
2. Message the patient: "You're at 648. That's in the range [lender] usually approves. Want us to let [office] know you're ready to re-apply?"
3. **Only on the patient's yes** (reply or button): notify the referring partner. "Maria is ready to reapply. She asked us to let you know." First name only, plus the fact that she's ready. Never the score or the items.
   - Why the yes matters: the patient's credit situation is the patient's information. Telling the office without asking, even with good news, is a breach of trust at minimum. Your enrollment contract should have an opt-in for this (counsel item). Even so, asking in the moment is the right move.
4. Task to Kate: call the coordinator within 1 business day. "Did she get scheduled?"
5. Set `contact.reapply_date` when the office confirms.

## Log the outcome honestly

`contact.client_outcome` is one of:

| Outcome | Meaning |
|---|---|
| **Approved** | The office confirms financing was approved on re-application. |
| **Improved, not yet approved** | The target was reached or the score moved materially, but no approval is confirmed yet (not re-applied, or declined again). |
| **Closed, no result** | Services ended without material improvement. |
| Cancelled in 3-day window / Cancelled after start / Refunded | Self-explanatory. |

**Report the third one honestly.** Every partner statement and every rep scorecard includes "Closed, no result." A partner who catches you inflating results is gone permanently, and so is every office they talk to. A partner who sees you report your misses believes your wins.

"Approved" requires the office to confirm it. Until then the outcome is "Improved, not yet approved." This is the one field reps will quote to other reps, so it has to be airtight.

## Referral compensation

**Don't pay until counsel has approved the structure in writing (doc 12).** Once they have:

- Calculated on **collected** revenue, net of refunds and chargebacks. Never on enrolled or contracted revenue.
- Paid on a **fixed date** (e.g. the 15th, for the prior month's collections).
- **Clawback:** a refund or chargeback within 90 days of a comp payment is netted from the next statement. Put it in the agreement, because it will happen.
- **W-9 before the first payment** (`contact.w9_on_file`). 1099-NEC at year end for anyone paid $600+ (confirm the current threshold with your CPA).
- **Statement** showing every attributed patient. The spec says "by name and date." Do that only if the client's enrollment agreement authorizes sharing their name with the referring partner. Otherwise use first name + last initial + referral date + status. Counsel item.

`scripts/comp_statement.py` produces the statement from a GHL opportunity export and handles both structures:

```
python3 scripts/comp_statement.py export.csv --month 2026-11 --structure per_enrollment --rate 150
python3 scripts/comp_statement.py export.csv --month 2026-11 --structure pct_collected --rate 0.10
python3 scripts/comp_statement.py export.csv --month 2026-11 --structure flat_monthly --rate 500
```

Switching structures means changing `contact.comp_structure` and `contact.comp_rate`. It's a settings change, not a rebuild.
