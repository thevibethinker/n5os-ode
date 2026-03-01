# Eliot Asenoth Gaspar-Finer x Vrijen Attawar

---
source: fireflies
date: 2026-02-20
participants: e.a.finer@gmail.com
duration: 0 minutes
---

## Summary

{'keywords': ['MacBook battery life', 'AI model training', 'Open-source AI models', 'Git and GitHub learning', 'Voice model creation', 'Resume generation'], 'action_items': '\n**Vrijen Attawar**\nContinue experimenting with AI voice model training to improve stylistic primitives and benchmark against Pangram (03:49)\nRefine the process of using AI to generate resumes for new jobs, focusing on selective import of relevant content (05:01)\n\n**Elie Finer**\nOptimize local open-source AI model deployments using current hardware setups, ensuring better performance and usability (02:58)\n', 'outline': None, 'shorthand_bullet': '💻 **MacBook Battery Life Discussion** (00:20 - 01:12)\nIssues with recent MacBook battery life discussed.\nComparison of M3 and M4 chips with M2 as the sweet spot for longevity and performance.\n🔗 **Supply Chain Challenges** (01:12 - 01:28)\nChallenges in compute hardware supply chains recognized.\nUpcoming Chinese suppliers entering the personal RAM market noted.\n🤖 **AI Interaction Evolution** (01:28 - 02:39)\nExplored evolution of AI interaction.\nImportance of structured prompts and technical setups for superior AI outputs discussed.\n🛠️ **AI Model Structuring** (02:39 - 02:52)\nNeed for frequent, sensible structuring when using AI models highlighted.\nBetter results achievable through structured approaches.\n⚙️ **Open-source AI Models** (02:52 - 03:49)\nExperience shared with running open-source AI models locally.\nHardware setup involving Nvidia Jetson and desktop GPUs noted.\n📚 **Learning Git and AI Training** (03:49 - 05:01)\nPersonal progress in learning Git, GitHub, and AI model training described.\nCreating voice libraries and stylistic primitives to surpass benchmarks like Pangram.\n📝 **Resume Generation with AI** (05:01 - 06:00)\nPractical applications of AI tools for generating tailored resumes discussed.\nEmphasis on selective data integration for relevance and simplicity.\n', 'overview': '- **AI Model Experimentation:** Elie runs the Quinn 3 model on a **3060 GPU**; better cards like the **50 series** could boost performance.  \n- **Voice Model Training:** Vrijen trains a Qin voice model on his own voice, aiming to outperform the Pangram model.  \n- **AI Interaction Insights:** AI output quality hinges on well-structured prompts and workflows, not just wording.  \n- **Battery Life Observations:** The **M4 chip** has poorer battery life than the **M2**, despite excellent performance.  \n- **RAM Supply Trends:** New Chinese suppliers may improve personal-use RAM availability, affecting future hardware sourcing.  \n- **AI Skills Development:** Users must learn to organize data and scripts, shifting from casual use to skilled operation.  \n- **AI in Job Applications:** A tool automates resume generation for new jobs, simplifying customization and improving efficiency.'}

## Transcript

Vrijen Attawar: Hello.
Vrijen Attawar: Hey.
Vrijen Attawar: Sorry.
Vrijen Attawar: You like my disappearing act?
Vrijen Attawar: I'm really good at it.
Elie Finer: I knew exactly what happened because I noticed the slow battery.
Elie Finer: We've all been there.
Vrijen Attawar: Yeah.
Vrijen Attawar: Yeah.
Vrijen Attawar: Oh, gosh.
Vrijen Attawar: You know, you're just going too hard and your laptop runs out of juice.
Vrijen Attawar: What are you gonna do?
Elie Finer: I don't know if you notice this, but I feel like.
Elie Finer: And I don't know what generation I could assume generically that you probably have a MacBook or.
Vrijen Attawar: Yep.
Vrijen Attawar: Yeah.
Elie Finer: Was it a really recent one?
Elie Finer: What generation?
Vrijen Attawar: Pretty recent.
Vrijen Attawar: Within the last year.
Vrijen Attawar: Yeah.
Elie Finer: Okay.
Elie Finer: I can't speak for the M3, but I feel like the M4 has a noticeably worse battery life than the M2.
Vrijen Attawar: Yeah, the M2 was sort of the sweet, sweet spot.
Vrijen Attawar: Right.
Vrijen Attawar: That lasted for days, I thought.
Elie Finer: Yeah.
Vrijen Attawar: And I was expecting a similar.
Vrijen Attawar: I was actually expecting a similar improvement on this one, which I bought within the last eight months and was, yeah, genuinely pretty disappointed.
Vrijen Attawar: But, you know, hey, at least it, like, flies with all the RAM that I'm like, chewing up.
Elie Finer: Yeah.
Elie Finer: I think we probably got them just in time before, like, you can't get them.
Elie Finer: Although I know the new Chinese suppliers will be spinning up for the personal use ram.
Elie Finer: I do know that.
Vrijen Attawar: Oh, my God, that's hilarious.
Vrijen Attawar: Well, you know, the funny thing is, like, with all these fucking compute wars, I don't know, I think that that same company I was talking about, Zoe, I'm so bullish on them because I do think they.
Vrijen Attawar: Long story short, as folks become native to AI, which is more than just I was raised by my mom's Claude Max subscription more so.
Vrijen Attawar: Right.
Vrijen Attawar: And it's more.
Vrijen Attawar: So do I have the technical primitives to instruct AI in a way that generates a superior output?
Vrijen Attawar: Right.
Vrijen Attawar: Because, you know, maybe two generations, three generations of state of the art models ago, prompting still had alpha.
Vrijen Attawar: And to the extent that prompting is still something that is alpha, sure, it matters what you say to the AI, but my, my observation has been it's more the structure, the structure of intelligence that you create within the machine and how you lay out the files and the scripts and all that, that can significantly affect or deteriorate performance.
Elie Finer: Absolutely.
Elie Finer: And with the models I've been using, it needs, they need.
Elie Finer: It needs to be directed towards sensible structure very relatively frequently.
Vrijen Attawar: Are you, Are you.
Vrijen Attawar: Are you messing with like the open source models or like running them on your own?
Elie Finer: Like, I have been looking into it because my friend does it, but he also has.
Elie Finer: My friend was really into it and he even bought like a.
Elie Finer: What is it, Jetson?
Elie Finer: The Nvidia, like computer that you can buy for it, right?
Vrijen Attawar: Yeah, I saw Jensen holding one the other day.
Elie Finer: Yeah, it didn't work out super well for him.
Elie Finer: I had limited, like I didn't really use it much, but I got like Quinn 3 running on my desktop PC that has like a 3060 in it.
Elie Finer: It's like something.
Elie Finer: Yeah, a 50 generation card would be better, but you know, work with what you can.
Elie Finer: But.
Elie Finer: And that is something that I have on my to do list is like getting that like more optimized.
Vrijen Attawar: Check this out.
Vrijen Attawar: So one of the reasons, and I use this as part of like the personal branding that I'm doing now was the pithy version of it is like you know, a year ago I couldn't tell you the difference between Git and GitHub, which is legitimately accurate.
Vrijen Attawar: And essentially since using Zoho, I was also last week screwing around with training a Qin model specifically on my voice over the course of the last few weeks.
Vrijen Attawar: One of many projects, but essentially created a voice library of what I would describe as like, like stylistic primitives.
Vrijen Attawar: And so I essentially want to beat Pangram and once I beat Pangram, then I want to figure out what's the cheapest model I can beat Pangram on.
Vrijen Attawar: And just like, you know, that feels like a underlying output that I have a good subjective measure of quality for.
Vrijen Attawar: As someone that's pretty good at writing and knows writing well.
Vrijen Attawar: Yeah, but it's still Terra nova enough for me to like learn a ton of shit about something I've never done before.
Vrijen Attawar: It's crazy what it lets you do nowadays.
Elie Finer: Yeah, definitely.
Vrijen Attawar: So what I was going to say was before I get too distracted.
Vrijen Attawar: So I'd shown you the place to generate the resumes.
Vrijen Attawar: I'd shown you that you can do that for every new job that you add.
Vrijen Attawar: And then I'd also shown you that you can of these things that you pick.
Vrijen Attawar: You don't have to go with everything.
Vrijen Attawar: You can basically just pull in the stuff that seems relevant, nice and easy.
Vrijen Attawar: You can sort of.