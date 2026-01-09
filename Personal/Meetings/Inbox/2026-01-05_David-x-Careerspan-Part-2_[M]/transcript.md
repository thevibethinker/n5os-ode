# David x Careerspan

---
source: fireflies
date: 2026-01-05
participants: logan@theapply.ai,dspeigel@gmail.com,loganhc@gmail.com, logan@theapply.ai, dspeigel@gmail.com, loganhc@gmail.com
duration: 0 minutes
---

## Summary

{'keywords': ['Zoe AI', 'Fathom transcription', 'Claude code', 'API integration', 'Discord community', 'Career span processing'], 'action_items': '\n**Vrijen Attawar**\nContact Logan to confirm chat scheduling and follow-up logistics (00:38)\nSend David public repository with Zoe personas and basic file system setup to facilitate onboarding (15:30)\nCoordinate with David to schedule next conversation for further Zoe integration support (16:35)\n\n**David Speigel**\nJoin Zoe Discord community and troubleshoot account login to gain platform access (06:40)\nReview sent Zoe public repo personas and file system setup to get started with Zoe tooling (15:42)\nBegin integration project to connect Zoe with Fathom call recording transcripts using Google Flash model (15:57)\n', 'outline': None, 'shorthand_bullet': ' **Activated career span processing system covering broad strategy** (00:00 - 00:00)\n **Interest in VC and coordinating with Logan about chat timings; Logan permits past noon chat** (00:38 - 05:04)\n **David subscribed to Zoe ($9 plan) but not yet active on Discord or deeply exploring tool** (01:07 - 01:07)\n **Walkthrough of Fathom API/webhook integration to automate transcript aggregation** (01:55 - 01:55)\n **Live demo of Zoe platform, Claude code terminal agent for file system and task automation** (04:11 - 04:11)\n **David struggles with Discord login, resolves with downloading app and re-verification** (06:40 - 06:40)\n **Discussion on AI tool costs, credit system, and coverage of Gemini, Claude in Zoe subscription** (05:22 - 06:29)\n **Differentiation between Lovable low-code builder and Claude code terminal agent described** (09:33 - 11:10)\n **Demonstration of enabling Claude code to understand and operate on file system tasks** (11:10 - 15:30)\n **Plan to share public repo with personas and base Zoe file system for David’s onboarding** (15:30 - 15:30)\n **David commits to start Zoe/Fathom integration project using Google Flash model as baseline** (15:57 - 15:57)\n **Scheduled follow-up conversation and ongoing support planned** (16:35 - 16:39)\n', 'overview': '- **Call Transcript Automation:** Team decided to automate transcript aggregation to enhance workflow and reduce manual work.\n\n- **Fathom Integration Setup:** Quick implementation using API/webhook recommended to bypass manual copy, improving productivity.\n\n- **Zoe Subscription Details:** $9/month plan offers access to multiple AI engines with credit accumulation for compute resources.\n\n- **Onboarding Issues:** David faced challenges with Discord and Zoe login; team agreed to assist in troubleshooting and setup.\n\n- **Claude Code Capabilities:** Integrated AI agent in Zoe to assist coding and streamline development processes with local context.\n\n- **Next Steps Planned:** Commitments made for resource sharing, follow-up sessions, and collaboration on Fathom integration for efficient learning.'}

## Transcript

Vrijen Attawar: Record with extension.
David Speigel: Perfect.
Vrijen Attawar: Okay, so that's activating again.
Vrijen Attawar: Okay, cool.
Vrijen Attawar: So that will go.
Vrijen Attawar: And start processing.
Vrijen Attawar: I think that is like good because it covers a lot of career span.
Vrijen Attawar: I think we covered a lot of really good career span strategy.
Vrijen Attawar: And so I wanted my system to start processing that right away, which it will.
Vrijen Attawar: But yeah, I think that's.
Vrijen Attawar: That's roughly where we are.
Vrijen Attawar: So yeah, VCs would be of interest.
Vrijen Attawar: I have to jump.
Vrijen Attawar: Let me see if logs is up to chatting right now.
Vrijen Attawar: If not.
David Speigel: To.
Vrijen Attawar: Hit you up faster.
Vrijen Attawar: Think it can be.
Vrijen Attawar: If so, yeah, I'll get look at the option because I need to chat with her.
Vrijen Attawar: But yeah, that's that sort of career span.
Vrijen Attawar: Have you had a chance to check out Zo yet or play with it over the winter?
David Speigel: No, I didn't.
David Speigel: And so that's why I wanted to talk with you about.
David Speigel: I'm subscribed, so I have an account.
David Speigel: I'm on like the nine dollar plan or whatever.
Vrijen Attawar: Nice.
David Speigel: I have not yet joined the Discord, but like, let me go back to that.
Vrijen Attawar: Join the Discord.
Vrijen Attawar: Do you have a Discord account?
David Speigel: I think I. I think I did one, but not sure.
Vrijen Attawar: It's pretty easy to sign up.
Vrijen Attawar: And they let you make.
David Speigel: Yeah.
David Speigel: I wanted to get an idea from you.
David Speigel: Like just give me the highest level overview.
David Speigel: Like I understand what Zoe does because I've seen you use it, but that's like skipping some of the setup steps and some of the, like the how does it work in terms of what needs to be connected in terms of the AI tools and like your own personal tools.
Vrijen Attawar: So let me show you.
David Speigel: Give me like the high level piece there because like here's.
David Speigel: Here's a question that I have.
David Speigel: For example, I would like to do something similar to what you have with your call transcripts, like to leverage them better.
David Speigel: So for me, I have all my calls in Fathom, but Fathom doesn't even aggregate my calls.
David Speigel: And so then I have to like literally manually copy that.
David Speigel: I have to click into each call, go to the transcript, copy the whole transcript, paste it into a Google Doc, and then re upload that Google Doc to my custom GPT.
David Speigel: I want to end that.
Vrijen Attawar: Yeah, that's a horrendous process.
Vrijen Attawar: No, it's.
Vrijen Attawar: It's living like a savage.
Vrijen Attawar: So the way that I would recommend we avoid that is so with Fathom, I actually it was so easy.
Vrijen Attawar: I can literally show you the conversation because I've been like, I swear to God.
Vrijen Attawar: So caveat emptor.
Vrijen Attawar: This was, this was What I'm about to show you is specifically just the fathom part.
Vrijen Attawar: So it was not the.
Vrijen Attawar: It was not the all of the other infrastructure to process the meetings.
Vrijen Attawar: It was just the fathom part.
Vrijen Attawar: But admittedly just the fathom part was.
Vrijen Attawar: Hey, this is the API.
Vrijen Attawar: This is the documentation.
Vrijen Attawar: The webhook and webhooks.
Vrijen Attawar: The API and webhook secret have been added to the developer section which you can go to.
Vrijen Attawar: Where is the settings developers?
Vrijen Attawar: We go to the developer.
Vrijen Attawar: I just added it over here.
Vrijen Attawar: Right.
Vrijen Attawar: And then.
Vrijen Attawar: And then it just ran.
Vrijen Attawar: This was the Gemini.
Vrijen Attawar: This was Gemini Flash even.
Vrijen Attawar: This wasn't even with a particularly beefy model and it set up the service and then I had to like close the conversation.
Vrijen Attawar: I troubleshooted it a little bit.
Vrijen Attawar: Boom, done.
Vrijen Attawar: Right.
David Speigel: So got it.
Vrijen Attawar: The.
Vrijen Attawar: The actual.
Vrijen Attawar: The actual constraint is not getting anything done.
Vrijen Attawar: So what I'll show you instead is which will be easier to wrap your head around is.
Vrijen Attawar: Wait, close that.
David Speigel: Son of a. Fuck.
David Speigel: There we go.
Vrijen Attawar: Okay, here we are.
Vrijen Attawar: Okay, so here I'll go to Zo.
Vrijen Attawar: I got shafted from this page, but I suppose the head of design at Cursor is a little more.
David Speigel: Yeah.
Vrijen Attawar: To have than my ass.
Vrijen Attawar: Yeah, let's do this.
David Speigel: One.
Vrijen Attawar: Second.
David Speigel: Oh, just to keep you on task.
David Speigel: Did Logan get back to you?
David Speigel: Are we able to go over past noon?
Vrijen Attawar: Yes, good question.
David Speigel: She is.
Vrijen Attawar: She responded.
Vrijen Attawar: She is not.
Vrijen Attawar: So I think we can go over.
Vrijen Attawar: Sweet.
David Speigel: And let's just have this while you're signing into this.
David Speigel: So how many AI accounts do you have?
David Speigel: Like how many LLMs or other tools now?
Vrijen Attawar: I. I basically only have Zoe.
Vrijen Attawar: I don't even play pay for chat GPT.
David Speigel: But do you have to pay if you use like I pay $9 a month to Zoe.
David Speigel: Does that get me access to Gemini and Claude and Chat a by token.
Vrijen Attawar: So you, you basically.
Vrijen Attawar: I think I gave you the 50 off, right?
David Speigel: Yeah.
Vrijen Attawar: Yeah.
Vrijen Attawar: So that means that every dollar counts for $2, but you still have to put in money compute wise to run it.
Vrijen Attawar: So the subscription, you pay.
Vrijen Attawar: About half of what you pay in the subscription is just to run the service and the other half you get in the form of credits and do those carry over?
David Speigel: Because I've had Zoe for a couple months now.
David Speigel: I'd have done nothing.
Vrijen Attawar: See, they should.
Vrijen Attawar: I think they should.
David Speigel: How do you even see that to do?
Vrijen Attawar: You should have a billing section over there.
Vrijen Attawar: But if you dig into their.
Vrijen Attawar: Yeah.
Vrijen Attawar: If you go to the Discord and just ask.
Vrijen Attawar: I'm pretty sure I've seen folks ask that before.
Vrijen Attawar: And it's always seemingly been handled pretty.
Vrijen Attawar: I suspect that.
David Speigel: Let's just do this.
David Speigel: Let me see if I can get it.
David Speigel: I think I had Discord on my computer.
David Speigel: Maybe I got rid of it.
David Speigel: Discord.
Vrijen Attawar: You shouldn't need the thing either.
Vrijen Attawar: You should just be able to.
David Speigel: Well, I guess I. I had Discord and I probably took it off.
David Speigel: So maybe it's in my email then.
David Speigel: Give me a second.
David Speigel: Let's move this over here and go into.
David Speigel: I guess just search for an email that says Zo Discord.
David Speigel: Your computer is ready.
David Speigel: Links Velocity coding links here.
David Speigel: Your computer.
David Speigel: So I signed up on 1027.
David Speigel: Join the Discord community.
David Speigel: Here's the link to the Discord community.
David Speigel: Invite Zo computer.
Vrijen Attawar: All right.
David Speigel: Display name.
David Speigel: What should everybody call you?
David Speigel: I feel like I did this already.
David Speigel: Tool again.
David Speigel: Maybe that's dumb.
David Speigel: I don't know.
David Speigel: A thousand numbers.
David Speigel: Good morning.
Vrijen Attawar: How is this so bad?
Vrijen Attawar: 70.
David Speigel: Let's see if I did this already.
David Speigel: Wait, are you a human?
David Speigel: Please click on the shape indicated by the arrows.
David Speigel: This.
David Speigel: Right.
David Speigel: Verification required.
David Speigel: Need to confirm your identity.
David Speigel: Ensure you're not safe to care.
David Speigel: Please verify it or email.
David Speigel: Why do I have to put a password now?
David Speigel: Oops.
David Speigel: What just happened?
David Speigel: Maybe start over.
David Speigel: Thanks a lot.
Vrijen Attawar: Okay, signing back in.
Vrijen Attawar: Good, good, good.
Vrijen Attawar: Jesus Christ.
David Speigel: Take long.
Vrijen Attawar: Do I?
Vrijen Attawar: Don't.
Vrijen Attawar: Don't you?
David Speigel: Email is already registered.
David Speigel: Okay, if my email is already registered, then how do I just join this?
Vrijen Attawar: There we go.
Vrijen Attawar: Okay.
David Speigel: Accept invite.
David Speigel: You've been invited.
David Speigel: Accept invite.
David Speigel: Accepting unable to accept invite.
David Speigel: Okay.
Vrijen Attawar: Yeah, it seemingly adds up.
Vrijen Attawar: Mine has been.
Vrijen Attawar: My credits have been aggregating.
Vrijen Attawar: It seems like.
David Speigel: All right, maybe I just go to Discord and down.
David Speigel: Just download Discord.
David Speigel: Discord download.
David Speigel: Give me a second.
David Speigel: Discord download to Discord.
David Speigel: Mac.
Vrijen Attawar: Have you used cloud code at all?
David Speigel: I'm embarrassingly behind on using AI for coding and development, so that's one of my New Year's resolutions.
Vrijen Attawar: Fair enough.
David Speigel: This trying to download Discord.
David Speigel: Do you prefer Claude code over others?
David Speigel: Like, I've been hearing a lot of good things about Lovable in terms of like, building applications, I think.
Vrijen Attawar: I think they're pretty different use cases.
Vrijen Attawar: Like, Lovable is more of like a low code, no code sort of vibe.
Vrijen Attawar: Coding?
Vrijen Attawar: Yeah, I guess.
Vrijen Attawar: App website builder.
Vrijen Attawar: But.
Vrijen Attawar: We're comparing that with.
David Speigel: With Claude code code.
Vrijen Attawar: Claude code is more like a.
Vrijen Attawar: It's like if you could have an agent within the command line.
Vrijen Attawar: So it would be the equivalent of like, within the context of this local system.
Vrijen Attawar: Like over here in Terminal me, Claude code comes Pre installed on Zo.
Vrijen Attawar: So it would be like me.
Vrijen Attawar: Yeah, there you go.
Vrijen Attawar: See, that's Claude code.
David Speigel: Wait, I'm not seeing it.
David Speigel: I'm still on a different window rear in.
David Speigel: Zoe, I didn't see what you were.
Vrijen Attawar: The terminal at the bottom.
David Speigel: Oh, now I see it.
David Speigel: Okay, yeah, I see it.
Vrijen Attawar: Yes, this is Claude code at the bottom.
Vrijen Attawar: Right.
Vrijen Attawar: So if I told Claude code, I want you to grasp how this system works.
Vrijen Attawar: Review all key files and scripts and give me thorough sense of.
Vrijen Attawar: Oh, first.
Vrijen Attawar: Copy that.
Vrijen Attawar: As far as we gotta get.
Vrijen Attawar: Set the model.
Vrijen Attawar: No model.
David Speigel: Trying so hard to get in Discord.
David Speigel: Oh, verify login.
David Speigel: Come on, verify login.
David Speigel: Not here though.
Vrijen Attawar: Opus 4.5.
Vrijen Attawar: Okay, it's hit Opus 4.5.
Vrijen Attawar: So if I were to paste this and I were to say so this I can give you right away and it can help you start using Zoe.
Vrijen Attawar: So I want you grass.
Vrijen Attawar: Give me a thorough sense of how.
David Speigel: Okay, I'm somehow in Discord, but it's all blacked out.
David Speigel: That's weird.
David Speigel: Did I not.
David Speigel: Can I share my screen and show you what Discord is doing to me?
Vrijen Attawar: Sure, give me one second.
Vrijen Attawar: Just check this out.
Vrijen Attawar: By the way, you're familiar with the terminal, right?
Vrijen Attawar: And how the terminal works.
Vrijen Attawar: This is also of course.
Vrijen Attawar: Okay, so it's like having an agent in the context of the terminal.
Vrijen Attawar: So over here, the terminal that I'm running is running within the context of the Zoho file system, right?
David Speigel: Okay.
Vrijen Attawar: It's like doing terminal operations on Zo files.
Vrijen Attawar: Because Zo is not a project system.
Vrijen Attawar: It is an actual file system attached to an agent.
Vrijen Attawar: Right?
Vrijen Attawar: It's not a single chat with a project system.
Vrijen Attawar: It is a agent with a file system.
Vrijen Attawar: Right.
Vrijen Attawar: And so over here, what CLAUDE code does is Claude code is able to.
Vrijen Attawar: Okay, logs can jump on a second.
Vrijen Attawar: Solved it.
Vrijen Attawar: Now.
Vrijen Attawar: So you basically can allow CLAUDE code to do specific analyses or operations within the context of your system.
Vrijen Attawar: So it's like you can describe to Claude code what you want it to do.
Vrijen Attawar: And it actually.
Vrijen Attawar: What I realized only a few days ago is that Claude code actually has the infrastructure to do a lot of what I built myself natively just via Claude code, like the ability to plan or the ability to set specific rules for specific agents.
Vrijen Attawar: Like that's all stuff you can set set with Claude code.
Vrijen Attawar: So that's sort of the utility of using it.
Vrijen Attawar: But what I can do is I can give you access to this public repo.
Vrijen Attawar: And this is going to show you in a second what it is that you would receive.
Vrijen Attawar: So you would get.
Vrijen Attawar: And I can update this as well.
Vrijen Attawar: But if you're like just hankering to go, I can give you this file system and you can just set it up and run it.
Vrijen Attawar: But it is essentially a basic version of super basic version of my file system where it has like, you know, a set of Personas that you can add to Personas being over here that you can add to any system.
Vrijen Attawar: It will boot those up and it will give you a couple of really basic scripts and such.
Vrijen Attawar: Actually, no, this isn't even that.
Vrijen Attawar: This is.
Vrijen Attawar: This is just the.
Vrijen Attawar: This is just the Personas.
Vrijen Attawar: So I could send you that right away as a way of like getting started.
David Speigel: I am going.
Vrijen Attawar: Let me jump to logs.
Vrijen Attawar: But I'll.
Vrijen Attawar: I'll send you.
Vrijen Attawar: I'll send you two things that you can take a look at and they should be able to help you get started right away.
Vrijen Attawar: And I'm happy to jump on tomorrow as well and close the loop on this conversation.
David Speigel: Let's do that.
David Speigel: Because I'm now in the discord.
David Speigel: I'm going to log back into Zo and maybe like as a first like entry level thing for me to get my feet wet is like, let's just walk me through using ZO to like pull all my Fathom recordings just to do something.
Vrijen Attawar: What I would do is I would open up your zo.
Vrijen Attawar: I would use Google Flash because that's a pretty cheap model that runs really well and has good context window.
Vrijen Attawar: And I would literally just ask ZO how ZO works and try a couple of things.
Vrijen Attawar: Like I've basically told you that you can integrate Fathom using the documentation plus two keys, right?
Vrijen Attawar: So try to do that as a starting project using Flash and see how far it gets.
David Speigel: Yeah.
David Speigel: Okay.
David Speigel: Choose your theme.
David Speigel: I don't know.
Vrijen Attawar: I'm going logs.
Vrijen Attawar: But yeah, let's keep chatting and shoot me a message about good times for you tomorrow and we'll chat more.
David Speigel: Okay, sounds good.
David Speigel: Thank you.
David Speigel: And we'll continue tomorrow.