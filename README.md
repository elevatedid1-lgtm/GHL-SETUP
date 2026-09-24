# Elevated ID: GHL referral system

The build spec, automation, and playbooks for the dental-partner referral pipeline in GoHighLevel (sub-account `Evfk5CgjxNHryw79uGDD`).

Two pipelines, one hinge:
- **Pipeline A: Partner Pipeline** (Kate). Offices and financing reps: Prospect → Signed & Trained → Producing.
- **Pipeline B: Patient Pipeline** (Kate / Rebecca / Twin). Declined patients: New Referral → Enrolled → Ready to Reapply.
- **The hinge:** every patient carries a partner ID from first touch, so reporting, compensation, and the story told to the next 300 reps are all provable.

## Start here

| Doc | Step | Owner |
|---|---|---|
| [00 Live account audit](docs/00-live-account-audit.md) | What's already built, and the 9 things to fix before partner #1 | Kate |
| [02 Partner pipeline](docs/02-partner-pipeline.md) | Stages, workflows P1–P5, agreement checklist, 15-min training | Kate |
| [03 Attribution kit](docs/03-attribution-kit.md) | ID convention, link/QR/keyword/dropdown/rep-submit, first-touch rule | Kate |
| [04 Intake & consent](docs/04-intake-and-consent.md) | Fields, forms, TCPA consent, HIPAA on the office side, workflow B1 | system |
| [05 Speed to lead](docs/05-speed-to-lead.md) | B2–B4: 5-minute response, 6 touches / 8 days, no-show recovery | Kate / Rebecca |
| [06 Consult & enrollment](docs/06-consult-and-enrollment.md) | CROA/TSR gate, 3-day window, billing timing, B5–B6 | Twin / Kate |
| [07 Dispute Fox handoff](docs/07-dispute-fox-handoff.md) | One-page system-of-record split, 6-field handoff, monthly audit | Kate → Hammock |
| [08 Client retention](docs/08-client-retention.md) | R1–R4: monthly updates, day-45 call, failed payments, score moves | Rebecca |
| [09 Close the loop](docs/09-close-the-loop.md) | Ready-to-reapply, honest outcomes, comp statements | Kate |
| [10 Scorecard](docs/10-scorecard.md) | Weekly and monthly review, kill-or-coach | Twin |
| [11 Projections](docs/11-projections.md) | Conservative / realistic / aggressive by phase: leads, revenue, comp, FTEs | Twin |
| [12 Counsel & payments](docs/12-counsel-and-payments.md) | Questions for counsel, payment-provider verification | Twin |
| [templates/](templates/) | Partner scripts, patient messages | — |

`config/ghl-schema.json` is the source of truth: pipeline and stage IDs, every custom field (existing and to-create, with the real, sometimes misspelled, keys), tags, and calendars.

## Build order

1. **Counsel (doc 12), started now, in parallel.** Nothing below waits on it except **paying partners** and **charging clients**. Start the high-risk merchant account application at the same time.
2. **Fix the account (doc 00).** Assign the 148 prospects to Kate, fix tag typos, rename field display names, then provision fields:
   ```
   export GHL_TOKEN=pit-...            # Settings → Private Integrations
   python3 scripts/provision_fields.py          # dry run: shows what it would create
   python3 scripts/provision_fields.py --apply
   ```
3. **Calendars and forms** (docs 04, 05).
4. **Workflows** in this order: B1 → B2 → B3/B4 → P1–P5 → B5/B6 → F1/F2 → R1–R4 → L1. Build them in the UI; GHL's API can't create workflows.
5. **Deploy the sync service** (`service/referral_sync.py`) as a serverless function (AWS Lambda handler included), and point B1's webhook at it. This is the piece that moves a partner to Producing and resets dormancy. GHL workflows can't update a *different* contact on their own.
6. **Test end-to-end** with one internal "partner" and one internal "patient" before the first real office.
7. **Pilot:** 10 warm offices from the rep's 112, for 90 days.

## Phased growth

| Phase | Scope | Gate to move on |
|---|---|---|
| **Pilot** (90 days) | 10 offices chosen with the rep, prioritizing high decline volume | Counsel sign-off in hand. ≥ 30 referrals. Measured show, enroll, and realization rates. Speed-to-lead < 5 min held. Zero consent or attribution incidents. |
| **Phase 2** | Remaining offices of the first rep (112 reported) | Positive contribution before staff at measured rates. Fulfillment audit clean 2 months running. Dispute Fox handoff automated or staffed. |
| **Phase 3** | Rep network (300+ reported) | Rep-level scorecard live (`parent_rep_id`). A second partner manager hired **before** onboarding reps, not after. |

**112 offices and 300 reps are reported potential, not verified pipeline.** Verify them as they're touched: each signed office is a real one. Re-run `scripts/projections.py` with pilot data before committing to Phase 2 hiring.

## Code

```
service/ghl.py              GHL API v2 client (stdlib only)
service/referral_sync.py    patient submission → partner record (Producing, dormancy reset, count)
scripts/provision_fields.py create missing custom fields from config (idempotent, dry-run default)
scripts/projections.py      3-scenario model → docs/11-projections.md
scripts/comp_statement.py   monthly partner statements; flat / per-enrollment / % collected
tests/                      python3 -m unittest discover -s tests
```
