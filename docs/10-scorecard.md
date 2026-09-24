# 10 — Scorecard and weekly review

**Owner: Twin · Weekly + monthly**

## The dashboard (GHL → Dashboard → new "Partner Scorecard")

The four numbers per partner, sorted descending by referrals:

| Widget | Source | Build |
|---|---|---|
| Referrals sent | Patient Pipeline opportunities, grouped by `referral_partner_id` | Opportunity table widget, filtered to Patient Pipeline, date = created |
| Consult show rate | Consult Attended ÷ Consult Booked | Funnel widget, Patient Pipeline, per partner filter |
| Enrollment rate | Enrolled ÷ Consult Attended | Same funnel |
| Collected revenue | Payments / transactions by contact → partner | Payments are per contact. The partner rollup comes from the monthly `comp_statement.py` output until GHL reporting can group payments by a custom field. |

GHL's native dashboards can't group by a custom field in every widget type. When a widget won't do it, use a Smart List per top partner (filter: `referral_partner_id = X`), or the CSV export plus `comp_statement.py`. Don't burn a week fighting the dashboard builder.

Sort descending and the truth appears fast. **Two or three offices usually produce most of the volume, and the rest send one patient and stop.** Protect the top three: a personal visit, the first look at new materials, and fast answers when they have a problem.

## Weekly (30 minutes, Monday)

| Metric | Target (pilot) | Where |
|---|---|---|
| New leads by partner | — | Smart list, created last 7 days |
| Speed-to-lead (median minutes to first human touch) | < 5 min in business hours | Opportunity created → first outbound call/SMS by a user. Spot-check 10 leads by hand until it can be automated. |
| No-show rate | < 35% | Appointments report, Patient Credit Consult calendar |
| Stuck files | 0 older than: New Referral 1 day, Contacted 8 days, Consult Booked 14 days, Enrolled without `disputefox-synced` 1 day | Pipeline view, sort by days in stage |
| `attribution-missing` / `attribution-conflict` open | 0 older than 24 h | Smart list by tag |

## Monthly (60 minutes, first Monday)

- **Cohort collections:** collected by enrollment month, not calendar month. A calendar-month view hides that the September cohort is churning faster.
- **Churn month by month** per cohort (cancelled after start ÷ started).
- **Comp paid vs. collected:** comp should never exceed the agreed percentage of collected revenue. If it does, a refund didn't get clawed back.
- **Cost per enrollment:** (staff time + tools + comp + processing) ÷ enrollments.
- **Outcome mix:** Approved / Improved / Closed, no result. The share of Approved is what the rep network will judge you on.
- **Fulfillment audit result** (doc 07).
- **Re-run `scripts/projections.py`** with the real rates in place of the assumptions. That's how the pilot earns the right to scale.

## Kill or coach

Any partner at zero referrals for **60 days** gets a decision: coach (book retraining, find out who left) or cut (move to Lost, reason `No production 60d`). Chasing dormant partners is where a small team's hours quietly disappear. In the realistic network projection, partner managers are the largest staffing line (2.4 FTE against 0.9 closers), because unproductive partners still cost follow-up time. Pruning them is how that scenario gets to a positive margin.
