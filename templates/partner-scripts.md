# Partner scripts

Every piece of copy that a partner will say or a patient will see gets counsel sign-off once (doc 12, B4). Placeholders are in `{{ }}` as GHL merge fields.

## 1. Kate's opener: rep-introduced office

> Hi {{contact.first_name}}, it's Kate with Elevated ID. {{rep name}} mentioned you'd be the right person. Quick question: when a patient gets declined for financing on a treatment plan, what happens to them today?

Then stop talking. Whatever she describes ("we try Sunbit," "they say they'll think about it") is your pitch, in her words.

> That's exactly who we work with. They're not a no, they're a not-yet. We work their credit with them and send them back to you ready to reapply. Can I show you how it works in 20 minutes this week?

## 2. Kate's opener: cold office (call, not text)

> Hi, this is Kate with Elevated ID. I work with dental offices on patients who get declined for financing. Who handles treatment plans and financing there? … Great, is {{name}} around for two minutes, or is there a better time?

The goal of the first call is a name and a time, not a pitch.

## 3. The decline-moment script (the card that goes on the desk)

> I'm sorry, it didn't go through today. That doesn't always mean no. Often something specific on your credit report is in the way. We work with a team that helps patients in exactly this spot. Scan this, or text **{{contact.partner_sms_keyword}}** to **{{location.phone}}**, and they'll reach out today. When you're ready, we'll run it again and get you started.

What the coordinator must **not** say: "they'll fix your credit," "you'll get approved," "it takes 30 days," or anything about cost. Train this explicitly. Coordinators want to be helpful and will promise things.

## 4. Kit email (sent by workflow `P3`)

**Subject:** Your Elevated ID referral kit: {{contact.dental_office}}

> {{contact.first_name}}, thanks for the time today. Everything's below. Nothing else to set up.
>
> **Your link:** {{contact.partner_referral_link}}
> **Text keyword:** patients text {{contact.partner_sms_keyword}} to {{location.phone}}
> **QR cards:** attached (print-ready). 50 more are on the way.
> **If the patient already left:** use this form and we'll call them: {{rep submit form link}}
> **The script:** attached as a one-page card. Keep it next to the financing screen.
>
> One rule: please don't send us anything about the patient's treatment or finances. Hand them the card and we'll take it from there with them directly.
>
> You'll get a text from us every time one of your patients reaches out, and a statement every month.
>
> Kate

## 5. Dormant re-engagement (workflow `P5`)

Day 0, call (Kate):
> Hi {{first_name}}, Kate from Elevated ID. Quick one: we just got a patient from an office near you back in the chair for an implant case they'd written off. Is {{coordinator}} still handling financing there? I'd love to show whoever's at that desk now how the cards work.

Day 7, email:
> **Subject:** One from last month
> A patient who was declined in {{month}} re-applied last week and was approved. {{office type}} in {{city}}. If someone new is at your front desk, I'm happy to do a 10-minute walk-through. Here's my calendar: {{training calendar link}}

## 6. Agreement nudge (workflow `P2`, day 2)

> Hi {{first_name}}, any questions on the agreement? Happy to walk through it in 5 minutes if that's easier than reading it.
