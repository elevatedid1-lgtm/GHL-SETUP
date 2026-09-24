# Patient messages

Tone rules: no exclamation points in the first message, no "Congratulations!", no urgency language ("limited spots"). This person is embarrassed and wary. Sound like a person, not a campaign. Every automated SMS is sent only when `sms_permission_status = granted` and `consent_confirmed_by_patient = Yes`.

## B2 · Speed to lead

**0 min SMS**
> Hi {{contact.first_name}}, it's {{user.first_name}} with Elevated ID. {{opportunity.referral_office}} said you might reach out. Sorry about today, it happens more than you'd think. Grab 15 minutes here and we'll look at what's in the way: {{custom_values.consult_booking_link}}. Reply STOP to opt out.

**0 min email**
> **Subject:** About today at {{office}}
>
> {{first_name}}, thanks for reaching out. Here's what the call is: 15 minutes, we pull your report together (it won't hurt your score), and you'll know exactly what's standing between you and an approval, and whether it's something we can help with. Some things we can, some we can't, and we'll tell you which.
> {{custom_values.consult_booking_link}}

**5 min SMS (no reply, not booked)**
> Just tried you. Here's the link again, or reply with a time that's good and I'll call then.

**Day 3 SMS**
> {{first_name}}, a lot of people put this off because they expect a lecture. It's not that. It's 15 minutes looking at the report together. {{custom_values.consult_booking_link}}

**Day 8 SMS (close)**
> I'll stop reaching out. If you want to look at it later, this link works any time: {{custom_values.consult_booking_link}}. Wishing you the best with the treatment.

## B3 · Booked

**Confirmation**
> You're set for {{appointment.start_time}}. Have the email from the lender handy if you got one, and 15 minutes somewhere you can talk. No judgment, we see this every day. Need to move it? {{reschedule link}}

**2 hours before (sent by hand by the consultant)**
> Looking forward to {{time}}. It's {{name}}, talk soon.

## B4 · No-show (+10 min)
> We missed you. No problem at all, life happens. Grab another time here: {{reschedule link}}

## R1 · Monthly update (example: month 1)
> {{first_name}}, your October update: we disputed {{n}} items with all three bureaus. Nothing back yet, which is normal. They have 30 days to respond. Round 2 goes out around {{date}}. If you get mail from a bureau, snap a photo and text it here.

## R4 · Score moved (increase or removal only)
> Good news: {{item or "your score"}} changed. You're at {{contact.current_score}} (started at {{contact.starting_credit_score}}). Target is {{contact.target_credit_score}}. Next round goes out {{date}}.

## L1 · Target reached
> {{first_name}}, you're at {{score}}. That's in the range {{lender}} usually approves. Want us to let {{office}} know you're ready to re-apply? Reply YES and we'll reach out to them.

## R3 · Failed payment
> Your card on file didn't go through for this month. Here's a secure link to update it: {{link}}. If a different day of the month works better, just reply and we'll move it.
