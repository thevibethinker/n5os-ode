Speaker 1 00:00:00
Okay, so means elephant in Japanese. I'm curious if that's where Zo came from.
Speaker 2 00:00:03
No, I believe they wanted to start with just the z or the zed and then someone was like that's a that's a SEO nightmare, There are other like logistical issues with like single single letter as they were like, okay Zo sounds cool Is sort of my understanding. Yeah So. This is Zo. In effect, the central space is very similar, right? ChatGPT. The difference is instead of projects, you have an actual file system. And you have to effectively give it rules for how to access this file system.
Speaker 2 00:00:39
So it starts completely bare. Like there's no files over here. There's no conversations over here. There's no schedule tasks over here, right? This is where the agents or the schedule tasks are. And then obviously, like I said, it's a literal computer in the cloud, right? So it has half a terabyte of online storage. It has memory, stuff like that. So this is all. And then these are all just like. connections that i've set up so that's the other cool thing you can literally plug into n8n and the.
Speaker 2 00:01:12
api and have your personal version of n8n onZo is the reason for this generally engineers or is that people who they're trying to make it for not got it they're explicitly trying to make it for non- engineers it is obviously way more powerful in an engineer's hand got it but it's primarily meant for non-engineers and it's primarily meant for folks to have their own sort of like have their own like mini projects indie hacking sort of like spend their whole life up around it right so.
Speaker 2 00:01:44
as an example let me get some water actually.
Speaker 2 00:04:53
It's the like, oh I have to like compose this email, I have to like put this in.
Speaker 1 00:04:59
That's why I'm so good at voice to text because I feel like if I can just start using voice to text. Oh yeah, sorry.
Speaker 2 00:05:07
Do you use dictation on your laptop. 
Speaker 1 00:05:09
I started using it now with Proplexity, but I don't really use it for other things.
Speaker 2 00:05:13
You should get a desktop dictation app. That makes a big difference. I got, so do you know Evry, the venture studio? Yeah, you know what you can do to break an Evry like legitimately you could do exactly this gap monologue.
Speaker 2 00:05:44
well okay i don't want to tell you like spend money to like get this job let me describe what i'm thinking yeah they have a dictation app called monologue they have a marketing slash content creation app called spiral they have an email app called quora wait they have like a whole ecosystem yeah so it's a venture studio they build these little apps i know the ceo or the the lead for monologue because i was user i was user six in their rankings at 1.4 actually uh so i i used it a bunch i switched this is Evry yeah this is Evry so i switched back to super whisper kind.
Speaker 2 00:06:19
of um but if you're looking for a job at Evry i know that the way that Evry works is they'll basically hire a talented person to spin up a product line but that person works relatively independently so i think the monologue guy is like totally solo and he takes he except he's got like no followers on linkedin he like accepts messages so if you like use it he'll definitely take feedback wow, yeah he's been pretty responsible yeah it's it's it there's their sweet is good so theoretically.
Speaker 2 00:06:50
like Quora you've got superhuman but you could save money on that if you like Quora enough because that's what people use it as is a superhuman replacement got it so you can use Quora for superhuman theoretically if you do a lot of content generation then spiral is quite good, like my approach for content generation which i'll show you in a second is decent yeah but um spiral is is just a very forgiving form factor okay yeah spiral is a more forgiving form factor it's more like this.
Speaker 2 00:07:32
Like it's a writing, AI writing partner for marketing. So the cool thing with Spiral is you can pull in all of your LinkedIn posts. Somehow they must have had an in at LinkedIn. So they...
Speaker 1 00:07:44
Oh, wow.
Speaker 2 00:07:45
Yeah, so Spiral...
Speaker 1 00:07:46
Because that's what they do. It's like basically posts on LinkedIn a lot more, but it's just like I feel like they don't have time.
Speaker 2 00:07:53
So I'll show you Spiral because that could be a... That's definitely, like, a specialized enough, yeah, I always write it first. Well, so that's, but that's a timestamp, right? So what I have set up is a system where I will just, like, voice record things. Let me, let me actually just show you Zoe first. So, okay, so essentially, this is, let's do an example, right? So let's do an easy example. Um, I want to write a LinkedIn post about some topic, but I want to, let's see if a.
Speaker 2 00:08:33
researcher was being a little buggy yesterday, but let's say, I want you to research current, trends in the hiring market for early career professionals, and then pull from my knowledge base and find any opinions that I have that are relevant or any aspects of career span that are relevant to this trend. And then produce a 500 word LinkedIn post in my voice. Okay, so let's see if she operates correctly.
Speaker 2 00:09:08
Okay, so I have it set to Sonnet, so you can adjust your models over here. You pay token rates like the same rates that they pay, so it's totally transparent pricing. You can adjust the models like reasoning level over here. So generally keeping it on medium or high. Medium for most things is fine. And then over here, it's currently showing this processing thing. If it stops doing this, it means it's hung, so you can tell it to resume. But essentially, this thing is indicating that it's processing.
Speaker 2 00:09:39
So you'll see how it's agentically going through everything. It's starting the Vibe Builder persona. Theoretically, it should have changed that along the way, but it will most likely change it to Vibe Rider before writing. So the reason I'm referring to these personas is because that's a change they made recently, and it's actually a pretty powerful change. You can set up these personas and have it switch between them. So it will like switch. between these on the fly. So I actually have situations where I will like.
Speaker 2 00:10:10
be building something and I'll say, okay, start with architect. That will help me plan everything out because it knows my file system. Then it'll switch to the builder persona, which is specialized in building within that environment. And then it'll switch to the debugging persona and like test everything. So it's like a very cool way of just like having, you know, team, like, you know, team member available to you. So that's a really cool functionality that no one else really does. And that's like a pretty, like, you know,
Speaker 2 00:10:43
from day one, you can start benefiting from that, because you can effectively do this thing where you have, let me show you, load up my voice system and all the files related to generating content or output on career span in my voice or on Zoho in my voice. Okay, so you can tell it to, like, load things up, and it will, like, think through its system and essentially, like, come up with stuff for you.
Speaker 2 00:11:13
So a lot of this, like, setting up of, like, the file system and whatnot, that's a pain in the ass, right? So that's what I've effectively handled is, like, setting up a base layer that has all of, you know, some of the basic commands, some of the basic things you can do. So you literally just learn through prompting it. So that's the cool part. I have looked at zero lines of code doing this. And just over the month, I've essentially just learned. Like, it's crazy.
Speaker 2 00:11:43
I went, you know, I was always, like, decently technical, but before using Zoho, I would look at code, and it would look like gibberish. And now I look at code, and it actually just does make a degree of sense. Like, you can see the patterns and the way it explains it. The other cool thing. So it uses any language. So because internally it's just a computer, right? So it can script in anything. I can set up databases. So I have a database set up for, let me show you, go-to-market database.
Speaker 2 00:12:22
Load the go-to-market intelligence database. So we'll load this in a second. Meanwhile, we'll come back to some of the other. Okay, so let's see how far. How far this has gotten. Okay, so it's figuring out. Let me search your knowledge base. Oh, it picked up my predictions file.
Speaker 2 00:12:53
So we'll see how that goes. So that was the best part because I've done the heavy lifting of setting up the ingestion systems, it should take you like minutes, literally, just like give it your content, and it will generate something for you. Because I did the heavy work of like the heavy lifting of like creating. So you'll see all these files, what I wanted to illustrate was load your voice system, there's an entire voice system built out with like, what's the prompt? What's the transformation system? What are the voice profiles look like? How do we route it from one place to another? Like you can build all but when I say build it, I meant I conceived of the system and then just described it. And the more technical you get, the better you'll be at describing the system. And then.
Speaker 2 00:13:43
you get that and then you get better workflows and blah, blah. So it's like a it's like a pretty cool learning process. If you're trying to get more technical, this is by far the best like forget about anything else. Like one cool example is, so for example, over, here, I can just tell it, switch to the vibe teacher persona and explain to me how the system works for a non-technical person that's trying to be an engineer. This is SuperWhisper.
Speaker 2 00:14:16
by the way. You should see it in a second.
Speaker 1 00:14:27
It's pretty much exclusively used for FlexBase, so it's interesting to see how other products, work, right? Yeah, exactly.
Speaker 2 00:14:34
What's going on here? Why has this gotten crazy all of a sudden? What's going on? Desktop version. Here you go. Okay. So, did I ask... Yes, okay, it's thinking oh.
Speaker 2 00:15:16
So because it's agentic it unfortunately just like it takes time for every single thing to get like checked, but the, Fun thing is that like it will show you sort of and you can actually learn along the way like oh What does a computer actually do right? It will like first seek out the file. It will like search Well, how's it gonna search? Oh uses grep search though Then you can like look at this stuff in context and then the cool thing is.
Speaker 2 00:15:47
Okay, that's loading in a second. I was briefly in McKinsey for like nine months but then before that just career coaching literally just yeah just like helping people get into college how people get into jobs. Like even after college? Yeah. Why? Ironically because I couldn't get a job so I went to Singapore to teach SAT and ACT yeah so I did that for like a year and a half and then gotten admissions and then did admissions and coaching. We've only had admissions before.
Speaker 1 00:16:18
Oh really? Yeah we used to work at, well I mean she's a dad. What's her name? um her name is um liz bass liz bass she works there now she worked in china for a long time do you know which company um i could find out and she could university oh she works oh she.
Speaker 2 00:16:32
works admissions at university okay so she's probably at like eln us or something or i, checked out what she's america if she's american she possibly yeah yeah she's got a private school in china for a while and then in singapore so uh oh cool i i actually would love to look her up in a second just to see what the the name game looks like okay so here's this database so for example like the idea of like setting up a database loading everything today is generally pretty intimidating right you're like oh how the hell am i even gonna set something like that up.
Speaker 2 00:17:08
with this i just instructed it hey set up this database and it's set up this database where i can, Capture go-to-market insights. So if I click into. So it will basically take my meetings it will access these b31 blocks which look like, this But these are essentially like meeting intelligence blocks so to take a step back the thing that I can set up for you today is.
Speaker 2 00:17:48
effectively a system that will, take your meetings, Where is it? records.
Speaker 1 00:17:58
Basically like all the follow-ups from the first meetings I do but also like when I meet people in person.
Speaker 2 00:18:05
sure so then you need a combination of this for in person so what my system is basically whether it's plod granola or fireflies yeah it all ends up here and once it ends up here and we'll actually i'll close this recording and actually show you in once we're done with this part but essentially we'll upload it it won't say zo processed i taught zo okay then the moment it gets in you ingest it you add it to a queue when it's in the queue you change this so there's this concept called like idempotency which is the idea that like it's like popping a air bubble right like once you or like.
Speaker 2 00:18:39
popping uh those little like like once you pop it it's popped right right so it's like once it's the kind of thing where you can press it a million times and it will still be in the same state so that's called idempotent so it's a good powerful design concept because essentially like you don't want it constantly processing the same transcript again right how do you spell that i-d-e-m, then potent so you learn these like cool concepts like these systems engineering concepts along the way so it's actually really gratifying using Zoho for that.
Speaker 2 00:19:11
reason but then just so you had said your main use cases are like hey I am getting overloaded with like intros right so the way that we would do that would be yes so it would be getting the system set up where for each email so let's say it was the I did a customer service right I'll show you I'll.
Speaker 2 00:19:47
actually show you what it generated for that call yeah okay so we have warm, intros oops did it right over your call show you this one so, So this is how it stores it right now, where it'll give you a detailed recap of the meeting, right? It'll identify what were the things we committed to. So I committed to connecting with her on LinkedIn. I shared the career span wait list. I said, hey, you can like invite me in the.
Speaker 2 00:20:17
future, blah. Then it had like, what were the questions raised and questions unanswered? I think it also captures so implicit unanswered questions. So this is all like a reflection of like, your, my cognitive style, you want to adapt this to your cognitive style, right? So you can actually tell it like, hey, I don't actually like block B07. This is block B07, right? Which says, what are the warm, what are the introductions that we committed to? Right? So like, it'll show.
Speaker 2 00:20:48
potential opportunities, it will show like, I don't know why it's including networking philosophies, but there we go. Oh, this is the principle disgust. Okay, so I bring that spiel up a lot. So you have something like that, and then the final step for that is actually, I was working on last night, was the follow-up email part, which I'll show you a...
Speaker 1 00:21:12
Have you heard of GoodWork. 
Speaker 2 00:21:16
GoodWork? It sounds familiar.
Speaker 1 00:21:17
Yeah, because I went to their launch party last week, and everybody on there is the most famous music connectors. Really? Yeah, everyone there was like... Jessie was there.
Speaker 2 00:21:28
I saw the GoodWork thing on Twitter or something.
Speaker 1 00:21:31
Yeah, and everybody who was there is posting about it, so it's like my entire feed is just about GoodWork, and I used to work with Caroline Dell, she's the founder.
Speaker 2 00:21:38
Oh, it's a cool...
Speaker 1 00:21:39
I mean, I can't show you what it looks like, but I mean, maybe after. But yeah, I'm not sure how to use it in a way. I know I need to meet with them and figure out how to use it, but I feel like... It could also help me with figuring out how to do it. What does it do? That's what I think I'm trying to figure out, because ideally it's supposed to be an alternative to LinkedIn. And it's really hard to know what the actual product is from their website.
Speaker 2 00:22:07
That's always so tough with these companies.
Speaker 1 00:22:09
But it basically just kind of goes through and just services people that it thinks that you want to meet. But then you're also supposed to feed it information, which is, again, what they haven't done yet.
Speaker 2 00:22:17
So that's the problem. The problem, that's the issue that every company runs up against in the AI world is, oh, we can process all of your data. Great. How do I get my data in there? Right? So that's the problem. And that's where my belief is that the ideal model will be one where you carry your data with you in this sort of vac-sealed container, and you plug it in selectively to different websites. So it's like a little balloon that goes with you, right? Yeah. that way your data is always like segmented away you know the other company only needs to know as.
Speaker 2 00:22:50
much as they need to in the moment to like service you but if you look at like this email that this does like this incorporates not only what was discussed in the meeting but also draws from the, profiles that have been created so i have a crm system here as well where hopefully whoops like this really doesn't come off as like written as ai at least not, That much not to the extent that you can fix it So that's where you want to tune it where you want to add like your voice when you adapt it to your.
Speaker 2 00:23:27
Particular tone and voice etc. That's when you want to like tune it essentially.
Speaker 1 00:23:31
And how do you tune it is it just by inputting more stuff or giving it examples and then letting it analyze itself. 
Speaker 2 00:23:38
Yeah, so you just let it like essentially so so what I'm trying to effectively figure out is Something where as little as like two lines of code and it will just like spin up on your laptop So I'm like 90% of the way there I wanted to essentially have that ready for Wednesday so I could distribute that to folks And that can be the like little lead magnet is like hey, there's a base system of like and five.
Speaker 1 00:24:05
Like, is it, like, VCs that are trying to use your product. 
Speaker 2 00:24:08
It's mostly founders and, like, AI Circle. And I think VCs that are looking for, like, personal productivity boost.
Speaker 1 00:24:14
And are they founders that are looking, like, for productivity tools, essentially? Or is that kind of...
Speaker 2 00:24:19
I think the theme is meant to be, like, founders that are generally dissatisfied with AI tools.
Speaker 1 00:24:24
Got it.
Speaker 2 00:24:25
And are, like, looking to a new way of, like, using tooling.
Speaker 1 00:24:30
Because I think when you talked to Ben, you could also mention doing, like, a virtual workshop for him.
Speaker 2 00:24:35
Yeah.
Speaker 1 00:24:35
Because I think that would be really good.
Speaker 2 00:24:37
That would be awesome. I mean, we would be so willing to do that. The Zoe folks would be happy to even sponsor that, I'm pretty sure. Because Nextplay would be a high-value community for them.
Speaker 1 00:24:48
Yeah. I think if you want to do an in-person event with Nextplay, there's a lot of New York people. I think that would probably need sponsorship. The virtual event you could do.
Speaker 2 00:24:56
Yeah, totally. And I think Zoee actually wants to...
Speaker 1 00:25:00
I mean, you know this, but they're very high quality people. Which is, I don't know, that's just impressive for a job. Yeah, Nextplay is really solid.
Speaker 2 00:25:09
Nextplay and FOHE are the two communities I'm in the most. Wait, which one? Future of Higher Education. Oh my god, my friend Finn is in that. Oh yeah? Yeah, FOHE's great. That's so crazy. You definitely should meet him.
Speaker 1 00:25:21
He just started a new job, but you should try to meet him. He would love this stuff.
Speaker 2 00:25:25
Yeah, yeah, yeah. See, here I am.
Speaker 1 00:25:28
I'm going to connect you with him. Am I going to do it?