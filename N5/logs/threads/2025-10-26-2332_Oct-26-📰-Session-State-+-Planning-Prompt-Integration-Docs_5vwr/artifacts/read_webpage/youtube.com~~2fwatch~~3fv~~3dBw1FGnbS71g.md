# Velocity Coding (Oct 2025)

<iframe width="560" height="315" src="https://www.youtube.com/embed/Bw1FGnbS71g" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

## Transcript

[0:00](https://youtube.com/watch?v=Bw1FGnbS71g&t=0s)

Andre Karpathy like two years ago, year ago. Um but like the vibe of coding, we all know what it is, but um basically it's like a form of coding where like you don't look at the code, you just kind of like let it happen and you just trust the AI to do it the right way and you just like kind of get mad at the AI if it does anything wrong. Um and it's actually like surprisingly effective. Um but it's not the way that I code. Um I I like to call it velocity coding, not five coding. And it's it's really about using AI item to move faster, not not vibing. Um viving is like fun sometimes, but it's like not the path to success. Um it's probably obvious, but anyway. Um I have a real serious problem with AI. I I'm addicted to coding with AI. I spend way too much on it. Um this was kind of like my peak. I was spending like $6,000 a month. Um some of you probably been here. I've heard many horror stories. Um but but yeah, for like the first two months of working on Zo, I was spending about $6,000 a month, which is a lot. Still cheaper than a human, but it's

---

[1:00](https://youtube.com/watch?v=Bw1FGnbS71g&t=60s)

pretty expensive. Um and this is this is what it looked like. Um this was me. I I'm proudly the top contributor in our codebase. We have a whole team, but I I've written the most code. Um I've written half a million lines of code uh in just four or five short months. Um and and yeah, it's it's very real. I was averaging like 40,000 lines of code every week, which is abnormal. That's that's a lot more than I used to to write. Um, and it's real. Like you can see that my my week overw week contributions are like kind of around that amount. Um, very high. Uh, yeah. And and do I have any regrets about this? Sure. Like some of the good bad. Um, but that's just how it is when you're writing code. Like you start out and you're writing some stuff and some of it's bad. Um, and it was bad because I just like didn't think hard enough about those parts. Um, so nothing's really changed. I'm just writing more code. Um, yeah, let's pause a little bit here. Uh, just talk about like what that

---

[2:01](https://youtube.com/watch?v=Bw1FGnbS71g&t=121s)

code was like. Um, it was it was a real code. Uh, 500,000 lines of of like very real stuff. Um, we were building this thing called So Computer. You can try it out right now. Um, it's an AI cloud computer. Uh, so you can see kind of like looks like an IDE or something. Um, but you can work with like all kinds of files. I I like live coded this slide deck. Um, and it's just hosted on my server, but I do all sorts of other stuff in my Zo. Um, you can connect your Zo to like email and text and like Google Calendar. So, you can like talk to your computer in all these different ways. I text my computer all the time. It's really nice. It's like a friend who always texts back. Um, and you can like schedule different things. You can like create agents that kind of run like dams on your server. Um, this is an example of one that I run. Uh, it runs this command that I'll show you. Um, but basically it looks at my Twitter feed. Uh, oops, this one is empty. Anyway, um, it looks at my Twitter feed and it like downloads it into this database. Um, and

---

[3:04](https://youtube.com/watch?v=Bw1FGnbS71g&t=184s)

now I can like analyze my Twitter feed. So sometimes I just like I don't have to look at Twitter. I just ask my AI like what's what's on my feed. That's pretty nice. Um, you can like I've been reading Charlie Strauss's Accelerando. Um, really nice to like collaboratively read with AI. Um, yeah. Uh, you can work with all kinds of files, not just code. Um, yeah. Uh, anyway, this is not about Zo, but go try it out. Um, I have a QR code at the end of this talk. Um, and some credit cards. Anyway, um, that was just to show you that like we built a real thing here. Like it's a real computer in the cloud. like there's a lot of like kind of different kinds of code front end, back end and um that went into this and that's why like it was a lot of code actually was required. Um it wasn't just kind of slop code. Um anyway um so part one um I'm just going to kind of talk about my general principles first for kind of creating building anything and then I'll I'll get into like kind of how it works with AI. Um so I'm going to

---

[4:05](https://youtube.com/watch?v=Bw1FGnbS71g&t=245s)

start at like a super high level. when you're building something new, um it's all about these two things I think like simulation and leverage. So the simulation part is basically like how do you avoid actually doing the thing and just like simulate the different things that you could do. um this is like the best way to like really find yourself in the right kind of like direction in the initial phases and then after that it's all about kind of like finding different points of leverage so that you can kind of move faster or like you know expand your your perception or um so this just kind of a general practice when you are building or making anything I've been making stuff like since I was a kid like writing music and you know tinkering around on my computer and so so like these are just general rules Um, I'm always looking for like new ways to simulate and new kinds of leverage. Um, that's always been true. Um, and um, it's also important to think about like the things that slow you down, like kind of like the tiers of

---

[5:05](https://youtube.com/watch?v=Bw1FGnbS71g&t=305s)

things that slow you down. So like top tier is just like doing the wrong thing. Um, that's going to slow you down in a big way. Like wasted like you know three days doing the wrong thing. That's terrible. Um, the other way is like doing it the wrong way. that can kind of like bite you uh surprisingly like down the road and that that sucks as well. Really slows you down. Um and then you can like do it the right way. You like chose the right thing to do and you do it the right way, but you just like do it badly. That's also going to slow you down. Um because like you'll find that is like poorly implemented or like poorly executed like low scale. Um so these are just like general principles. Um and uh just over the last two years as a founder I've been like kind of building a lot of things. Um this was actually from 2023. Uh we were building a very different product. We're building an inference platform uh and kind of an agent framework. Um again I wrote like half a million lines of code all of it by hand. Um yeah it was very different different experience different process. Um and uh to do this I actually used some

---

[6:06](https://youtube.com/watch?v=Bw1FGnbS71g&t=366s)

old school code generation techniques. Um kind of from you know standard traditional programming uh which is just like you know making templates and like generating stuff. have a lot of SDKs in different languages. So naturally you try to like generate that code. Um and you might find that internally it's also useful to kind of generate code from like declarative templates. So this is like kind of like before LLM's like how we used to generate code. Um and still inspires me today. I still like use a fair amount of this this trick. Um this is what people call like metarogramming or macros or um it's a very good technique generally. Um and then um yeah fast forward this year kind of these AM models got really good um and I started using them to code basically entirely and um wrote half a million lines of code again uh and uh yeah very different form of code and this is what codegen looks like now in 2025 um it's these English documents that are still pretty technical um if you kind of I'll go into this in more detail later but um it's

---

[7:08](https://youtube.com/watch?v=Bw1FGnbS71g&t=428s)

code mixed with English And this is like mostly what I look look at now. Um, look at these plan files. Um, so I'll talk about this a lot more, but uh, yeah, kind of a hint of where I'm going. Um, I don't know why I have a slide here, but reminder to follow me on Twitter. I just I just hit 4,000 followers today. It's a it's a a celebration. Um, so yeah, please add to my follower account. Um, yeah. Cool. Um, yeah. Um, let's see. So, I'm still kind of at this high level. Um, and I thought it would be helpful to just like kind of talk about like the lessons I've learned from like 10 years of professional programming. Um, and how this apply today. So, um, this is Kent Beck. Kent Beck was this uh, he's still alive. Um, he's famous for kind of pioneering extreme programming and I think like some of the test driven development stuff. Um, wise man. Um and uh he he has this famous quote that's become kind of an adage among engineers uh which is

---

[8:09](https://youtube.com/watch?v=Bw1FGnbS71g&t=489s)

just to make it work and then make it bright and make it fast. So like poor thinkers you just make it work first. Like that's all that matters. Um you can't really do anything to it works and and you should not worry about like making it good or bright or fast until it just works. Um that that's just kind of like how you build stuff. There's many like different lenses and different quotes uh for for this like same same kind of idea. Um other ideas like kind of building the steel thread of like what you're trying to build. Um like the MVP the steel thread is kind of like an electrical engineering term. Um but basically like you just like get the minimal components that like kind of help you validate the entire system before you kind of like flush it out and and like keep working at it. So, um I think this this quote is is really relevant today because with AI you can just make a ton of it work really fast and then you can worry about like making it good or whatever. Um but uh it's really kind of amazing how much you can make work super fast now. Um yeah, so um coding has always been this

---

[9:12](https://youtube.com/watch?v=Bw1FGnbS71g&t=552s)

way and code coding well is always about kind of understanding that coding is a form of thinking. um when you're coding like the code itself is like kind of instrumental to like what you're actually doing which is like designing systems and putting stuff together and it's just a form of thinking um and so really like kind of build it well you just have to like get into this focused flow state so um I think it's really important to not forget about this when you're working with AI like the flow state and the thinking are are critical parts of of just working well with code um and it's really easy to kind of like get lost uh and to lose the flow state. Um so coding with AI is about leverage thinking. Um but this part is is interesting you know like AI is people have all discovered this in different ways but like it is this like amazing tool for leverage thinking. You can kind of think in these different ways you can like kind of have conversations with yourself. You can have conversations with codebase or with like the internet in this like very new way that's like

---

[10:14](https://youtube.com/watch?v=Bw1FGnbS71g&t=614s)

great for thinking. um this is like really high leveraged form of thinking when used well. Um and then you might find that like working with AI is really hard for the flow state. But I think if you like really practice and figure out how to do it well, you can actually increase your focus. Um and I'll get into that that a little bit more later. But um basically there's just one weird trick when you work with AI and it's it's that you can focus like your whole brain on the really important thing like the hardest problem that you want to solve. Um the thing that you really need to do right now and then you can maybe do like one other thing on the side in parallel. That's that's all it is. Um I think that that's basically my workflow. Um I'll talk about it more but um this is really all it is. um you can just like really focus on one thing, your human brain, like your whole human potential and your brain and then you can have like some other stuff going on on the side that can like kind of come back to and review later. So that's that's kind of like the whole whole

---

[11:16](https://youtube.com/watch?v=Bw1FGnbS71g&t=676s)

secret. Um uh I have this quote by Prep Victor which I I think is interesting and relevant to the flow state thing. Um so Prep Victor this talk inventing on principle is really good. You should watch it. It's on YouTube. Um but uh graphic's whole thing is that um creators need immediate feedback on what they're creating. They talk about this in all these different forms um including programming but also like other types of media but in a lot of mediums where you're like working with as a creator you don't get this immediate feedback. It's not like painting like you know put something on a on a canvas and it's like immediately there like it's it's very different from that when you're coding like you have an idea and it like takes so long to like kind of get feedback on it especially in the old days when you have like type every character that was crazy um but now you don't have to type every character and you can can get this like immediate feedback much faster. So there's something about AI coding that is actually really good for the flow state. Um, and it's important to like kind of stay aware of that. Uh, and like really try to increase it. Um, so, uh,

---

[12:18](https://youtube.com/watch?v=Bw1FGnbS71g&t=738s)

going to recap a little bit here. Um, so I talked about a few things in this this section. Um, so first make it work first. Just focus on making it work and then you can worry about making it good later. Um, and just take advantage of the fact that you can make a lot of it work really fast. Um, uh, always remember that like simulation is always better than actually doing the thing. So like in the context of coding it's like just like think about what the different options are maybe like spike them prototype um take advantage of the fact that like code is free now you like generate so much of it you like kind of try something feel it out throw it away and not worry about it um because it didn't take that long. Um, and uh, really try to like give yourself this like fast feedback loop because that's that's really what like kind of like gets you excited and like gets you into this like flow state and just gives you the energy to like kind of go really far. Um, yeah. Um, cool. So, in this next part, I'll talk more about my actual workflow. Um, and I'll try to leave a lot of time for questions. Um, but yeah. Um, so a lot of people have

---

[13:18](https://youtube.com/watch?v=Bw1FGnbS71g&t=798s)

arrived on this. Um, this is like kind of no secret. uh especially among kind of people who like do a lot of AI coding but um I'm basically going to talk about a form of spec driven development which you'll hear as a term nowadays. Um I I approach it in like a much more minimal way. Um I think it's good to keep things simple and like start from just like keep it grounded in like kind of first principles and just the basics of coding in general. Um so first I think then I plan and then execute. That's that's really all it is. Think, plan, execute. But I I'll talk about kind of why and and how that works for me personally. Um so um let's talk about thinking first. Um so uh how do you think more effectively with AI? How do you like leverage your thinking? Um uh so this this phase for me is all about kind of like researching like you know what I want to do um like simulating like what potential solutions might look like, imagining them, maybe like proposing some solutions, looking at them and just like yeah maybe I sit on it for a while. like don't actually tackle until like sleep on it. Um uh and yeah, leverage

---

[14:20](https://youtube.com/watch?v=Bw1FGnbS71g&t=860s)

the power of like just spiking stuff. Um you can like really like prototype something really quickly and just get a feel for it. Sometimes you don't really know how something will feel until like you have it and then you like try to change it. Um so I'll talk about feel a little bit later as well. Um and like what else does it mean to think in the context of coding? Um it's really just like kind of two main things. Um trap doors and trade-offs. Um so it's important to like kind of be aware of these two things. Um trap door decisions are things that like are hard to reverse. Um you know it's like you choose a certain framework or like you know you choose the technology. Uh there many many trap doors and some of them are like kind of hidden. So important just like make sure that you're in very intentionally making any trap door decisions when you're building something. Um and the trade-offs is just important to like kind of simulate like what the different options are. What are you trading off when you choose something? um that's how you can kind of like more intentionally move your code and your kind of project forward. Um and then yeah, it's always good to just sleep on big decisions um before you

---

[15:22](https://youtube.com/watch?v=Bw1FGnbS71g&t=922s)

make them. Um yeah. Okay. And then the next part is planning. Um planning is is how you do it. Um and again, I'm going to start kind of pretty high level here, but um it's really important um when you're kind of working with AI to to not lose the feel for your code. Uh I I kind of feel this very uh all the time now. Um as I'm coding where they like lost touch with the code. Um and keeping the craft high in in code is all about kind of feel. It's about having like like a very like kind of human like kind of visceral sense of like how your code feels to read, how it feels to change it, kind of like what parts are weird. Um I don't have words for like the weirdness usually. It's just kind of a feeling. Um and you only develop that if you're actually looking at the code. Um I don't know why this Christopher examiner quote is sorry this is maybe not intentional but um I do have this quote by Christopher Alexander. Um yeah right. Um basically like this is just

---

[16:24](https://youtube.com/watch?v=Bw1FGnbS71g&t=984s)

like kind of general uh knowledge from anybody who's built anything that like there's just stuff that like feels more right that feels more kind of like correct maybe a little more dense like semantically. Um And I think like over time as you like work with code uh you just develop a sense for like what is good and what's bad, what your own taste is. Um and that's just like important to keep an eye on. Um yeah, so I'll just like pass these. Um yeah, let's see. Um let me let me refresh this. I think I had some other content. Let's let's go back here. Uh sorry, we're bit of a right. Yeah, there we go. Okay, I think we're back in the latest version of this talk. Sorry, I was just working on it right before this. Um, cool. Yeah. Anyway, um, so, uh, the next phase is is planning. Um, I talk about planning, I guess, but, um, to plan something well, you have to like really own the planning process. Um, so you'll find that in in

---

[17:25](https://youtube.com/watch?v=Bw1FGnbS71g&t=1045s)

IE, um, a lot of them are trying to like build these like new planning UX things. Um, like cursor as a plan mode, kilo code as the plan, cloud code as plan mode. I I think like those are like kind of reasonable, but I don't think they're really necessary and I think they like kind of like remove you from the very important process of planning. Um like you don't want to outsource this planning process because the planning process is like what generates your whole codebase. Um like why would you well I personally I don't want to do that. Like I I want to own the plan uh and the whole process that creates the plan. Um and I really obsess over the plan. Um because like I'm not spending time writing code anymore. I'm spending time like planning. So that process is like very important. Um I don't want to just like delegate the whole thing to AI. Like it's definitely not at that level where it's going to be good if I do that. So if own some part of the coding process and the planning process is like the part to own these days. Um so um how do I plan kind of intentionally? Um it's all the same things I've been talking about. Um but

---

[18:26](https://youtube.com/watch?v=Bw1FGnbS71g&t=1106s)

basically you just like you create this plan and then you just like keep iterating on it. like you don't settle for like the first thing that comes out of like the AI's mouth. Like that that's going to be bad. Um you have to read it, you have to think about it, like sit on it. Um you have to try your options. Um and and just like really obsess. Sometimes I'll spend like, you know, 30 minutes or like an hour just like writing a good plan. Um and and that's that's really kind of like the the core of high quality planning. Um the the planning prompt itself um is it is like something that you can just make. Um I I don't I'll share like some some versions of what we have later after this talk but um yeah you know um you should just experiment with like applying a prop that works for you. Uh like think about the document that you want at the end and and like kind of guide the AI to like generate that basically and like insert whatever you want. Um this is just kind of like the structure of of some of our planning prompt which is like you know describe the code changes be concise um kind of highlight at the top like kind of what's going on and like go into more details.

---

[19:26](https://youtube.com/watch?v=Bw1FGnbS71g&t=1166s)

Um, so there's like a particular way that I like to see these plans and I'll kind of like show you what it looks like in practice at the end. But, um, yeah, that's me. Um, I also have some weird stuff in our plan. Um, so, uh, planning is or prompting is just this kind of like weird dark art. Um, and some stuff like just I don't know if it works, but I think it does. Um, and I think it like changes as models change. Um, but uh sometimes like the right prompts will like kind of get your AI to like I don't know like talk back to you or like criticize you more or like go deeper. So like I describe things. Um this is one example of like something in our in our plan prompt. Um uh we have a lot of stuff in our plan prompt. Um we have like quotes from Rich Hickey and Christopher Alexander. Um and it's kind of like the religious text. It's like the Bible of our codebase. Um and it's the thing that is kind of generating all the code. Um so it's very important like you know obsess over it keep parts of the secrets like a secret recipe. Um I think it's very important because it's like the main thing that is like part of

---

[20:28](https://youtube.com/watch?v=Bw1FGnbS71g&t=1228s)

the creation process. Um so yeah you think about the planning prompts and the rules that you set up. Um so like there's this prompt that generates a plan and there's like other rules like cursor rules or whatever rules you use cloud MD files that are kind of like the seed um of your code. And then like you go from this planning prompt um to this plan and then the code. So like all of this is like kind of the origin of your codebase. So it's I keep repeating myself but it's very important. Um just own this part of of it and experiment with it. I think like this is how you kind of arrive at kind of code that like is in your style and like feels like you and like feels like an extension of yourself. Um if you like really kind of own it. Um yeah. Um this slide isn't complete but um you should use good models. Um so the other part of kind of what generates your code is the model itself and different models have different styles. Um so like part of it is kind of like tweaking the plan and part of it is just like trying out different models and and just using the best ones like best in in your

---

[21:29](https://youtube.com/watch?v=Bw1FGnbS71g&t=1289s)

definition like which ones generate the code that you like basically. Um uh yeah um this is kind of like the plan output I talked about. Um I use this thing called restructured text. We use RST files on our routine instead of markdown. Um, personally I like them because they have like a little more kind of like syntax highlighting. Like there's like little uh little things in RS like in addition to like markdown that are nice. Um, so you kind of have a little bit more like kind of visual variation when you review these lines and like this is the main thing I'm looking at. It helps. Um, yeah. Um, cool. So moving on to kind of final step which is just execution. Um, this is like really kind of a robotic process. Um, it's just about moving fast and not breaking anything. Um, and and that's just about kind of like not making mistakes. Um, uh, there are some tricks that like kind of can help you generate faster. Um, but basically like once you once you're at the coaching stage, if you've already made a mistake in terms of like what you're doing or like kind of um, you know, the way

---

[22:30](https://youtube.com/watch?v=Bw1FGnbS71g&t=1350s)

you're doing it, then it's already over. Like it it doesn't matter how you kind of like generate the code. Um, and and the plan kind of like already has all of the information about like the code that's going to be generated. So, it's like kind of already over by the time you've written the plan. And the code gen is just like kind of this like mechanical step um that I don't really worry about that much. Um, there's some like stylistic things that like some models do better than others. Uh, generally use like a fast model for this kind of like execution code gen. Um, and and I like to like use models that like more tur and like just like kind of like do the right thing in in the style I want like follow instructions well. Um, but yeah, for Koshen, I I just like experiment a lot with like kind of walls that are like kind of like the at the paro like threshold for like kind of fast and like high quality. And that's kind of what I want for this cogen phase. Um, yeah. So, kind of recapping um moving fast, it's all about just like not doing the wrong thing, not doing the wrong way, and not doing it badly. And that all starts from the top, like from like just thinking about it, coming up with the right thing to do, planning it

---

[23:32](https://youtube.com/watch?v=Bw1FGnbS71g&t=1412s)

out well. Um, and I want to skip to like the codeen phase. If you've done the other steps, right, then then it'll just be good. Um, cool. Um, so other parts about moving past, especially as your code base increases, uh, is just about like being really ruthless with your code. Um, this has always been true and I think it's especially true now as like one person can like even more code. Um, you have to like really eliminate anything that slows you down. Um, so you just have to have this like really keen eye for like anything in your code that is slowing you down. Like is this like code kind of janky or like buggy or whatever like that's going to slow you down. You should probably go and like fix it. Um, and you should also prioritize things that speed you up like you know various tools or like many things can like speed up your coding process outside of AI and it's important to like invest in those things um because they'll give you leverage. Um, so there's a ton of old tricks that a lot of you probably know, but um, you know, invest in tests and types and linting and refactoring. Um,

---

[24:32](https://youtube.com/watch?v=Bw1FGnbS71g&t=1472s)

but even more importantly, just like invest in simplicity. Um, this is really crucial and if you haven't watched this talk by Rich Hickeyi, it's really good. Um, highly recommend it. Um, this is kind of another piece of our our planning prompt. Um, but the gist of it is really just simplicity. Like simplicity is is like the golden rule in code. Um uh simplicity means many things or many like kind of aspects to it. Um but well-designed systems that are simple and like well kind of like architected and not too coupled in the wrong ways um they will just be easier to work with. And when you have a codebase that's like nice and easy to work with, you can feel it, especially when you're like working with AI because it'll just kind of like grow by itself. Like it'll just know what to do with itself. Um, I think once you start to kind of get this feeling for code, you kind of like feel when the code is kind of living and when it's like kind of dead and sick. Um, so I think that that's kind of important to keep an keep an eye on. Um, yeah. Um, cool. And then the new tricks um are really pretty

---

[25:34](https://youtube.com/watch?v=Bw1FGnbS71g&t=1534s)

straightforward, but um, basically you should always remember that if you're generating more code, you should be spending more brain power on it. Like that's very important. Um, like if you're spending the same amount of brain power on on more code, like if you don't feel just like more tired, uh, then something's wrong. Like then you just like haven't really understood the whole thing that's happened. Um, so you should feel tired when you're like generating a lot of code with AI or just like working with AI in general, it's a very tiring process. Um and uh if you are really like kind of living it really like kind of feeling the code even becoming the codebase um you develop this like kind of spidey sense for parts of the code like you know which parts are bad um where there might be like kind of dark forests like parts that you don't really understand or like parts are just like kind of weird um or where there's like kind of brittle stuff that just breaks all the time or where there's like kind of like pesky issues that just like come up um and you don't really understand why. like those are kind of like signals to you that you should maybe like dig in there, maybe understand those like kind

---

[26:35](https://youtube.com/watch?v=Bw1FGnbS71g&t=1595s)

of with your human brain more because like a not help you like really fix those. It's just going to like give you like weird band-aid patches. Um it'll take like four deep thinking to like really fix these things. Um yeah. Um so AI code review is is useful. We we've like experimented with this in different ways. Um I I don't have too much to say here, but um the plan actually helps a lot. uh when you have this plan and it goes up there uh to the AI with like the changes, then the AI kind of like knows what you're trying to do and it can like kind of spot issues um between the plan and the death. That's very useful. Um, and then, um, it's helpful to like if you can like choose the model that's doing the review and also like kind of prompt it in a particular way. Like maybe you have like particular things to watch out for. Maybe there's like context like uh just like kind of invest in those systems and like kind of just tweak them a lot until like they they have all the context that you think they should have to like really review your code well. Um, like yeah, for us we have like you know style guide things for like front end stuff like don't use like these hardcoded colors or whatever. Um uh so like very

---

[27:36](https://youtube.com/watch?v=Bw1FGnbS71g&t=1656s)

important to like kind of do that stuff and invest the time there. Um yeah. Um and in terms of like actual execution for me, I don't like the whole parallel coding agents thing. Um I also don't use these CLIs that much. Um I I just like to work on one branch. Um, and I sometimes in parallel, like in parallel cursor tabs, I'll like kind of like do little small things that are usually unrelated to the kind of main thing I'm doing, but are like possible for me to like kind of review in a batch when I like kind of review the big thing that I'm doing. So, um, it's all about for me kind of like optimizing for like a little bit of parallelism while I'm kind of doing this main thing and then like just kind of bashing my review because like you always have to like human review the things just like validate it, make sure it's working working. Um, so I just kind of like try to like bash some kind of like parallel things that can be viewed at once with like my big thing. Um, that's that's really like my my whole trick. Um, yeah. So, uh, brief recap. Um, it's been a lot on cursor. Coding is about thinking and it's about

---

[28:37](https://youtube.com/watch?v=Bw1FGnbS71g&t=1717s)

the flow state. Really about optimizing for your flow state. And then, yeah, AI is really just about kind of like leverage thinking and like trying to optimize for your own flow state. even in this kind of like brain roddy like AI context. Um yeah, AI coding in like its bad form is a brain rot like if you're like kind of just like waiting for this thing to generate your code and like kind of I don't know like scrolling on Twitter or something. Um that's bad. Um like your code's going to be bad. Um you have to like be locked in to your code. You have to be looking at the code the whole time. like even while you're generating something, you should just like watch it generate stuff or like you know look at somewhere else in your code or like figure around like just like in the zone. Um uh it's really easy to like lose that when like something is ering the code for you. But um just don't do that. It's really bad. I I still do it sometimes, but like really important to try to avoid it. Um it's like I think it's what leads to like the worst code that I've written. Um yeah. Um yeah. And then what I talked about just now think,

---

[29:37](https://youtube.com/watch?v=Bw1FGnbS71g&t=1777s)

plan, execute. Um and just remember that like it all starts from the thinking process. Um all the code stuff is like all all just like kind of at the end of the pipeline. Um you just have to like think, do the right thing, do it the right way. And then like the codegen is just like kind of mechanical now. Um which which is awesome. Um but it doesn't stop the importance of thinking. Um so so like very specifically what I use I use cursor. um models I like these days I like to use GP5 codeex for planning and I like to use GP5 fast for implementing um I experiment with other models for implementing um I definitely think codeex is the best planning model right now um it's slow but it's like fine for it to be slow um because the plan is like so important it's fun to like wait for it think about it um and just like kind of review it a lot um yeah uh cool um I'm going to pause here and then I might come back and like show you like some more specifics about like cursor as we do Q&A. But um yeah, that's

---

[30:38](https://youtube.com/watch?v=Bw1FGnbS71g&t=1838s)

my talk. [Applause]