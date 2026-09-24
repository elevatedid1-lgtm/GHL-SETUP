# 06 — Consult and enrollment

**Pipeline B · Owner: Twin / Kate**

## Running the consult

1. **Pull the report with the client present.** Pull through the IDIQ link on screen share or in the room, never "send us your SSN and we'll pull it."
2. **Show the specific items standing between them and approval.** Not "your score is low": "this $412 medical collection from 2022 and this late payment on the Capital One card are what a lender's model is reacting to."
3. **Give a realistic timeline and say the honest thing.** Some files clear in 60 days and some don't clear at all. An accurate, verifiable, recent negative item may not come off. Say that. The client who hears it from you on day 1 trusts you on day 60. The client who hears it on day 60 files a complaint.
4. **Set the target.** Ask the office or the rep what score or profile the lender needs (usually roughly known per lender), and write it into `target_credit_score`.
5. Record `contact.starting_credit_score`. Without a baseline, "score movement" messages later have nothing to compare to.

You're qualifying out as much as in. A patient with a 2025 bankruptcy and a $38k plan isn't getting approved by CareCredit in 90 days, and enrolling them anyway costs you the fee, the partner, and a review.

## Enrollment: the compliance gate

The **Credit Repair Organizations Act** (15 U.S.C. §1679) requires the following. Counsel confirms before enrollment #1:

| Requirement | How it's enforced in GHL |
|---|---|
| **Written disclosure statement** ("Consumer Credit File Rights Under State and Federal Law") given **before** the contract is signed, as a separate document. | Documents & Contracts: disclosure template sent first. The contract template can't be sent until the disclosure is signed (workflow `B5` guard). |
| **Written contract** with the terms, total cost, services, time frame, and the 3-business-day cancellation right with a cancellation form. | Contract template (counsel-drafted). The cancellation form is attached. |
| **No fees before services are fully performed.** | Billing is scheduled **after** work is performed. See below. |
| **3-business-day right to cancel.** | `contact.cancellation_window_ends` = enrollment + 3 business days. **No fulfillment file, no dispute letter, and no charge** before that date. |

**The Telemarketing Sales Rule** is stricter, and it's the one operators miss. For credit repair sold **by phone**, it bars payment until the promised time frame has passed **and** the client has a consumer report, issued more than six months after the results, that shows them. Monthly-after-service billing may **not** satisfy it. Whether an in-person or video consult removes you from the TSR is a counsel question (doc 12, B2). Until it's answered, treat pricing and billing timing as undecided.

**State law:** many states add registration, a surety bond, and their own contract language for credit services organizations. These are keyed to **where the client lives**, not where you are. In a multi-state referral network, that's the trap: one rep's 112 offices can span three states. `contact.patient_state` is required on the intake form so this is known **before** the consult. Maintain a list of approved states. If the patient's state isn't on it, tag `counsel-hold`, have the consult, and don't enroll.

## How to structure the $1,500 so it's earned before it's charged

Options for counsel to choose between. Don't pick one without them:
- **Monthly after service:** e.g. $250/month × 6, each billed after that month's dispute round is sent and documented. The most common structure, and the easiest to defend.
- **Per deletion:** billed per negative item removed, confirmed by bureau response. Revenue is lumpy, but it's the cleanest "fully performed" story.
- **Hybrid:** a small monthly service fee after each round plus a per-deletion fee. Complex to explain. Avoid it in the pilot.

Model it in GHL as a **Product** with a **recurring price**, with the first charge date set to **after** round 1 is documented, not at signup. `scripts/projections.py` uses a 75% realization assumption: you won't collect all $1,500 from everyone.

## Payments: don't assume you can use Stripe

Credit repair is a restricted or prohibited category at many mainstream processors, and GHL Payments runs on Stripe by default. A Stripe account that gets flagged after 40 enrollments freezes the funds. Before enrollment #1, see doc 12 for the payment-options checklist (high-risk merchant account via NMI or Authorize.net, both of which integrate with GHL).

## Workflow `B5 · Consult outcome`

- **Trigger:** Opportunity stage changed to Consult Attended, or a manual outcome button (a custom "Outcome" dropdown on the consult form the consultant fills in).
- **Enroll path:**
  1. Send the disclosure document. Wait for signature.
  2. Send the contract. Wait for signature.
  3. Collect a payment method on file (card vault, **no charge**).
  4. Set `enrollment_date` = today, `cancellation_window_ends` = +3 business days.
  5. **Wait until** `cancellation_window_ends` + 1 day.
  6. If no cancellation was received → move to **Enrolled**, tag `enrolled-client`. **This stage change is the only trigger allowed to create a fulfillment file** (doc 07).
  7. If cancelled → `client_outcome = Cancelled in 3-day window`, stage Closed with No Result, $0 charged. Nothing to refund, because nothing was charged.
- **Not-ready path:** stage Nurture, add to `B6`.
- **Not-a-fit path:** Closed with No Result, `client_outcome = Closed, no result`, with a kind SMS and, where it applies, a non-profit credit counseling referral (NFCC). Offices notice when you treat their patients decently even when there's no fee in it.

## Workflow `B6 · Nurture 30/60/90`

Day 30, 60, and 90 SMS/email, each with a reason to come back: "Offices usually re-run applications in the spring. If you want to be ready, here's the link." Many of these patients come back when **the office** follows up on the treatment plan, so give the office a way to trigger it. If the coordinator sends the patient's link again, `B1` re-engages the existing contact without losing first-touch attribution.
