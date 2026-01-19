# Trio Standup

---
source: fireflies
date: 2026-01-16
participants: logan@theapply.ai,ilse@theapply.ai, logan@theapply.ai, ilse@theapply.ai
duration: 0 minutes
---

## Summary

{'keywords': ['Silent scans', 'Vibe check threshold', 'Auto-apply', 'Role publishing', 'Candidate notifications', 'Scan concurrency control'], 'action_items': '\n**Ilse Funkhouser**\nProvide a document with two tabs for AI overview and instructions (00:15)\nEnable role-based email additions and silent scans with auto-apply functionality (01:44)\nImplement and test safeguards preventing multiple simultaneous scans on the same role (03:42)\nShare examples of scans for user experimentation while advising on cost control (03:10)\n\n**Vrijen Attawar**\nReview the shared document and experiment with scan settings and thresholds as advised (00:41)\nProvide update on scan usage and feedback to Ilse the next day (05:12)\n', 'outline': None, 'shorthand_bullet': '📄 **Document Overview** (00:28 - 00:41)\nDiscussed careful management of credit access to avoid misuse in AI-driven candidate scans.\nExplained adding email addresses to roles to enable silent scans for basic candidate info collection.\n📊 **Vibe Check Thresholds** (01:44 - 03:09)\nClarified vibe check thresholds controlling candidate visibility and auto-application in the system.\nEnabled limits of 250 days on scans with no minimum story restrictions for user flexibility.\n⚠️ **Scan Limitations** (03:42 - 04:51)\nWarned about simultaneous scan attempts on the same role potentially causing failures.\nDescribed automated email notifications to candidates after scans with transparent and humorous messaging.\n🤖 **Automation Goals** (04:51 - 05:14)\nEmphasized the objective to reduce manual work and simplify candidate matching.\nConfirmed next update to be shared the following day.\n', 'overview': '- **AI-Driven Candidate Scanning**: New silent scan automates candidate applications based on vibe check, minimizing manual effort and maintaining privacy.  \n- **Access and Resource Control**: Role-based access prevents duplicate scans; CSV exports will be enriched later to improve data quality.  \n- **Cost Management Strategy**: Credit limit of 250 active scanning days set to control resource consumption and prevent budget overruns.  \n- **Positive User Experience**: Light, casual email tone to candidates mitigates concerns while maintaining a positive employer brand.  \n- **Testing and Improvements**: Silent scan system ready for testing; further enhancements planned based on user feedback and cost monitoring.  \n- **Feedback Loop Established**: Continuous progress tracking ensures alignment, issue resolution, and agile delivery of new features.'}

## Transcript

Vrijen Attawar: Howdy.
Vrijen Attawar: Howdy.
Ilse Funkhouser: Hello.
Vrijen Attawar: Hello.
Vrijen Attawar: How can I help?
Ilse Funkhouser: Okay, I gave you a document.
Ilse Funkhouser: I gave you a summary but short now.
Ilse Funkhouser: Yeah.
Ilse Funkhouser: So you can read the document.
Ilse Funkhouser: It has two tabs once for your AI.
Vrijen Attawar: Yep.
Ilse Funkhouser: Be careful.
Ilse Funkhouser: Do not give employer.
Ilse Funkhouser: Don't give people access without explaining to them.
Ilse Funkhouser: Don't give them too many credits.
Ilse Funkhouser: Because if.
Ilse Funkhouser: Yeah, don't give them too many credits.
Vrijen Attawar: Wow.
Ilse Funkhouser: You said when people can scan.
Ilse Funkhouser: Okay.
Ilse Funkhouser: So if you recall earlier when you're adding a role, you can add an email address here.
Ilse Funkhouser: I suggest people do that.
Ilse Funkhouser: Yeah.
Ilse Funkhouser: Because that's the.
Ilse Funkhouser: Currently, if you do a silent scan, the easiest way to get basic information about people.
Ilse Funkhouser: Once you do have that up though, whatever, I'll just use this one.
Ilse Funkhouser: The role needs to be published before this will work.
Ilse Funkhouser: You can click scan database.
Ilse Funkhouser: It will check to make sure you have access ahead of time.
Ilse Funkhouser: Public.
Ilse Funkhouser: You know what that means?
Ilse Funkhouser: That literally means if their vibe check threshold is above a certain level, we surface it to them.
Ilse Funkhouser: Oh no, sorry, I take that back.
Ilse Funkhouser: If it's public, if they're.
Ilse Funkhouser: If their full analysis is above a certain threshold, we expose it to them and we email them being like, hey, you should apply silent is.
Ilse Funkhouser: They never know about it.
Vrijen Attawar: Great.
Ilse Funkhouser: If you know the vibe check threshold, that is obviously if their vibe check is below that, we don't let them continue roll match.
Ilse Funkhouser: The same thing.
Ilse Funkhouser: I tried to throw in as much of the, of the old like preferences check stuff as well.
Ilse Funkhouser: I can make it stronger to save us more money.
Ilse Funkhouser: But it most important the thing is auto apply.
Ilse Funkhouser: If you have silent scan, it will auto apply.
Ilse Funkhouser: But you know the, the person will never know based on this threshold because there's no difference between they did a good note.
Ilse Funkhouser: It's just.
Ilse Funkhouser: You see it.
Ilse Funkhouser: So we just use that number auto apply.
Ilse Funkhouser: So obviously it doesn't work and yet it goes away.
Ilse Funkhouser: If it's a silent scan.
Ilse Funkhouser: You know what auto apply is.
Ilse Funkhouser: If it's above certain score, we still email them right now.
Ilse Funkhouser: It's still a pretty tongue in cheek email of like, hey, we let them know you're a really good fit.
Ilse Funkhouser: Don't worry about it.
Ilse Funkhouser: Like you know the fact that even if you're not interested, that's their problem now, not yours.
Ilse Funkhouser: I literally say that in that email.
Ilse Funkhouser: So bucket it.
Ilse Funkhouser: Minimum stories here.
Ilse Funkhouser: And technically I'm enabling no limit because I know you want it.
Ilse Funkhouser: There is a limit.
Ilse Funkhouser: I do have that limit set to like 250 days right now.
Ilse Funkhouser: Nice.
Vrijen Attawar: That's fine.
Ilse Funkhouser: The fact that I'm enabling this for.
Ilse Funkhouser: So that you can just give it to other if they're paying you.
Ilse Funkhouser: If they're paying you.
Ilse Funkhouser: I don't know where Logan is.
Ilse Funkhouser: Yeah but like you know but whatever you.
Ilse Funkhouser: You get the point.
Ilse Funkhouser: Yeah play around with it.
Ilse Funkhouser: I sent you some examples if and you can click start scan.
Ilse Funkhouser: I'm not going to because it's just needlessly expensive.
Ilse Funkhouser: Yeah and but then it will check and prevent you from running multiple scans for the same role.
Ilse Funkhouser: Nice Simultaneously Right now I don't have it set up where will it will fail in exotic and dumb ways if someone tries to create a scan for the same role so this is already done.
Ilse Funkhouser: I already created the scan and you can tell I had auto supply that literally says career span admin auto submission silent database scan.
Ilse Funkhouser: So they'll know you remind them in the email address you in the email you get of like hey this is a silent scan warning.
Ilse Funkhouser: They have not yet expressed interest.
Ilse Funkhouser: You're not going to be happy with the with the CSVs because right now it's literally just user email address and their scores.
Ilse Funkhouser: I know you want more bullshit in there.
Ilse Funkhouser: I haven't gotten to it yet because they do still get the email address if they were the email if they were good enough.
Ilse Funkhouser: That does include the bottom line in their score.
Ilse Funkhouser: Hey it's a strong move forward candidate if you can provide light onboarding.
Ilse Funkhouser: Blah blah blah.
Ilse Funkhouser: Who the cares you get it.
Ilse Funkhouser: I'm giving you what you need.
Ilse Funkhouser: We can obviously update the but the important thing here is now.
Ilse Funkhouser: You don't need to.
Ilse Funkhouser: I was going to say you don't need to bother me.
Ilse Funkhouser: That's not what I meant.
Vrijen Attawar: No no I know.
Vrijen Attawar: I also was going to say that that is exactly what we want is is like is to reduce that she is jumping on in a second.
Vrijen Attawar: Awesome dude.
Vrijen Attawar: Hell yeah.
Vrijen Attawar: Hell yeah.
Vrijen Attawar: This is.
Vrijen Attawar: This is rock and roll.
Ilse Funkhouser: I'm done.
Ilse Funkhouser: I have to go.
Ilse Funkhouser: I'm probably not going to be back today.
Ilse Funkhouser: Cool.
Vrijen Attawar: Have a good one.
Vrijen Attawar: We'll give you an update tomorrow.