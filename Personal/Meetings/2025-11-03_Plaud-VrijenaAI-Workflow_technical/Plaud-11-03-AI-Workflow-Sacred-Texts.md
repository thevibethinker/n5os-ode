# Meeting Transcript

Source: Google Drive (ID: 1enL61sFkNRFLNOG4caw28PtUydLBSmAo)

Speaker 1 00:00:00
essentially have like inflows of data, right? Where you have stuff coming into your system and then you have places where it pools up. And when it pools up, it's generally bad, because then that's like tasks, like it's never just the data, right? It's always the data about tasks you have to do or about messaging that you have. So my philosophy is that we're still in a pre-AI world with storage and capture. What we actually need to optimize for is like, where is information pooling? Is it pooling in the right places?
Speaker 1 00:00:31
And like the stuff that's like runoff just needs like runoff, right? So the way this system is set up and the way I would recommend setting AI systems up is you have your sacred texts that are like the most up-to-date version of who you are. Right? And your sacred texts always have to be clean. They have to be high quality. Like you stand by every word in that section, kind of like quality. And then once you've done that, then you're ready to go. you can benefit from like AI stuff, right?
Speaker 1 00:01:06
Because then once it has that central understanding of who you are, it'll never come out as generic, because it knows enough about you to not be generic. So yeah, in this day and age, it's more about like, am I filtering the right data? Am I having it stream into the correct places? And then am I re-leveraging that correctly with AI. 
Speaker 2 00:01:29
because that's the thing is i feel like i do a lot of things manually and i'm like even my events database it's like so manual and i'm just like i know there's ai that could teach me but it's like in the moment this is what's useful it's like i'm spending time doing it because it is getting results in terms of like when i talk to people yeah tell me like that bootstrap problem is hard.
Speaker 1 00:01:50
which is exactly what i'm trying to solve for though is like can we give folks a like virgin flavored version of so that's like easier to use you know that's like just swap and swap out um and so that's effectively what i'm working on i think if i want to add the meeting stuff to it i might need a little bit more dev time but i'm effectively like i said by wednesday i'm going to have the link ready and i'm going to try to have it as simple as like you just need to paste in these two lines and it'll install everything so that's the level of simplicity i'm going for um.
Speaker 1 00:02:23
and then once that's done like you should be pretty well set up to use it.
Speaker 2 00:02:26
though on your own and is the idea to like use a first.
Speaker 1 00:02:29
specific purpose or to try to use it for like just to get people to a point where it's usable enough for them to do cool stuff on their own right because like like you said like yeah setting up a file system getting it to remember like when to delete when not to delete things like that's not worth your time right you can't afford to spend that much time like learning how for it to not fuck up your stuff yeah um so yeah that's it's on me um but because even if it just helped.
Speaker 2 00:02:58
me like where i could just figure out a way to like all the intros i gotta make like just taking that off my plate just the intro that would be because everyone called me a super connector should they expect me to connect them yeah and then it's like i tell people i'm going to connect them and then i like it just drops off my plate it's so hard but what you want is.
Speaker 1 00:03:13
effectively a system like this that every time you have a meeting or every time you upload a transcript it checks it it adds it to a queue a separate thing will look at that queue and say what's in the queue okay let me process this yeah right and that's where it processes it you, and then it leaves those five, is left over and then at that point you could design a third workflow that takes those blocks and does something with it which is where I would recommend like how blurbs and how that's the last bit of like blurb auto generation email auto generation that I'm working on but effectively.
Speaker 1 00:03:46
that will like just knock everything out so you can just go through your day and then at the end of the day you just have like all the things you agreed to that you can copy paste edit.
Speaker 2 00:03:56
it yeah yeah that'd be awesome yeah I know I'm just like I have anxiety about all the people that I promised stuff and then like I have such crippling anxiety about it and it's like slows.
Speaker 1 00:04:07
me down because eventually the anxiety becomes so crippling that I'm like not working right.
Speaker 2 00:04:12
it's like I feel like it's like that starfish thing where it's like the guy like it's just like throwing random starfish into the sea and it's like like certain people think that I'm amazing and then a lot of people think that I'm like not well it's a numbers game but.
Speaker 1 00:04:25
Believe me when I say this, everyone is struggling from it. We are all struggling with it, and we just are all silent about it because the expectation is that you're more productive in AI. So what kind of jackass is going to say they're less productive in the age of AI? So it's a collective silence thing where no one's willing to admit that they're actually less productive with AI. But that's because there's more information. It's not our fault. Now everyone has a taste of what it's like to be ADHD. So I wouldn't be too harsh on yourself about it.
Speaker 1 00:04:59
I would just say to yourself, okay, how do I develop a reliable system, to run that stuff? And I think even if Zo can't be it, there are a couple of really easy ways that you can even do something with chat PPT. For the longest time, what I did with Claude was I had... I'll just literally pick a track.
Speaker 2 00:05:22
Do you have an opportunity to follow them? Because I have one to Plexi, and I don't have anything to anybody.
Speaker 1 00:05:26
I have company access to Clod, but we'll probably get rid of Clod soon. Basically, ChatGPT has collapsed all of my chat, or Zo has collapsed all of my chat apps into just Zo, because it's the same quality model, right? And my system is better than the project system. So I actually don't need it, and it has great integrations. But what is an equally serviceable path for you is to do something like this, where you set up a project, right?
Speaker 1 00:05:56
And in the project files, you put these function files. I'm sorry, what's an example of a function file? Like this is a function file, right? A meeting intelligence orchestrator. So what you can do is you can say, you know, for this meeting, generate... thinking no style okay do that granola pardon me i do that in granola so with granola you would have.
Speaker 1 00:06:31
to set up granola to put things onto google drive using zapier oh god so that's a little annoying part about granola because granola's integrations um if you look at like their settings, their integrations yeah they don't have a google drive integration so you can i mean you could you could drop it into notion and then have it pull from notion but in my experience notion's kind of a finicky abi i haven't loved the notion experience that could be a zooside problem so.
Speaker 1 00:07:06
you know it could have just been resolved or something but essentially um. Oh, interesting. They have branching now. So what you do is you effectively put those files, which are basically just really intense prompts in the library. And then when you tell it, use the relevant function, it will follow that workflow. And it will like generate a follow up email at the end. So you can create an equivalent relevant function.
Speaker 1 00:07:46
So think about it this way, right? So pre AI, we used to create scripts, right? And we used to write scripts, and these different scripts would reference other scripts, and they reference libraries and shit. Basically, it was all like this coding language, right? Now words are code, right? Because an LLM can interpret them. So you can have, prompts, which are essentially a new, you can think of them as a new classification of script, right? It's a natural language script, right? It's something that a human can read and an AI can read, and it has instructions in it. So that's the distinction where like now you can you use a combination of prompts and scripts, because sometimes you need the AI to be deterministic, i.e., you know, mechanical operability, like zeros and ones, very like mechanical, but limited operations, or.
Speaker 1 00:08:42
you can use LLMs, which are fuzzy, but the same fuzziness that has the upside of flexibility has the downside of inconsistent output. So good design in this day and age is about how do I blend like the fuzzy bits with the deterministic bits to get something really consistent as the output, but that is flexible enough that it can absorb a variety of inputs, right? It can absorb your resume and my resume and process them to the same stack.
Speaker 1 00:09:12
Yeah, as opposed to like fucking up because yours is the wrong formatting to mine, you know, So you can see here it like goes through this workflow it says hey, which meetings do you want so I say. And then it will generate, So once I've picked out the meeting, so it's basically a long instruction.
Speaker 1 00:09:43
So when I say like function file, I basically just mean a prompt right instead of a what used to, Be a script is now just a write-up for the AI, So if you like if you once you like internalize couple these basic design patterns, it becomes like much more, Natural and intuitive and hopefully this is also connecting the things that you already know Because the whole goal is to make non-technical people like us like solidly technical right or at least like passively technical. Yeah.
Speaker 1 00:10:13
So you'll see here, this is like, pulling out the stuff from Notion, it's like, it has like a process, it identifies the stakeholder, I, one of my like things is I always have it ask me questions, which is another really good design pattern, so it like knows how many days late is this, how should we handle it, like, what's the primary goal of this? Um, which, which links do you want to include? Right? That was another drag for me. It's like, I'll have 15 links to put from 15 places. But now I just have a, I use tech expander for that. Oh, you do? I use Mackie, M-A-C-C-Y. So it's like good to, you can like bookmark links. And then you can also see like everything you've copy pasted recently. But even then, what's better, I would argue, is a system where you can.
Speaker 1 00:11:12
like, you can like, you, you have all of your essential links essentially like stored away right so it can like fetch from this file you see because i've organized it under preferences communications links, so that's what i mean by like creating your own file structure where i started with just like one prefs doc right i started with just like this prefs folder was just one document and then over time i've expanded it to include oh these are my communication style preferences is so it's like uh it's like a system that evolves with you that like as your needs evolve you can.
Speaker 2 00:11:45
like make it evolve you know that's so interesting yeah because taxi spender is like pre-ai so it's like not not that reliable right no well it's not adaptable like so for example like with taxi spender like if i just wanted to like if i wanted to send you my events database like i just hit the word there and then it just says like oh like here here's the link oh right if i wanted to send someone my um my notion page then i'm like oh here's the notion right right.
Speaker 1 00:12:14
How many blocks do you have saved like that. 
Speaker 2 00:12:18
So for example, I have this one where it's like, you know, someone just got added to Angel Squad.
Speaker 1 00:12:26
But it's not very flexible, right? Because you have to remember the same chunk every time. Or you have to... Have just the link and rewrite it.
Speaker 2 00:12:33
I mean, you could have things where, like, because, like, I just try to make it, like, this one has their name, like, the follow-up to this doesn't even have a name.
Speaker 1 00:12:38
Right.
Speaker 2 00:12:39
Because I'm doing, like, ten at a time.
Speaker 1 00:12:40
Right, right, right.
Speaker 2 00:12:41
So, like, if I even type someone's name, it, like, slows me down. It'll, like, fuck up. No, it just, like, slows me down. It's just, like, I have to remember their name and, like, put it in.
Speaker 1 00:12:48
Yeah.
Speaker 2 00:12:48
And it's, like, the first one had their name in it, so I'm, like, the second one doesn't have their name in it.
Speaker 1 00:12:51
I'm so familiar with that exact motion of, like, I need to copy something, but I can't copy the name because then I have to delete the name for every single thing. Exactly, so I don't have a name in it. So I just don't enter the name, but then it sounds too generic, and it's, like, it's a constant, like, struggle.
Speaker 2 00:13:04
Yeah. I mean, this is what I did all day when I worked at Chief in Class Pass. Yeah. I wrote all of these, and then everyone used the same ones.
Speaker 1 00:13:09
Yeah.
Speaker 2 00:13:10
That I wrote. Oh, my God. And then they were supposed to add their own flair to it, like, because I was, like, I wrote this, so, like, you spend one minute writing your own flair on it, you know? Exactly.
Speaker 1 00:13:18
But, like, what you ideally want is something that, like, in any given moment, if I were to say, like, uh... Like... Look up Pam Kavalum and write a email inviting her to this event. Use my voice and set maximum warmth settings.
Speaker 2 00:13:43
Oh my god, that sounds like her. Maximum warmth settings.
Speaker 1 00:13:49
Give me maximum warmth, dammit. This is freaking Luma.
Speaker 3 00:14:03
Yeah, so her name is Tia Gordon. I just thought of it.
Speaker 2 00:14:13
The one that I want to connect Amanda to.
Speaker 1 00:14:15
Oh, nice. Okay. Tia, name right. Let's see how it does this, right? So what you ideally need is something like this where it will look Pam up. It will define, okay, so it knows these are the steps that need to go through.
Speaker 2 00:14:37
Wow, it even spelled my name right. Like, it just heard you.
Speaker 1 00:14:41
the the super super wizard is pretty good for that so like so you'll see here i have a crm, that builds every time i meet you so like every single time we meet we will like this will like compound you know what i mean so like that's actually valuable where it just like by itself builds out this like intelligence right that's the thing that sucks is like for example i met.
Speaker 2 00:15:02
with this woman the other day we and she did not have any route collection that we've met four years ago yeah and i had a memory but it was like kind of a vague memory yeah but she had no she literally thought she was meeting me for the first time and we ended up talking for an hour and i was like you're gonna remember this next time i see you right she's like yeah and then she's already texted me yeah but it's just so funny it's it's our memory is fallible right.
Speaker 1 00:15:22
our memory is like really limited the woman like so she's using oh sweet yeah she was super cool.
Speaker 2 00:15:31
oh she has charlie i mean we have 80 people yeah jesus i mean can i remember where i met her i don't really remember but yeah her thing is called it's electric so she's.
Speaker 1 00:15:41
Oh, my God, Amanda would love to meet her. Yeah, that's so good. Which I will do. Yeah. Let me give this guy a little bit of a head start.
Speaker 3 00:16:30
Details.
Speaker 2 00:16:56
Is she out of town. 
Speaker 1 00:16:59
She is back soon. Yeah, she's back soon.
Speaker 2 00:17:03
It was on her message, but I won't expect it. Yeah. Maybe I'll say, like, no rush.
Speaker 1 00:17:10
Yeah. She should be working, so she'll probably respond. She'll see Tia, Tia's profile, and get super excited.
Speaker 2 00:17:17
Oh, okay, cool.
Speaker 1 00:17:19
Because that's right up her alley. So this is, like, like...
Speaker 2 00:17:34
Oh, is it in San Francisco. 
Speaker 1 00:17:36
This is in San Francisco, yeah. So it pulls the details, it gets everything, so it knows to reference the work you're doing in Dumbo. It's not perfect, it's not ideal, it needs to have details filled in. The last part of this, and partially why it's got rough edges, is I've been so busy building the systems as opposed to really living them out and using them. But I am excited to make that switch soon because I think I've finally built out enough that I can switch to more of a monthly company.
Speaker 2 00:18:08
For all the VCs you're meeting, is it a similar use case? Is it the follow-ups. 
Speaker 1 00:18:13
From what I'm hearing, it's follow-ups. It is, ingesting, large decks or large data dumps and processing them and organizing them. They want to do that in a place that doesn't just feed stuff to chat GPT, which protections on API, are a little bit better. They want something that is secure and only their eyes are on it and has all of their, proprietary intel on it and they don't want to spend any efforts setting it up, obviously.
Speaker 1 00:18:46
So that's where the last bit comes in where I do think if I have something that's genuinely very like, you know, Press, like, type in three lines, install, and then you're good to go. Like, I think that would sell like hotcakes.
Speaker 2 00:19:00
When you say type in three lines, like, what does it do. 
Speaker 1 00:19:02
Like, literally just, like, an instruction to GitHub to pull the repo, download it to your zoo, and, like, install it. That's, like, three lines. Okay. And in three lines, it will, like, do all of that automatically. And then you just have, like, a blank version of my system. Not exactly my system, but, like, a blank version of that shell that you can build off of. And you can personalize it.
Speaker 2 00:19:23
And then, yeah, and then in terms of the personalizing, like, what exactly do you have to do? Is it kind of more like giving instructions. 
Speaker 1 00:19:30
Up to you. If you can, you can tell it, hey, so I want to build a new workflow. I want to build a workflow where I record. messages after my networking night and like you turn them into recordings, and if you have it on like vibe architect it will like guide you okay this is where you put it this is where you so it's it's i've built that enough of the support stuff that it should be much easier for someone to do it right the other cool thing i wanted to show you was this which is always awesome was always fun is being able to show folks like so i told it hey switch the vibe.
Speaker 1 00:20:04
teacher persona explain to me how the system works for a non-technical engineer right the voice system so it does a pretty decent job right so it switches to teacher mode and then it explains, So this has been really powerful is I'll do something and then I'll have it explain what the hell is going on, right? And that will dramatically increase your like speed so it explains This is a script this scans this this explains this like it's so much easier Yeah If you just aren't able to just say hey switch to teacher and explain what you just did and how can are you using that. 
Speaker 2 00:20:36
Like do that every day like and like you're just kind of using it in between other stuff that you're working on. Yeah.
Speaker 1 00:20:42
Yeah, so I'll just now I'll just go through the day of meetings and I'll keep like 45 minutes at the end of the day Just like copy paste check verify send and then I just knock out everything in one go.
Speaker 2 00:20:53
And then in terms of like how you hate like have they make money like so right now very classic like not trying to make.
Speaker 1 00:21:00
Money in Silicon Valley, so they they essentially charge a monthly, Subscription, but you get the whole volume of the subscription and credits. So they're basically it's basically you pay what you spend Oh, they're making nothing in the middle interesting. Yeah, and there we see back up, VC backed. Lights feedback.
Speaker 2 00:21:17
Got it. Yeah. Oh, that's awesome.
Speaker 1 00:21:19
Yeah. I didn't even know that there were lights feedback. They're just casually dropping that. They're really good dudes.
Speaker 2 00:21:24
Yeah. That's the thing. It's so hard to get funded nowadays. By the way, are you guys VC backed yet? No. Are you trying to get VC backed? Are you trying to bootstrap. 
Speaker 1 00:21:34
I'm trying to bootstrap right now.
Speaker 2 00:21:35
Okay. Got it.
Speaker 1 00:21:35
Trying to more so focus on VCs as customers. Got it.
Speaker 2 00:21:39
Then you'll get customers through them with their full- Ideally.
Speaker 1 00:21:42
Yeah. Portcos. Yeah. Because their Portcos can hire stealthily. Their Portcos can hire en masse. We will go out and distribute it, and we'll distribute it to the best communities.
Speaker 2 00:21:52
Got it.
Speaker 1 00:21:52
So it's pretty decent. I don't know if Hustle Fund is looking for some type of support like that.
Speaker 2 00:21:56
Yeah. Because I was thinking it would be cool if I could try to get you a chat with Weil, who's the chief of staff, because he writes a lot on LinkedIn, and so does Brian, but Brian's really hard to get a meeting with, so he's Brian's chief of staff.
Speaker 1 00:22:12
Yeah. Hell would be great. Yeah. Hell would be great. Yeah. like we have a lot of well-formulated thoughts on hiring and i think i really think we've cracked it with the solution that we have you just give us a jd you give us a voice message the voice message is to describe the unrevealed preferences because you always have things that you don't want folks to know but you still want folks judged against yes we handle both we'll turn what you say into a rubric and we'll show you total transparency on how we're evaluating and then we go out and distribute the link even so you can have your main application system if you want.
Speaker 1 00:22:47
career span can just be an extra yeah and we just route folks to you right you know what maybe what.
Speaker 2 00:22:52
i'll do is i'll send you um the pitch with sarah and then if you don't mind maybe just like when you listen to it i think it'd just be good for you yeah of course yeah i trust you you could send me like two lines on like why you think the conversation with sarah would be useful for you yes because i think that would be more powerful than just me being like oh here intro you both, yeah yeah and then i think because like i know she's a tech crunch right now like she's like kind of famous right yeah, And, like, I really want her to be, like, super... Like, she is super pumped because I told her about you. But, like, I just think if she had, like, a hook of, like, why...
Speaker 1 00:23:23
Totally, totally.
Speaker 2 00:23:24
But I feel like I'm not able to...
Speaker 1 00:23:26
I can absolutely...
Speaker 2 00:23:27
Understand exactly. I know that you guys would get along really well. I just can't articulate it.
Speaker 1 00:23:31
I totally trust that.
Speaker 2 00:23:33
Yeah.
Speaker 1 00:23:33
It's a cool product, and I actually totally see the synergies. So I'm happy to get that over to you. Luckily, Plot's liking this, so I'll remember. Yeah, I'm happy to get you that. I'll spin this up, get you the thing, and then if you... I'll also send you something for...
Speaker 2 00:24:02
And then I'll also send you Ben's email, because I thought I had sent it to you, but...
Speaker 1 00:24:07
Ben's email would be great. I'll see you in the message so that he knows it was through you. And then I'll put forward something that's sort of intriguing or compelling.
Speaker 2 00:24:18
Yeah, but I think a webinar would be really good.
Speaker 1 00:24:21
Yeah, you got it, you got it. I'm so ready to talk about how Zouk can help professionals.
Speaker 2 00:24:28
But also I feel like just your thoughts on how AI works and stuff is really interesting, just like some of the stuff you were talking about with the polling or whatever. I just think in general, you're a thought leader in that kind of stuff. The way you're thinking about it is really interesting.
Speaker 1 00:24:42
Thank you. Yeah, I just need to put stuff out.
Speaker 2 00:24:46
It's so hard, because you're exactly the kind of founder people want. You're literally doing the work, but I also think you should be visible. People should hear from you, because, you are like, you're just really... good at talking about concepts that are really hard like hearing people talk about ai it's always the same thing and i feel like when you talk about ai you talk about it more in an nitty-gritty way that people don't really talk about people talk about it so high level and it's like i just walked away with not understanding people talk to hear themselves talk yeah but vcs just talk about ai.
Speaker 2 00:25:20
in just such a vague way and it's very like how am i going to make money from it yeah and it's just like so yeah i feel like it would be really helpful just uh yeah and i think you could i think if you just like got on a couple podcasts and then you get on more yeah hey hey if you could.
Speaker 1 00:25:35
recommend me to folks yeah i'm definitely trying to to get that sort of uh exposure and i'm i'm i think that's partially the reason i set this up for even the content reason was yeah now i will just like voice record something yeah and it will get turned into. It'll have the pipeline of reflection to identifying this is a thought leadership thing to generating not just one post but multiple different posts and then I can pick one. So it's fun. It's fun once you set all of this stuff up for you.
Speaker 1 00:26:08
You just think once and then let your thinking think for you. I think I have to dip in a second. Got to get mobile time for.
Speaker 2 00:26:26
And you still have an hour here, so if you want to do your call, unless it's going to go past.
Speaker 1 00:26:31
It's going to go past, and I have to...
Speaker 2 00:26:35
And you probably live a few minutes away from here, right. 
Speaker 1 00:26:37
I live super close.
Speaker 2 00:26:38
Okay, good. So I'm not going to do that at all. And when you do want to do your... I don't know if I sent you the link, but you should do a seven-day pass here. Yeah, how much is this for a month? So they have a bunch of different tiers. And actually, I'll walk you out, and then I'll show you where it is. So my tier is that I have four day passes in, and then a day pass here costs $28, so if I don't really feel like it, I could get another pass if I want. But then I also can go to unlimited events, so I can go to any event that I want. And they do a lot of events here. They do a lot. They probably do two or three events, but they also have a tribe back here.
