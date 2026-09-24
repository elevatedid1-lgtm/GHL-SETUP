# 12 — Get it reviewed before you pay anyone or charge anyone

Nothing here is legal advice. It's the list of questions a practitioner brings to counsel so the hour you pay for gets used on decisions, not education.

## A. Healthcare attorney: partner compensation

Per-patient compensation to a dental office, or its staff, can trip **state patient-brokering, fee-splitting, and anti-kickback statutes**, depending on the state and how the money moves. That's true even for cash-pay cosmetic work, because several states' laws aren't limited to government-payer business. Dental board rules on accepting rebates or referral fees also apply to the **dentist's** license, separately from any statute.

Questions to get answered **in writing, before the first check**:

1. In each state where we'll have partners (start with SC, where the prospect list is), may we pay a dental office, its staff, or a financing rep for referring patients to a **non-healthcare** service (credit repair)?
2. Which is safer: a **flat monthly marketing fee** (fair market value, not tied to volume), **per-enrollment**, or **percent of collected**? What documents fair market value for a flat fee?
3. May we pay **individual office staff** (the coordinator) directly, or only the practice entity? Paying staff directly, behind the dentist's back, is the version that ends partnerships and draws board complaints.
4. **The financing rep:** she's employed by or contracted to a lender (CareCredit, Sunbit, etc.). Does her employer's policy or contract prohibit outside compensation for routing declined applicants? **Ask her before counsel does.** If she's prohibited, the structure might be relationship-only for her and comp for the offices, or a formal agreement with her employer. Discovering this after 300 reps are in is the worst version.
5. Can the comp structure be different per state? (The pipeline supports it: `contact.comp_structure`, `contact.partner_state`.)
6. Does the office's HIPAA exposure change if staff use the rep-submit form? (Our design: the office sends nothing clinical. Confirm that it's enough.)

**Until answered:** every signed partner gets `comp_structure = Pending Counsel Review`, and `comp_statement.py` pays $0 on that value. The agreement can be signed with compensation "per Schedule A, to be issued." Partners can start sending patients while the comp structure is still pending. Pay starts once counsel approves.

## B. Consumer-finance counsel: credit repair

1. **CROA** (15 U.S.C. §1679 et seq.): approve the disclosure statement, contract, cancellation form, and billing timing. Is our "after services performed" definition (per documented monthly round) defensible?
2. **TSR** (16 CFR 310.4(a)(2)): this is the one that can change the business model. For credit repair sold by telephone, the TSR bars taking payment until the promised time frame has passed **and** the client has a consumer report, issued **more than six months after** the results were achieved, that shows those results. That's far stricter than CROA's "after services performed." Many operators assume monthly-after-service billing is enough, and under the TSR it may not be. Questions:
   - Does the TSR's **face-to-face exemption** cover us if the enrollment consult happens in person? Does it cover a **video** consult? (Don't assume it does.)
   - Does the consumer-initiated-call exemption help? It generally **doesn't** for credit repair. Confirm.
   - If the TSR applies, what billing structure works? That answer sets pricing, cash flow, and the projections' `realization` and timing assumptions. **Get it answered before pricing is final.**
3. **State credit services organization laws:** registration, surety bond, and state-specific contract terms. Keyed to where the client lives. Get the approved-state list, the bond amounts, and the renewal dates. SC first.
4. Marketing claims: approve the exact phrasing of the partner script and patient messages (`templates/`). "Doesn't mean no" and "often fixable" are the edges.
5. Client authorization to share first name + "ready to reapply" (and, if wanted, full name on comp statements) with the referring office.
6. TCPA/state texting: approve the consent language and freeze it as `consent_language_version = v1`.

## C. Payment options: verify before you advertise anything

The user-preference rule applies here: **never advertise a payment option before the provider has formally accepted the company.**

| Option | What to verify | Practical read |
|---|---|---|
| **Stripe (GHL Payments default)** | Stripe's Restricted Businesses list. Credit repair has historically been listed as prohibited or restricted. | Assume **no** until Stripe confirms in writing. Don't take the first 40 enrollments through Stripe and hope. A frozen balance is the failure mode. |
| **High-risk merchant account** via **NMI** or **Authorize.net** gateway (both integrate with GHL) | Underwriting requires your CROA contract, disclosures, state registrations, refund policy, and chargeback history. Rolling reserve (often 5–10% held 90–180 days). All-in rates of roughly 3.5–5%+. | The realistic path. Start the application **now**: underwriting takes 2–4 weeks, and they'll ask for the counsel-approved contract. That's another reason to do B first. |
| **ACH** (via the same processor) | Same underwriting. Lower cost; returns (R01 insufficient funds) behave like failed payments. | A good second rail for clients whose cards fail. |
| **Affirm / Klarna / Afterpay / Sezzle (BNPL)** | Merchant acceptable-use policies. Credit repair is commonly excluded. Also, **these are credit decisions**: your clients were just declined for credit. | Unlikely to be accepted. Even if accepted, approval rates for this population would be low. Don't build around it. |
| **In-house installments** (the monthly-after-service schedule itself) | This is already an installment structure, because you bill as services are performed. Confirm with counsel that it isn't an extension of credit needing disclosures (it shouldn't be if no service is billed in advance). | **Your best "payment option."** It's accessible by design: $250/month, after the work, is the pitch. |

Payment-provider checklist, per provider:
- [ ] Written confirmation that credit repair / credit services is a permitted business
- [ ] Fees: rate, per-transaction, monthly, chargeback fee, reserve %
- [ ] Underwriting documents submitted
- [ ] Approval letter received **(only now is it mentioned on any page or script)**
- [ ] GHL integration tested with a live $1 charge and refund
