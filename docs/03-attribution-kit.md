# 03 — Give every partner an attribution asset

**Pipeline A → Pipeline B · Owner: Kate**

Attribution is what the whole referral network runs on. If a rep believes you undercount her, she stops sending, and she tells the other reps why.

## Partner ID convention

Format: `{REP}-{TYPE}-{NNN}`. Example: `CLRCH-DEN-014`.

| Part | Meaning | Rule |
|---|---|---|
| `CLRCH` | The rep's code (5 letters). | Assigned once per financing rep. |
| `DEN` | Partner type: `DEN` dental office, `REP` the rep herself, `STF` an individual staff member. | |
| `014` | Sequence within that rep. | Never reuse a number, even after a partner leaves. Old QR cards stay in drawers for years. |

Store it in `contact.partner_id` and also set `contact.parent_rep_id = CLRCH`. At 300 reps, the prefix lets the scorecard roll up by rep with one filter.

Uppercase only, no `O` next to `0`. Coordinators will read it aloud over the phone.

## The four paths (all carry the ID)

### 1. Unique link
`https://elevatedid.com/start?ref=CLRCH-DEN-014&src=link`

GHL-specific detail: URL pre-fill only works when the query parameter **matches the custom field's Query Key**. So:
- The form has a hidden field **Ref Capture** (`contact.ref_capture`). In Settings → Custom Fields → Ref Capture, set **Query Key = `ref`**.
- Hidden field **Ref Method Capture**, Query Key = `src`.
- The page at `elevatedid.com/start` has to be a GHL funnel page on a connected domain, with the form embedded **natively** (not in an iframe on another site). Iframes drop the query string unless you pass it through deliberately.

### 2. QR card
Same URL with `src=qr`. Print with the partner name on the card: "Dr. Patel's patients: scan here." A card with the office name on it gets handed out. A generic card gets tossed.

Generate the QR as SVG so print shops don't blur it. Test-scan every batch before it leaves the building. One bad print run is a month of zero attribution from that office.

### 3. SMS keyword
Patient texts `APPROVE14` to the GHL number.

How to build it:
- One workflow, **`B0 · SMS keyword intake`**, with one **Customer Replied** trigger per partner, filtered on "message contains APPROVE14". Each trigger path sets `contact.ref_capture` and `contact.ref_method_capture = sms_keyword`, then sends the intake link.
- Past about 50 partners this gets unwieldy. Switch to a single trigger on "contains APPROVE", then a webhook to a small function that parses the digits and sets the fields. `service/ghl.py` already has the calls.
- **A2P 10DLC:** your registered campaign has to describe this keyword opt-in flow and include the opt-in confirmation text, or carriers will filter your replies. The first reply must identify the business and include "Reply STOP to opt out."
- An inbound text is consent to **reply to that conversation**. It is not blanket consent for a marketing sequence. The reply sends the intake form, and the form captures real consent.

### 4. Fallback: "Which office sent you?"
Required dropdown on the public form (`contact.office_dropdown`), fed from the partner registry. Always include "My dental office isn't listed" (→ task to Kate) and "Not referred by an office" (→ organic).

The dropdown list goes stale the day you add a partner. Put "update form dropdown" in `P3` as a task step, not in anyone's memory.

### 5. Rep-submitted (the one learned the hard way)
The reality: a rep texts a patient from her own phone, "hey call this girl, she can help you." That patient shows up with no ID. You record them as organic, and three months later the rep is sure you're shortchanging her.

**`Rep Submit` form** (link in the kit): the rep's partner ID (pre-filled from her link), patient first name, patient phone, best time to call, and a **required checkbox**: "The patient asked me to share their name and number with Elevated ID." Tag `manual-rep-submit`, method `manual_rep_submit`.

What happens next is in doc 04. Short version: **a person calls; no automation texts** until the patient confirms consent themselves.

## First touch wins, and it's enforced

GHL forms **overwrite** contact fields on every submission. If a patient scans Office A's card on Monday and clicks Rep B's link on Thursday, `ref_capture` flips to Rep B. The fix:

- Forms only write `contact.ref_capture` (temporary).
- Intake workflow `B1` (doc 04): **If** `contact.ref_first_touch` is empty, copy `ref_capture` into `ref_first_touch` and onto the opportunity's `referral_partner_id`. **Else, if** it's different, add tag `attribution-conflict` and create a task for Kate.
- `ref_first_touch` never appears on any form.

The conflict rule to publish to partners before it ever comes up: **first attributed touch within 90 days owns the patient.** Kate decides edge cases, logs the reasoning in a contact note, and tells both parties the same day. A written rule nobody's seen is worse than none.

## Kit checklist (sent by `P3`)

- [ ] `partner_id` assigned and entered
- [ ] Link generated, stored in `contact.partner_referral_link`
- [ ] QR SVG and print-ready PDF (50 cards for the first order)
- [ ] SMS keyword assigned, stored in `contact.partner_sms_keyword`, trigger added to `B0`
- [ ] Office added to the fallback dropdown
- [ ] Rep-submit form link (pre-filled with their ID)
- [ ] Decline-moment script card (`templates/partner-scripts.md`)
- [ ] Test: Kate submits a test patient through the link, and the partner's card moves to Producing. Then delete the test contact and reset the partner's stage and count. **Every kit gets tested once.** A kit that fails silently looks exactly like a partner who never sends anyone.
