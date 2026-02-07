---
url: https://www.youtube.com/watch?v=Jcuig8vhmx4
---

# AI mistakes you're probably making

*Theo - t3․gg*

<iframe width="560" height="315" src="https://www.youtube.com/embed/Jcuig8vhmx4" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

## Transcript

[0:00](https://youtube.com/watch?v=Jcuig8vhmx4&t=0s)

I have a feeling I can guess what your stance is on AI right now. It seems pretty useful and especially helpful in small projects, side projects, and early stage startups. But when it comes to real problems in real code bases, these things just aren't that useful. And you don't understand why everybody's getting so hyped and excited about those things. If that's your perspective, I understand. There's a lot of reasons most people should feel that way, and I did myself just a few weeks ago. But the harsh reality is that things are changing, and I want to talk a bit about that. But more importantly, the mistakes that you might be making when you use these tools that result in the lackluster experience that you're having. This stuff has changed so much and my own understanding of how I use it has too. I keep seeing other people who are struggling and when I talk to them, I found this set of mistakes that almost all of them seem to be making that once corrected result in really, really good things being built using these tools. So whether you're a skeptic that doesn't see any value in these things yet, or you're somebody who's really deep in the weeds using them every day and you just want to double check you're not making obvious mistakes, hopefully this video

---

[1:00](https://youtube.com/watch?v=Jcuig8vhmx4&t=60s)

will be helpful. I have a ton of sources and things I want to talk about here, and I'm really excited to do all of that. But the first thing I want to tell you guys about is today's sponsor. It's 2026. Everything about how we code changed last year, yet nothing about how we hire did. That's kind of insane because hiring is worse than ever now that we're getting swarmed with terrible AI generated resumes constantly. If you're tired of reading that AI slop, check out G2I. These guys have it figured out. They have a network of over 8,000 engineers ready to go. And these aren't just people who are fresh out of college. These are experienced developers, many of which have worked at fang companies in the past. And they've all been onboarded with the best modern AI tools. So, you're not going to have to catch them up the whole time that they're employed. They even offer 7-day work trials to make sure that the employee that you get is a good fit for the company. Do you know how much easier my life would have been when I was doing job hunting if I could have tested a company for 7 days? I honestly think both sides benefit from this. Nobody wants to work somewhere that isn't a good fit. Nobody wants an employee that isn't either. It just makes sense to me. And if you don't think 7 days is a lot, I have good news for you. Their process

---

[2:01](https://youtube.com/watch?v=Jcuig8vhmx4&t=121s)

to get them to file their first PR from when you start can take as little as 7 days. After you sign up for G2I, you'll meet with their team. You'll set up a shared Slack channel, decide how often you want to meet in chat, and within five or less days from that point, you will have your first candidates, many of which are ready to go on the spot. And don't worry, you get to interview the candidates yourself, too. They do a first pass. They'll even take questions that you write for them to go ask the candidates and send you video responses so you can see how the candidate actually interacts. This is a person you're going to be employing. You want to know what they're like, not just what their credentials are on a piece of paper. It's 2026, guys. Stop hiring like it's 95. fix it now at soyv.link/2i. So the first thing I want to talk about, one of the biggest mistakes I see is selecting the right problem. So we start with I have a problem. Step one, you validate the problem. Is it really a problem? Maybe this is a thing I misunderstand or doesn't matter. But once you've decided that this is really a problem and it does matter, the next thing you probably do is the obvious solution, if there is one. If you're

---

[3:02](https://youtube.com/watch?v=Jcuig8vhmx4&t=182s)

looking at this problem and it's a space you understand and the solution seems obvious, you can go try that. But if that fails, you have to do the harder solution, which is something less obvious. Maybe you have to debug more to get more information. Maybe you have to think about it more, read more code, check more logs, find some way to reproduce it. You have to put more time in. But once that fails, you go to step four, which is try something new. This is the point where once your existing solutions, your existing way of doing things has failed you, you then go try something else to see if that will solve it. So let's say you have a database performance problem. Maybe when you do too much throughput on your database, people start having errors in their experience. First thing to do is make sure it's really a problem. Are the errors actually happening? Are they only happening when there is too much throughput? Are they happening for some other reason? Are they happening because the user has a weird extension or they shipped something wrong? Once you validate the problem, you look at the error. You see what line of code is on. And then you go make the obvious fix.

---

[4:04](https://youtube.com/watch?v=Jcuig8vhmx4&t=244s)

You ship it. Nothing changes. You never reproduce the issue because you couldn't figure out how to. So then you sit down, you put in the effort, you try to reproduce it. You think you find the repro for it. You ship some changes. You put it out. Still have the same issue. At this point, you've concluded this database I'm using just cannot handle the thing that I'm doing. So, you go explore new solutions. Maybe you look at a different database. You look at other technologies or systems or you try something else. Or maybe you ask the AI for help at that point. And this is a problem I see a lot. Most people don't try a new solution on a problem they already know how to solve. If you know how to solve the problem, you just solve it. You don't use another tool to try to solve it. And this is a very common mistake I see. People aren't using these tools to solve problems they already know and understand. They are using them as almost like a safety net type thing once everything else they've tried has failed. And that's often the first time they tried the thing. This is not meant to pick on Adam, but I think he's

---

[5:05](https://youtube.com/watch?v=Jcuig8vhmx4&t=305s)

actually a really good example of this particular problem here. Come on AI, give me that 10x power that I saw out of Davis 7. Ben Davis is my channel manager, also a fellow YouTuber, and is having a ton of fun building with all of these things. He wants to see how powerful this stuff can be. Here's the example he gave asking a question to Opus 4.5 in cursor. There's a hydration error in this app. I traced it to this file provider. TSX, can you help me find the problem? This is for a lot of different reasons the wrong way to use AI. And thankfully, I'm already seeing people in chat realizing they're doing the same thing. They aren't reaching for these tools to solve known problems more easily. They're reaching for them when they've exhausted the other things within reach and then they're giving the model something that's really, really hard or poorly understood enough to seem really, really hard. This is a really important thing I want to push. I talked about this a little bit in the you're falling behind video and I'm going to try to not let these things overlap too

---

[6:05](https://youtube.com/watch?v=Jcuig8vhmx4&t=365s)

much, but one of the best things to try these tools on is problems you already know how to solve because then you can compare your solution to the solution the tool would have done. If I know how I would fix this hydration error or this database error and I'm curious if the AI can do it too, start there. It's a great place to test these things out. Or another way of thinking about it, what context would you give another engineer on your team? When I am handing problems out to earlier career engineers at my businesses, I'm not giving them the problems that I don't understand. I'm giving them the problems that I already understand and know how to write the code for, knowing that if I give it to that employee, it's going to take longer and maybe come out worse and maybe have to do some back and forth with them to get it in the right shape. But I'm doing that knowingly to get it off my plate and to spread the knowledge of the codebase around the team. Learning how to do that with AI is a skill you'll pick up over time and you'll get an intuition not just of what problems the AI can solve, but also what things that

---

[7:07](https://youtube.com/watch?v=Jcuig8vhmx4&t=427s)

it needs to know it solved it right. And a fun thing you can do here is gify it a bit and automate it a bit. If you have a problem and you know how to solve it and you give it to the agent with the same information you have, like you saw a log that referenced a specific line of code that you're pretty sure is the problem because of this blog post you read. Give it all of that information, all the things that led you to the solution. Maybe just go through a PR where you fix something. Check out the commit before that fix. Hand all of what you knew to the agent and see if it can solve that. Chances are it will. And if it doesn't, you have a thing that is as good as gold. you have a reproducible test to see the capabilities of the model. If you have a pull request that fixes a problem that an agent was unable to fix, go grab the code state before you push that fix, freeze it somewhere, grab all of the information you need to solve it, put it in a markdown file in that place, and then every time a new AI tool comes out, throw it at that problem with that frozen state and see if it can solve

---

[8:09](https://youtube.com/watch?v=Jcuig8vhmx4&t=489s)

that. Those types of tests are gold because benchmarks suck. Now, and if you can collect a handful of these types of problems, the few things that the models can't do, but you could, you have a combination of things that's useful. You have a realworld reproduction test. You have the information needed to solve the problem and you have knowledge of what the right solution looks like and a way to validate the solution was correct. That is a hard combination of things to get and you should be hunting for as many of those as you can find because if you can sit on them and use them to run evals and you can tell your team or people on Twitter or the company that made the model, hey, this update made it so these five things that the AI couldn't do before, it can now. That is huge. And if you can sit there and say confidently, it can't solve any of these things, it still can't solve any of these things. That is even better. That is really useful. And if you can hit me up and share some of that with me, I will gladly pay you to have these reproductions that I can use to validate and test new things when they come out.

---

[9:09](https://youtube.com/watch?v=Jcuig8vhmx4&t=549s)

That is as good as gold. That said, what I think you'll discover when you do this is that when you have the right context and the right instructions and you had enough information to solve the problem, if you give the same exact information to the AI, it will solve the problem in roughly the exact same way. But that's just the top of it. That's just selecting the right problem. I was touching on context management a bit there. So I'm going to go deeper on this for the next piece. This is a project called repo mix. Its goal is to take a given codebase and flatten all of it into a single AI friendly file so that you could include it as contacts with chat bots. This project is a [ __ ] scourge and should be wiped off of the internet. Not only has this project personally cost me and T3 chat in the entrance we are running probably multiple hundreds of thousands of dollars, it also virtually guarantees you're going to get [ __ ] output. It turns out that AI shouldn't have access to your whole codebase at once in the context. I feel like I have to talk about this multiple times a day at this

---

[10:11](https://youtube.com/watch?v=Jcuig8vhmx4&t=611s)

point because it happens so often, but all AI is is autocomplete. If you hand it the capital of the US is and then stop, it is doing a bunch of crazy math across a bunch of things called parameters and those parameters linked some text to other text. When you have the early text of the capital of the US is it increases the likelihood that the next pointer is pointing towards Washington DC. The whole model that we use for LM is next token prediction. Based on everything currently in context, all of the information passed to the model. What does it think the next most likely 3 to six characters are? And it does that over and over again. The fact that these things can generate real meaningful contributions to real meaningful code bases that effectively through this autocomplete strategy is genuinely unbelievable and is an accident that it was discovered in the first place. But you have to be conscious of this when you use the tools. If you hand a model too much

---

[11:13](https://youtube.com/watch?v=Jcuig8vhmx4&t=673s)

context so that the majority of the context is just nonsense about your codebase, it's just going to generate more nonsense. Sure, there are some models that can handle way more tokens than others. Like Opus 4.5, I think is capped at 100, maybe 200k tokens, but Gemini can do 1 to2 million. We should just all use the models with higher context windows. No. No, we shouldn't. The more the model knows, the dumber it gets. The problem isn't that it needs to know everything. Because the more it knows, the less likely it is to autocomplete the solution. Because if the problem exists in the codebase, giving it the whole codebase does not give it the solution. And if you get to the context limits, even with something like opus, once you break 50k tokens of context, the model starts to perform worse. There is a very important concept of context rot which is when you have too much context and it is distracting you from the thing that matters. Just to visualize it, this is the average score that the models get for finding things

---

[12:13](https://youtube.com/watch?v=Jcuig8vhmx4&t=733s)

in a set of repeated words. And as you increase the number of tokens the model has, the success rates plummet fast. For example, sonnet 4. Up to a certain point, it's 100% successful. And then once you have too much context, it goes down to less than 60%. If the model has too much information, it will perform worse. Stop doing this. Imagine if in every Jira ticket or linear issue you got, the actual thing you cared about, like the problem the user had was stuck in the middle of paragraphs upon paragraphs of [ __ ] And you have to go deep into all of it to just find the actual problem. That's effectively what you're asking the AI to do when you compress the whole codebase in to the history. If you copy paste your codebase into a chat product like T3 chat or chatgbt or anything like that, it's going to confuse the hell out of it. It's not going to perform well. Don't do that. The reason all of these new tools like cloud code, open code, and even to

---

[13:15](https://youtube.com/watch?v=Jcuig8vhmx4&t=795s)

an extent things like cursor are doing so well at this is because they don't give the whole codebase to the model. They give the model tools to find what it's looking for in the codebase. Things like an agent MD or a claude MD file that briefly describes what exists where in the codebase. Things like a GP tool to find the specific line that matters so that it can address that and only pull in the section that matters instead of the whole codebase. Just imagine how you solve a problem. If you see some typo on a web page, you don't go read every line of the codebase trying to find the typo. you use GP or command shift F to find it in the codebase and then you go fix it. Models aren't that different from people. If you give it a search tool, it will use it. If you don't and you expect it to read every line of the codebase, you're just as bad as the junior engineer that would go and do that. People often ask, "How do you learn a codebase?" I tell them to go check the poll requests. Now, my thoughts are a little different. But you certainly shouldn't do it by reading through it file by file. You should do it by searching around the codebase, doing things in the app, trying to

---

[14:15](https://youtube.com/watch?v=Jcuig8vhmx4&t=855s)

figure out where the thing you're doing exists in the code. in building the mappings and the relationships between those things because you can't keep the whole codebase in your brain. Don't expect the model to do it. They don't work that way. So, we've established that giving it your whole codebase is bad. But what is good context? This is a more complex question that you'll get varying answers about. Generally speaking, less is best. If you can simply describe the thing that is wrong and what needs to be done, you can usually trust the model to go find what it needs to from there. This is actually one of the things that makes codeex slightly better than Opus right now with cloud code is that Codeex will do a very good job of reading all of the files that might be relevant, only pulling in the ones that matter, and then going and solving the problem. it is slower as a result because it'll spend a ton of time looking into each potential file that might be relevant, but once it does, it'll make a precise change with confidence. Whereas a model like Opus isn't quite as eager to search the

---

[15:16](https://youtube.com/watch?v=Jcuig8vhmx4&t=916s)

codebase and is more eager to change it. As soon as it finds something that it thinks is the problem, it immediately goes into editing mode. So with something like Opus, it is better to put a little more time up front to say the problem is here. Don't touch this. Don't touch that. Just solve here. This is also an important thing to do with your claude MD file or agent MG if you're doing other tools. I'm very thankful everyone else is following a standard and anthropic is just special snowflake. They are what they are. They'll never embrace standards that they didn't make. It's how they are. One of the most interesting things I learned about the Claude Code team is that whenever they notice the model doing something poorly in the Claude Code codebase, they immediately go and change the Claude MD file to help steer the model in the right direction. I actually just made some changes to the T3 chat codebase for the same reason. I noticed a couple mistakes that were happening as a result of this file not steering the model in the right direction. There are certain things that we do every day as devs that

---

[16:17](https://youtube.com/watch?v=Jcuig8vhmx4&t=977s)

the model probably shouldn't. One of the ones that pisses me off the most is PNPM dev. I don't want the model to run a dev server. I have a dev server running. I want the model to make changes to know that I have a dev server running and to just run a type check when it's done with its work. So I updated this file where I describe the PNPM scripts and specify now note don't use this unless otherwise told to. and all of a sudden the model randomly running dev commands stopped entirely. I also wanted it to be able to check the types from convex because if I wasn't running a dev server or it was running in a cloud environment where I didn't have the dev server running, it would make changes to the convex files and then not have the types update and then get really confused about the type errors. So I added another command here, pnpm generate, and told it generate convex types after schema changes. Now it knows when it makes a schema change, it should run this command and then the types will be correct again. Constantly changing this file based on the mistakes you see it making seems like you're babysitting the

---

[17:19](https://youtube.com/watch?v=Jcuig8vhmx4&t=1039s)

thing. It feels like you're doing way more work than you have to. I promise you it's not. This took 5 seconds and it's already saved me hours. And it also helps with building the intuition for what these can and can't do. Funny enough, when I was at Twitch, I experienced very similar things even though this was preai. When I onboarded into the codebase for the web app when we were rebuilding it in React, I was still learning React and TypeScript. I put up my first two PRs and had some dumb mistakes in them. Another engineer who was much more experienced hit me up and asked me, "Hey, not trying to pick on you or anything. Why did you do this though? Why did you write this this way?" So, I showed him the page in Twitch's docs that made me think incorrectly that I should do things a specific way. I don't remember what it was. I just remember this order of events. I linked him the docs page that led to me doing it this way. He said, "Oh, I see why it would make you think that. I'm going to go fix it." And before my PR even merged, they had updated the docs to make it less likely that the next person would make the mistakes I made. The issue with AI is that it doesn't remember things when it

---

[18:20](https://youtube.com/watch?v=Jcuig8vhmx4&t=1100s)

makes mistakes. That's your job. You have to build the memory for it. Not in the sense that you have to manage every single parameter inside of the model, but in the sense that when you notice it making stupid mistakes the way a new engineer might in your codebase, you need to document that so it's less likely to happen to the next person because the AI agent is a new engineer every time it runs. The role of this file is to take this really skilled engineer who just joined your company and make sure they know all of the things that are special about your company and your codebase. If you're copy pasting a cloudmd file from somebody else or some template repo somewhere, you're doing it wrong. Even if you're running the init command that a lot of these CLIs have, you're probably doing it wrong. The role of this file isn't to describe every single thing about the codebase. It's not just docs. It is specifically a gotchas pile almost like listing the things you've seen it do wrong to steer it away from that. This file should start really small and simple and slowly have small additions added and tuning done to it to

---

[19:21](https://youtube.com/watch?v=Jcuig8vhmx4&t=1161s)

steer the model away from the things you don't want it to do. And this file is always included as context. So it's basically guaranteeing that everything in it will or won't happen depending on how you describe it. So less code, more markdown. This is one of the most important pieces for the big code bases, too. By the way, if you're noticing problems with agents in really big code bases, the problem isn't the size of the codebase so much as the number of opinions and expectations that have been encoded. As a result, as the codebase gets bigger, the things that are weird about that codebase increase, too. Your expectations around how people operate in that codebase grow. So, you need to encode those. Another fun side effect of this is I've noticed when I look at a new codebase and I read through this cloud MD or agents MD file, I learn a lot about how the team builds and how they think about the codebase. It's actually a really useful way to learn. Honestly, context management is complex enough that I could do a whole series of videos on it. It's not complex in the sense that it's like super super hard to figure out. It's complex in the sense

---

[20:23](https://youtube.com/watch?v=Jcuig8vhmx4&t=1223s)

that there are many different solutions to the weird set of problems and you can for the most part ignore them and be fine. So don't overthink this one. Don't try to hack this one either. It's a common mistake. That's kind of that stupid repo mix thing I was sharing earlier. It's kind of the problem with things like this. It's trying to hack the context instead of use the context. And hacking the context doesn't work. Don't try to work around this reality. Try to embrace it. recognize the fact that these problems shouldn't require knowing everything about the codebase. Again, to go back to the selecting the right problem thing, if you had a really smart friend that you were giving access to this codebase, what information should they have in order to solve the problem that you're describing? Assuming they know nothing about the codebase, what is the smallest amount of info you can give them for them to meaningfully understand and solve the problem? That is what you should give to the agent. We'll probably talk a little more about context management in other pieces here and I might even do more videos about it in general in the future. But you have enough of an idea now about the common

---

[21:23](https://youtube.com/watch?v=Jcuig8vhmx4&t=1283s)

mistakes I see. Hopefully that'll help out enough that you can get more value from these tools. Speaking of which, one of the biggest problems I see using outdated tools or even worse holding your perspective based on experiences you had with outdated tools. Let's be real. If your perspective on how good AI is at coding is based on your experience using sonnet 3.5 in wind surf in the early days of agentic coding where you handed it the whole codebases context and didn't have a cloudmd or an agent md file to help it out. You're in a different world than us. That's legitimately like comparing notepad.exe to vim. Like the gap here is insane. To be fair to the people who feel this way, this is not just a cope. This is a learned behavior from a history of doing stuff with software and in the development world. If you tried adopting GraphQL right when it started getting hype and it went really poorly for you and then you tried again four years

---

[22:23](https://youtube.com/watch?v=Jcuig8vhmx4&t=1343s)

later, it didn't get much better. And that's the case a lot of the time. There are things that have a lot of hype that you go try, they just don't work well for you. then going back a few years later is very unlikely to change anything. That has been the case in the dev world for a while. If you tried React a couple months after it dropped and you just hated the syntax, the way it worked and no matter how hard you tried, you couldn't get over it, coming back a year later isn't going to be any better. Cuz like as much as React has changed, it hasn't changed in ways that would turn a skeptic into a supporter. It just improved in ways that take supporters and make them more powerful. So, if you used these tools two years ago and got nothing out of it and you've based your way of evaluating things on how you've evaluated them your whole lives, chances are this thing isn't going to be any better. I understand why you're avoiding it. Things are changing absurdly fast. I had problems that nothing in the AI world could solve 6 months ago that started being solved three months ago. Like, they went from, "Oh, haha, AI can never solve this," to,

---

[23:24](https://youtube.com/watch?v=Jcuig8vhmx4&t=1404s)

"Wait, what the fuck?" in literally a 3-month window. That is insane. This level of oh [ __ ] has not happened in the software dev world almost ever before where a thing could go from incapable of something to beyond capable at the exact same thing in months. So if you're not using the state-of-the-art stuff, you don't know where it is today. And I know a lot of you guys aren't using it because I've seen the numbers. Not the numbers of how much you're using certain models or how many tools you're using and when you use them. I'm just talking about my sub count. Did you know less than half of you guys are subscribed to my channel? How are you expecting to keep up on all of this [ __ ] I can barely do it and it's my job to. If you want good summaries of what's going on and what the hot [ __ ] is and what you can learn from it and whether or not to try it, hit that red button. It costs you nothing and it helps you a ton with keeping up. I guarantee you that that engineer on your team that is way ahead that is killing it with all these AI tools, they're probably subscribed and you're not. Fix it. Anyways, I could sit here and tell you what the hottest tools are right now, but I want this video to

---

[24:24](https://youtube.com/watch?v=Jcuig8vhmx4&t=1464s)

stay useful for a while, so I'm not going to do that. You can go check Twitter or you can go to my channel and sort by most recent and get a rough idea of what is good enough today. I will say chances are it's probably not co-pilot. And also important thing, if your company doesn't let you try the new cool hot things, this is harder to do. And I actually do empathize with that. If you applied to get co-pilot approved at the start of 2024 and it finally got approved halfway through 2025 and everybody's moved over to Cursor and Cloud Code and Codeex, you now have to wait a year and a half for it to be approved again. That sucks. There are reasons that you're on outdated tools that aren't your fault. And if that's the case, first off, I'm sorry. Second off, you should start ignoring those rules and doing it anyways. If you get fired, you have an awesome story. Ask forgiveness, not permission. And third, you can probably find a better company to do these things at because this stuff like like don't fall behind because your company doesn't let you try new things. And you'd also be amazed how many big

---

[25:24](https://youtube.com/watch?v=Jcuig8vhmx4&t=1524s)

companies are embracing this. There are medium-sized companies like Sentry that are big enough to buy Super Bowl ads that will let you bring in whatever tools you want. And then there are giant companies like Microsoft that will also do the same. I can't tell you how many of the startups I've invested in that have Microsoft as a customer because they're actually willing to try out these new tools. I think that's really cool, especially because they compete with a handful of them. But then there's places like Amazon where they are constantly being told they can't use these tools because they really want to make their crappy vibe coding, PRD building. I think it's called Kira is their VS Code fork. There are a lot of people at Amazon that are forced to use that and can't use better tools because Amazon really wants the information in order to make their tool better. So that sucks. And if you're in one of those boats, figure it out. I'm sorry. It sucks. I get it. But the fact that your company is forcing you to use worse tools does not mean the tools are useless. The ones you're using might be useless. And I know you guys don't know many people using Kira, but all the Kira users I know are my ex-coorkers that are still on Amazon and Twitch cuz they're all forced to use it. Yeah. So if

---

[26:26](https://youtube.com/watch?v=Jcuig8vhmx4&t=1586s)

they're skeptical of AI tools, I get it because Yeah. But you should find opportunities to try the best things. I am regularly amazed. Like when I started using Cloud Code with Opus, after using cursor with Opus, my brain just kept opening to the things you could do with it. Next common mistake, and I really hope people aren't making this, but honestly, I I know you are because I've seen it a whole bunch and I've made this mistake myself too in a handful of places. Broken environments. This one is so common. Good example here. I've been in code bases that are mono repos where if you open the repo at a root level in your editor, the type system breaks. you have to open the sub packages in order for the TS config to work. That's a broken environment. If I can't in the root of the project run a type check command and know that everything in the project is handled properly, your environment is broken. And this is a very common thing. I've seen this so many times. If your type check involves a CD, an actual directory change, your

---

[27:28](https://youtube.com/watch?v=Jcuig8vhmx4&t=1648s)

environment is broken. And you can go try to teach the agent about all of these things through the MD files through agent MD or cloud MD, but it's much better to just fix your [ __ ] environment. I just had this in a Vibe coding project. I was working in the Vibe canban codebase and they had a mistake in their ESLint config that meant that whenever you opened a file in the editor and you were in the root, not the subpackage, every single file wouldn't be type checked and threw an error on the first line because it expected you to be using it at the root. fix those things. Not just for the agents, but for your co-workers, too. If I open up your project in my codebase and I go to a file and it's getting a type error from main because your configuration is bad, fix it. A good rule of thumb here is if you have a good engineer that has never touched your codebase and you ask them to spin up on it and they run into these types of things, you shouldn't tell them why they're wrong or how to fix it. You should go fix the codebase so these don't happen at all. Especially because again these agents effectively have

---

[28:28](https://youtube.com/watch?v=Jcuig8vhmx4&t=1708s)

their memory wiped every time you run them again. So if you have this type of type error where every file has a bad eslint config every single time the agent runs it's going to see the error. It's going to try and fix the error. It's going to realize the error isn't because of their changes. And I can tell you how many times we've seen this. The agent finds the file that it needs to touch to fix the problem. It makes the changes. It fixes the problem. It verifies the fix. It runs the type check. It gets a type error. It freaks the [ __ ] out. It tries a billion random things to fix it. Eventually, it reverts the change. It sees the same error. It then says to itself, "Oh, I guess this error already existed and is unrelated to my changes. It reapplies the change and then it finally ships." And then you run the agent with a different problem and the exact same thing happens over and over and [ __ ] over. If you tell an AI agent about a ghost, it will chase it forever. You need to get rid of the ghosts. You need to get those skeletons out of the closet. And do you know what's really crazy? If you see these issues, you can tell the agent about

---

[29:30](https://youtube.com/watch?v=Jcuig8vhmx4&t=1770s)

them and it'll fix them really well. Do you know how I fixed the problem in the Vibe canband codebase? So my issue is when I went in a file, I had a type error. So what I did to solve this problem is I didn't feel like dealing with the TS config [ __ ] I literally clicked in cursor the little button that appears that says oneclick fix this error. Ask the agent to fix the error. I clicked that. It put this in the text here. For this code present, we get the following error. Parsing error. Cannot read the file tsconfig.json. Fix it. Verify. And then give a concise explanation. And it did it. It realized the problem is that the project expected the tsconfig to be at dot slash. So where we currently are, but it's a monor repo, so it doesn't actually exist there if you're using it at the top level. If I had opened my editor in the front-end folder, it would have been fine. But I opened my editor at the root, so it wasn't. So what we need to do is use the path helper to figure out where we are so we can actually link it correctly. And it did this with no issues in one shot. I then pushed it up, got it

---

[30:32](https://youtube.com/watch?v=Jcuig8vhmx4&t=1832s)

merged, and now the agents will behave better when they work in this codebase. So the very problem you are giving agents can actually be solved by those very same agents. You need to fix your environments. I I have played in far too many big code bases that have lots of problems like this. You can fix them yourself. You can fix them with an agent, but please [ __ ] fix them. The next time I see somebody who can't get AI to solve their problem because their environment is broken, I'm going to flip a [ __ ] Obviously, if you have type errors everywhere because you suck at setting up the environment, things are going to break. Fix it. Okay. The next mistake I see is actually one I'm scared about because I have a feeling this video might contribute to it. I almost want to put this earlier, but I'm going to put it here because this is where it starts to matter. MCP Helen over configuration. I cannot tell you how many times I have seen this. People spend so much time trying to set the agents up to succeed that they lose the plot. They bloat the context with dozens of MCP servers and then nothing works.

---

[31:33](https://youtube.com/watch?v=Jcuig8vhmx4&t=1893s)

As you know, I've been using Cloud Code a lot. Want to see all the MCP servers I have configured? Oh, literally none. Zero. Same deal with cursor. Same deal with every other tool I use. Stop loading up your agents with these useless [ __ ] things. Just don't. It's so common, too. I've seen this a ton. Chad immediately says, "Now, let's see your skill section." Okay, I have one skill. The front-end design skill. Do you know what the front-end design skill does? It is a single markdown file that tells the model to not make AI slop. It literally says exactly that. This skill guides creation of distinctive production grade front-end interfaces that avoid generic AI slop aesthetics. Implement real working code with exceptional attention to aesthetic detail and creative choices. Never use generic AI aesthetics like overused font families, clichéed color schemes, particularly purple gradients on white backgrounds. This is all that skill is. That's all I have for configuration in cloud code. I have a custom runner CC

---

[32:36](https://youtube.com/watch?v=Jcuig8vhmx4&t=1956s)

that is a oneline addition to my zish file that adds a specific environment variable in front to hide my email address and also appends the d-dangerously skip permissions. I am tempted to put a piece of advice that is always use mode and dangerously skip permissions, but you'll get there yourself. I don't need to tell you this. Stop adding all of this [ __ ] to your stuff, though. skills are literally just markdown files and they're often way longer than they should be. They are for the most part context bloat and context rot. Avoid them unless they solve very specific problems that you are specifically having after you've tried solving them other ways. And I've talked enough about why MCP servers suck. You should already understand that by now. If not, go watch my other videos. If you are skeptical of AI being useful in your day-to-day work and you are touching MCP at all, you are [ __ ] up. If you don't see the value in these things yet, don't configure [ __ ] Don't go into MCP. Don't add a whole bunch of skills. Don't add hundreds of rules to cursor. Make subtle adjustments to your cloud MD and your

---

[33:37](https://youtube.com/watch?v=Jcuig8vhmx4&t=2017s)

agent MD file. And try to give a bit more clarity in your prompt as you talk to the model. One more thing, and I feel bad calling this out cuz it seems like a pretty good and very well-intentioned project. Oh, my open code. This seems fine if you're already deep in open code, getting a lot of value from it, and you want to see what it looks like to thoroughly configure it. That's the point of oh my open code. But we're already seeing in chat, oh my open code is so bloated, slop. Yeah, it's a mixed bag at best. You don't solve problems with AI coding tools by adding more things to them. More features, more MCPs, more plugins, more skills, none of that's going to make you go from this thing is useless to this thing is useful. If anything, they're going to make it feel worse. I promise you if you take somebody who isn't sure about these tools and you clone them, you give one version of this person stock cla or codecs and tell them to solve problems, you give the other one a

---

[34:39](https://youtube.com/watch?v=Jcuig8vhmx4&t=2079s)

super customized oh my open code setup with all the fancy MCPS, all of the skills built in and everything, the person with stock codec is going to have a much better time and going to enjoy it a lot more. These things can be useful in small doses once you have specific problems that they solve, but nobody talking about them is there. Everybody talking about this [ __ ] is just AI maximalist trying to squeeze every single possible thing. It's the same people who would buy Android phones because they cared so much about every single line in the specs. I'm saying this cuz I was one of those people. I used to tell you very excitedly how many gigahertz were in my phone. I was so hyped when I got my first dual core phone back in the day. I don't even know how many [ __ ] cores my iPhone has. I have literally no idea. I know it's fast. I know the GPU is even faster, but I have no [ __ ] idea what the specs of this phone are. I have better [ __ ] to do, and you do, too. Stop adding all these [ __ ] tools. The tool maximalist people are the same ones who care too much about specs when your grandma's buying a computer. It's the exact same people. Ignore them and go get real work done. I feel like Pete comes up in

---

[35:40](https://youtube.com/watch?v=Jcuig8vhmx4&t=2140s)

almost all of my videos at this point, but there's a reason why. He is building an absurd amount of things in parallel, all for free and open source, because he's already made his money, and he's killing it. He's doing really, really cool [ __ ] And he's vibe coding almost all of it. And he's vibe coding so hard that he's putting out 500 plus commits a day regularly. So he must be maximizing all of this stuff, right? All the customization, all the MCPs, all the skills, all the things. He's probably running his own forked version of whatever. No. Ready to see what he uses? He uses stock codecs. Here is his config for codecs. Defaults to GBD 5.2 Codeex high. defaults to high reasoning, has a limit for how many tokens it can output, has a model autocompaction limit, and then in the features, ghost commits are off, unified exec is true, free form patch is true. It's just a tool they have for doing patching better. I think it's on by default now. Web search request is true because for whatever [ __ ] reason, the search tool for searching the web is off by default in

---

[36:41](https://youtube.com/watch?v=Jcuig8vhmx4&t=2201s)

codeex. This is like the only part in here that really matters. Skills is true cuz he's playing with skills. And then the shell snapshot is true. I don't even know what that does. This allows the model to read more in one go. The defaults are a bit small and can limit what it sees. It fails silently, which is painful and something they'll eventually fix. Also, web search is still not on by default. Yeah, the unified exec apparently replaces using T-mucks for handling execution. Not much, but like that's it. No crazy plugins, no crazy forks, no absurd orchestration stuff. Keep it simple. If the thing isn't useful in the simple form, it's not going to magically get useful by adding a bunch of [ __ ] Please stop. I actually really like this article he did called just talk to it. This is as people realize over time what they can do with these things. They start with please fix this and as they get more in they do crazy things. Eight agents running at the same time, complex orchestration with multiple checkouts, chaining agents together, custom sub agent workflows, libraries with tons of slash commands, full stack features being built in MCPs, all that [ __ ] And

---

[37:42](https://youtube.com/watch?v=Jcuig8vhmx4&t=2262s)

once you get through all that, you realize the best thing to do is just say, "Hey, look at these files." and then do this thing. Life is much better when you realize that's all you need. That said, even he admits he'll sometimes just take a screenshot of a thing that's wrong, paste it to the model, and say, "Fix this," and it will. Last important piece here, plan mode and iteration. A very common mistake I will see is someone asks the agent to do something, usually compounded with the other mistakes, like with a bunch of weird tools on, nowhere near enough context on the problem, and then it struggles. And rather than fix the context, they keep asking more things and adding on. They keep appending more stuff as the mistakes compound. And remember, this is all autocomplete. So if the history that it has is a bad instruction, incorrect implementation, and then a correct instruction, there is still more bad information than good. If the whole thing is autocomplete based on the history, having a bunch of bad things in the history is going to result in bad output. even put a good thing at

---

[38:44](https://youtube.com/watch?v=Jcuig8vhmx4&t=2324s)

the end. Obviously, it can work through this and there are plenty of examples of it doing it. But it is significantly better to not do this this way. When you notice that the output came out bad rather than try to fix it with a better input being appended, revert, go back, make the better input the start. Because if you have a better input as the start, the likelihood that the output is better too is much much higher. The more good context exists in your history, the more likely the next thing is good as well. Obviously, there's a limit here. If you have too much context, chances are the context has become less relevant, which makes it worse, which makes the output worse, too. Fix it. And you know what? One of the best ways to fix this is plan mode. Plan mode is great because instead of the bad input resulting in a bad output, the output will be a confused output. In fact, it'll be confused questions where instead of it doing a whole bunch of things it shouldn't, it will add a little bit of additional

---

[39:45](https://youtube.com/watch?v=Jcuig8vhmx4&t=2385s)

context. That is, hey, I'm not sure about these three or four things. Can you answer these questions for me? And you might realize, oh, I should have put that at the start. And you can kill it and restart if you want. Or you can answer the questions. Those answers to those questions result in better answers. And then the model can output a good plan. And now the majority of your context and the majority of your history is useful. So the likelihood that it builds something good is much higher. This is why plan mode is good. It gives the right relevant context instead of handing the model your whole codebase or a bunch of tools to find things in the codebase. The plan mode creates a perfect prompt almost. The goal of plan mode is to write the exact thing you want to hand to the model that it can then go use to solve the problem. But a really important piece here is what happens if it goes wrong. If you make this plan, you think it's good, you run it with the model and it comes out with a bad output. If it's just a few things

---

[40:46](https://youtube.com/watch?v=Jcuig8vhmx4&t=2446s)

that are wrong, sure, tell it that. Tell it to go fix those small things and it will. But if it gets the whole thing wrong, reflect on why. Read a little bit of what it did. Read the reasoning traces for why it made the change you don't like or the thing that you don't want. If it's something that was wrong with the plan, go fix the plan. If it's something that was wrong with the understanding of the code base, go fix your claw MD or your agent MD file. This is the delicate balancing act you have to do. And it's an intuition you build as you do it more. You'll write a plan, the model will start executing on it. You catch something it's doing wrong and you'll just know where to go to fix it. Just to go back to my example earlier in the T3 recheck codebase when I ran a plan and it got the code right, but then it ran a dev server and it couldn't verify things because the dev server went to the wrong port, caused errors, and broke [ __ ] I knew the solution wasn't to add to the plan. Don't run dev commands. I know that cuz I used to do that. Instead, I went and put it in the agent MD file and then cloned it as the cloud MD file and the problem disappeared. Figuring out where to put

---

[41:47](https://youtube.com/watch?v=Jcuig8vhmx4&t=2507s)

the thing to stop the bad behavior is an intuition you'll build and you'll build it way quicker than you think. The same way you build intuitions about how to use a tool, right? Like in React, you don't put hooks after an early return. You just get why after you use it for a bit. Those types of things are intuitions you build as you use the tools, but you have to build them, not just keep saying fix it over and over and over again. Generally speaking, if you're not oneshotting things often, that's because there are problems in your prompting, problems in your context management, problems in your agent MD and cloudmd files, problems in the environment you have given the model to solve things in. And as you catch mistakes on the other side, there are more solutions there, too. If you notice the model makes code that works, but the types are always erroring, go give it a command to check the types so that it knows they are good. A lot of things now have type-checking plugins built in with the LSPs. I've had mixed success with those personally, but giving it a type-checking command can solve almost all of these problems. Don't overengineer it. Just identify the common mistakes and fix those in the

---

[42:48](https://youtube.com/watch?v=Jcuig8vhmx4&t=2568s)

agent MD or in a given plan. If a mistake happens, don't tell it to correct it. Go back and adjust the plan and rerun it. So, to wrap things up, I want to go back to this tweet from Adam in the back and forth we had on it. He couldn't get it to solve this error. He had done a little bit of work. He found the file that it is likely coming from. He knew it was from this provider tsx file, but he couldn't figure out why. He also wasn't very clear in the ask. He had an ask mode and ask it if it could help him find the problem. It's not a big deal. Models can work through that type of thing, but being more concise and specific about what you want from it helps a lot. The bigger problem here though is that he didn't know what the problem was and hadn't found the right context for it. The feedback I gave was that he should copy paste the exact error. give it any useful context like does it happen to logged in or logged out users other information that could make it easier to root cause the bug also with a case like this because it's happening in the browser a tool that I can use to verify its fixes like playright or access to the browser directly can be really helpful I also

---

[43:50](https://youtube.com/watch?v=Jcuig8vhmx4&t=2630s)

specified put in less qualifiers instead of can you help me find it it's what is the cause of this error and if you think the model can fix it just skip straight to build mode turns out the reason that Adam couldn't do this is because he didn't know that there was an exact error. His immediate response was there is no exact error. Is there isn't the only framework that manages to actually give you a diff when the HTML is broken with a hydration error? And this is again to go back to the start why he was using the model. He was using a model to solve this problem because he had tried all of the other things he knew of and they didn't work. So he was using the model for the first time as a last fallback and that's not going to work great. If you're only using these models because you don't have enough information to solve the problem, you're not using them right. And what made this one really funny is that I effectively played the role of what the you wanted the model to do here. I told him that this was added in React 19 that you have traces that now show you in React where the hydration error occurs. Ah, I'm an idiot. The diff was right in front of my

---

[44:50](https://youtube.com/watch?v=Jcuig8vhmx4&t=2690s)

face. What's crazy though is that it appeared to understand perfectly what a hydration error is, but it diagnosed the cause wrongly, even absurdly. Almost exactly backwards. Yeah, because it didn't have enough context because you as well didn't have enough context. And once he found the right error and handed that to the model, sure as [ __ ] it could solve it perfectly. So again, if you apply the lessons from what I just explained here, you have to select the problem well. You have to not select a problem that you don't know how to solve. Ideally, you have to give the right context and find the context if it doesn't exist. Help the model work on it with you if it doesn't and you want to build it. He wasn't using outdated tools. All that stuff was fine. The environment was kind of broken in the sense that there was no way for it to know the right way. But if he was to go add everything, he would quickly end up in MCP hell. So finding the right balance here, a hard thing to do, but if you do it right, it's great. But with the right application of a handful of these tips, he would have had a much better time. And after that back and forth, he is now enjoying these tools

---

[45:50](https://youtube.com/watch?v=Jcuig8vhmx4&t=2750s)

much more. I hope I've done an okay job of explaining why I like these things and the mistakes that I've seen others having with them. And maybe, just maybe, you'll be a bit more of a vibe coder as a result. At the very least, you have a whole new set of things to flame me for in the comments. Let me know how you feel about this one. And until next time, peace nerds.