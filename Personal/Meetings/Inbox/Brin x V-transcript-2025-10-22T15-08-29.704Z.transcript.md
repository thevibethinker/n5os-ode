**\
00:02**\
Brinleigh Murphy-Reuter\
Hi. Oh my God. Do you want to type to me? Oh, my God, you sound awful.
Why don\'t I have access to Gemini? What is happening? Am I signed in
with the wrong account right now? My. My chat GPT isn\'t working.

**\
00:45**\
Vrijen Attawar\
Interesting. Wait, why? What are you doing?

**\
00:50**\
Brinleigh Murphy-Reuter\
And my Gemini is not available.

**\
00:53**\
Vrijen Attawar\
Oh, my God, is AWS down again? That would suck.

**\
01:00**\
Brinleigh Murphy-Reuter\
Yeah, it\'s like, not even. It wasn\'t allowing me to sign in with my
Google. It gave me like an error code and now it\'s saying, my Gemini is
not available. This is not the day. Is yours working? Yeah, Operation
Timeout. Weird. Oh, my God. My Gmail is working though. Can you hear me?

**\
02:07**\
Vrijen Attawar\
Dang it. I had left it on mute. Sorry about that.

**\
02:10**\
Brinleigh Murphy-Reuter\
Oh, no, you wasted your voice.

**\
02:13**\
Vrijen Attawar\
I know, I know. Well, I was. I actually got nice and warmed up for a
second there, which is why I sound a little bit more normal.

**\
02:21**\
Brinleigh Murphy-Reuter\
Oh, my God, you poor thing. Are you sure this is okay?

**\
02:24**\
Vrijen Attawar\
It is, it is, because I\'ve been like, dying to get this out to someone
or at least like get folks situated with it, and I need to work on a lot
of like, language and messaging, so I frankly need the practice. Okay.

**\
02:39**\
Brinleigh Murphy-Reuter\
Okay.

**\
02:40**\
Vrijen Attawar\
But yeah, don\'t worry, I\'m not pushing myself too hard. It doesn\'t
hurt. It just sounds like. What did I describe it? Emma Stone. Asmer.

**\
02:48**\
Brinleigh Murphy-Reuter\
Yes. Oh, my God. Asmer. Is that what the kids are saying these days?

**\
02:53**\
Vrijen Attawar\
I believe it is, yeah. Asmr. Asmr.

**\
02:57**\
Brinleigh Murphy-Reuter\
Asmr.

**\
02:59**\
Vrijen Attawar\
Shorten everything.

**\
03:00**\
Brinleigh Murphy-Reuter\
Yeah.

**\
03:01**\
Vrijen Attawar\
Cool. Okay, let me show you. Zoe. Zoe is fucking awesome. So for
context, you\'re non technical, right?

**\
03:10**\
Brinleigh Murphy-Reuter\
Completely, Utterly, totally.

**\
03:13**\
Vrijen Attawar\
Okay, I am also non technical, but I\'m definitely on the sort of very
technical side of non technical insofar as not only what I\'ve learned,
but also just like general instincts. Right. And I suspect that you
would fall into that category as well, given what I know about the
bootstrapping you\'ve done. So. So, long story short, one of the big
challenges for folks like us is in theory, if we could just describe how
server is set up or vibe code it, that would be great. But there is
still this non zero significant jump of going from text on a screen to
something happening. That abstraction is not very well practiced in
folks like you and me. What Zoe does is it is essentially a computer in
the cloud you can prompt. In fact, it\'s both a computer and a server.

**\
04:09**\
Brinleigh Murphy-Reuter\
When you say a computer in the cloud. What. What? What\'s that?

**\
04:14**\
Vrijen Attawar\
So it is a. I mean, in. In the most general Holy shit. Gary. How\'d you
get up there? Sorry, one second. My cat just went turbo.

**\
04:23**\
Brinleigh Murphy-Reuter\
Is your cat named Gary?

**\
04:25**\
Vrijen Attawar\
Yeah, Gary and Avocado. Avocado.

**\
04:29**\
Brinleigh Murphy-Reuter\
I always wonder about babies named Gary.

**\
04:35**\
Vrijen Attawar\
What led a parent to do that to their child?

**\
04:37**\
Brinleigh Murphy-Reuter\
Well, yeah, like I feel like Gary\'s aren\'t born, they just suddenly
appear as 45 year old men. Like I\'ve never met a child named Gary, but
I know a lot of men named Gary anyway. But you have a cat named Gary.

**\
04:51**\
Vrijen Attawar\
That\'s amazing, Gary. Yeah, it\'s after a particularly good TV show. In
case you like Futurama, I can recommend it.

**\
04:59**\
Brinleigh Murphy-Reuter\
I haven\'t seen it, but. Awesome.

**\
05:03**\
Vrijen Attawar\
Yeah. So long story short with Zoe, when I say it\'s a computer in the
cloud, I literally mean it is an input output device, right? So instead
of you clicking shit or like scripting or writing out a prompt, you are
prompting the AI and then the AI is essentially doing a sequential or
parallel release of or engagement of agents to go through that entire
process with you. So it sounds a little magical and when it works it is
magical. But I want to be upfront about this. It is very much a like
that. The company hasn\'t officially launched, it\'s run by some very
talented devs, but it is a imperfect solution.

**\
05:55**\
Vrijen Attawar\
Now that being said, the reason why Zoho is basically down to discuss
even paying me to build products for them is that I seem to have
apparently a very good knack for making Zo work. And so what I\'m
effectively going to show you today is different facets of the system
that I\'ve built out in Zoho. And then what I can offer, because I\'m
putting this together for folks for the next week or two is to
essentially either. And obviously if you\'re one of the first folks and
you\'re a friend, like if you\'re willing to put your faith and time in
me, then I\'ll give you a sweet deal and go above and beyond. But I\'m
essentially just looking for folks that are willing to take a punt on a
new productivity system.

**\
06:43**\
Vrijen Attawar\
Specifically folks that are independent and high agency enough to
maintain that system and not need me for every little fucking thing,
which I believe you are. So that\'s sort of the context. Are we on the
same page so far? Does that sound sort of like at least somewhat aligned
at the moment?

**\
07:00**\
Brinleigh Murphy-Reuter\
Yes. Yes. Okay, it does, yeah. And you say productivity system. So
basically I was telling Logan that I don\'t even have time to hire an
onboarded Chief of Staff.

**\
07:11**\
Vrijen Attawar\
Right.

**\
07:12**\
Brinleigh Murphy-Reuter\
And yet, like, I have too many fucking things to do that are like, I
need to introduce this person to this person and, you know, check in on
this thing and redo this timeline and then send it out to this person.
And it\'s like a thousand little things.

**\
07:31**\
Vrijen Attawar\
Totally.

**\
07:32**\
Brinleigh Murphy-Reuter\
Is this gonna help with that?

**\
07:34**\
Vrijen Attawar\
Oh, yeah. So, okay, so let\'s start with something really simple, right?
Let me paint you a picture right now what\'s likely happening. I mean,
you were trying to log into Gemini as soon as you jumped on a video
call. So I\'m assuming that means you pay Google for, like that business
pro plan. You\'re using Gemini, you\'re using all of their transcript
and sourcing tools. Are those correct assumptions? So far?

**\
07:58**\
Brinleigh Murphy-Reuter\
Yes. But I don\'t do anything with my Gemini transcripts.

**\
08:02**\
Vrijen Attawar\
Yes, exactly. So the point, I don\'t even.

**\
08:05**\
Brinleigh Murphy-Reuter\
I never read them, I never do anything with them.

**\
08:08**\
Vrijen Attawar\
Right. So we are all drowning information. Right. Especially with AI.
And the sort of salient insight for me was that it is less of a like, I
need to spontaneously or I need to, in a disciplined fashion, go through
every single meeting afterwards. Because that\'s just a waste of goddamn
time. Right? Yeah. What you instead need is a series of sort of like
staging gates, where at each staging gate a particular type of very
clearly defined analysis is happening to the transcript that in a very
reliable and deterministic way produces the kind of stuff that frankly,
we need things to boil down to. Right? So you don\'t need to know what
the small talk was that you had at the start of the conversation, and
you frankly don\'t even need to remember any of the action items.

**\
09:05**\
Vrijen Attawar\
What would be ideal is if everything that you had to do in a meeting
after meeting, from setting up warm intros to tracking decisions that
were made, all of that gets done programmatically. That\'s the first
thing I\'ll show you, is a system where I use Fireflies. All of my
transcripts end up over here. When a transcript is pre processed, it
doesn\'t say zo processed, it just keeps track of it. That way, once it
gets processed and updates the name, what that does is because it runs
on a schedule. What it does IS agent. Every 30 minutes it will go to
that folder and it will essentially check are there any new transcripts?
Then it will add.

**\
09:57**\
Vrijen Attawar\
Add all those transcripts to a queue and every 10 minutes it\'s going to
process that queue in a very particular type of way that I can customize
for you. But this is all zero input so far. Like literally this meeting
is going to end and you\'re going to see the follow up email sort of
come pretty quickly afterwards because it\'s basically zero touch.
Right. But to show you what the actual outputs are, because I know that
sounds very promising, go to N5, go to meetings. What\'s a meeting that
I did where I had a warm intro to do? I think the Ali Cielo meeting.
Yes. Okay. So right now I\'ll use this meeting as an example. I didn\'t
look into this one in particular because I didn\'t actually need to do
this, need to leverage this one.

**\
10:53**\
Vrijen Attawar\
But just to hopefully not land flat on my face, it generates multiple
distinct categories of analysis based on whether it\'s an internal or
external stakeholder and what type of stakeholder it is. And then it
will decide what blocks to generate that are relevant to that type of a
meeting. Okay. And so it will give you obviously a recap what was
discussed in this meeting that\'s always available. But with regards to
the warm intro, maybe you just want to cut to the chase there. Okay,
fuck. This one just generated, didn\'t have warm intro. Who did?
Theresa. Warm intro in this case, because on the call I had told her I
will introduce her to Gemma at samvid. Right. It natively extracts all
of that from the meeting, dumps that into context, identifies what
exactly I need to do.

**\
11:47**\
Vrijen Attawar\
And this was before I threw in the last step of generating the damn
thing according to your voice. So I don\'t want to just keep looking for
the same thing. But hopefully you can see over here with like zero
effort, it has like categorized every single intro I need to do and
given me enough essential information that you could dump this in Claude
and with one shot get a perfectly serviceable intro. Does that sort of
track so far?

**\
12:14**\
Brinleigh Murphy-Reuter\
Yes.

**\
12:17**\
Vrijen Attawar\
Now, this may not exactly fit what you want, right. And my thinking,
just to sort of like lay it out as I\'m putting this together, is
creating a sort of vanilla core version that is cheap and that
essentially ZO would help me clone onto people\'s accounts or share via
GitHub. So it\'d be very easy to do effectively. And that\'s a like buy
it, pay it, set it up yourself sort of thing. And then the other thing
I\'m looking to do is actually building out these workflows where, you
know, I would interview you for a certain amount of time and then build
out specific workflows for you off of a base of like a prompt library
that is more time intensive.

**\
13:03**\
Vrijen Attawar\
But again, in theory, because I\'m just trying to build up my brand and
sort of my reputation at this point and frankly even just learn how to
be a good collaborator in this process. I\'m down to do more of the
heavy lifting and keep it very lightweight for you, but frankly,
hopefully none of this looks especially complicated and it\'s all set up
for you to personalize as easily as swapping out a configuration file.
It\'s very much meant to be modular from the get go. I\'ll pause there.
And I\'ve thrown a lot at you.

**\
13:37**\
Brinleigh Murphy-Reuter\
Okay, so I\'m trying to think though. So you said like. Okay, so the
warm intro thing is there. I would. Is there a way then to tell Zoe,
like the next step, like write me the warm intro and send me the draft
that I can review and then I want to give you feedback on it or any
changes to make and then I want you to send it totally.

**\
14:01**\
Vrijen Attawar\
Not only that, you can actually set it up such that it will
automatically run that first half where it pre processes everything.
Then you can set it up to approach you when it\'s done and ask you
questions and fill in the gaps and then regenerate and have drafts
waiting in your account for pressing send or just telling it directly
because it has an integration with Gmail. Hey, just send this fucker
out. Right. Okay, so it\'s. The possibilities are actually staggering
and endless because, for example, you can spin up your own version of
N8N inside of Zoho. Of what? Have you heard of N8N? Or it\'s like
Zapier?

**\
14:46**\
Brinleigh Murphy-Reuter\
No.

**\
14:47**\
Vrijen Attawar\
Are you familiar with Zapier or Zapier?

**\
14:49**\
Brinleigh Murphy-Reuter\
I\'ve heard of it, but I\'ve never used it.

**\
14:51**\
Vrijen Attawar\
It is a very popular automation software. Zapier is probably the brand
leader. N8N is considered the hardcore version of Zapier. And you\'re
actually able to. Because N8N is open source, you can actually install
N8N and the workflow builder logic inside your Zoho. You can connect it
to another Skunk Works project that I\'m doing that I want to have be a
lead gen tool for Careerspan is I\'m building a like seed stage ATS on
Zo, something where you just plug in your API key and it will literally
do like 80% as good of a job as career span, basically for. For like
cost, like token cost. Huh.

**\
15:44**\
Brinleigh Murphy-Reuter\
Okay. Okay, I think this is making sense. I am not prepared to set it up
myself, so definitely. Oh, I\'m curious. The other thing that I. So
there\'s a couple different things that I feel like I\'ve needed.

**\
16:02**\
Vrijen Attawar\
Yeah. Describe to me, like, what have been the pain points, which, by
the way, I have more time. Yeah, we\'re, we\'re going into the 11, so
it\'s all good.

**\
16:09**\
Brinleigh Murphy-Reuter\
Yeah, I have an 11, so I just need to pop off then.

**\
16:13**\
Vrijen Attawar\
Perfect, Perfect.

**\
16:14**\
Brinleigh Murphy-Reuter\
So, like, okay, I got an email from a contact who wants me to introduce
her to a hiring manager and. But I only have contact with that hiring
manager on LinkedIn. But I like, have it read that email and go to my
LinkedIn and send a intro on LinkedIn. So that\'s like one thing.
Another thing is like, I can.

**\
16:49**\
Vrijen Attawar\
Yeah, okay. Yeah, keep going.

**\
16:53**\
Brinleigh Murphy-Reuter\
Trying to think of something else that happened yesterday. Oh, I wanted,
I was frustrated because Howie only exists in my email. But, like, I
wanted to be able to, like, text Howie something to change something. So
I was driving and I didn\'t know how to get Howie to change a call that
I was going to be late for because I was driving. And I wanted, like, to
be able to talk to how he somehow outside of my email and have Howie do
something to my calendar. That was another thing.

**\
17:34**\
Vrijen Attawar\
So that I can actually give you a Howie native solution for if you\'re
interested.

**\
17:40**\
Brinleigh Murphy-Reuter\
Yeah.

**\
17:42**\
Vrijen Attawar\
But Howie actually interacts very powerfully with Zoe because Zoe exists
through text, through email. You can email Zoe a voice recording and it
will process it according to workflows. It will run it, like on a
schedule agentically. So Zoe is sort of like a jack of all trades kind
of tool. The way that I would run that with Howie is. And I\'m yet to
fucking. Austin Petersmith has not responded to me. I\'m trying to,
like, break new ground with this goddamn app. But essentially I have a
system set up in Howie where you embed these invisible tags at the end
of your email. It\'s super easy, especially if you use Superhuman,
which, if you don\'t use Superhuman, you should use Superhuman. If you
don\'t use Superhuman and you have a problem with emails, you should be
using Superhuman. Human.

**\
18:40**\
Brinleigh Murphy-Reuter\
Okay, so if I. Okay, Superhuman. Yep. Okay, so I\'ll use Superhuman.
How. How do all these work together?

**\
18:49**\
Vrijen Attawar\
So this is the like, sort of multiverse of madness of tech tools that I
have, like, wrought onto myself. But they actually work like a charm if
you set them about up correctly. So let me show you, for example, with
Howie.

**\
19:05**\
Brinleigh Murphy-Reuter\
But, like, why do I need to use Howie and Superhuman?

**\
19:09**\
Vrijen Attawar\
Because, because of the specific things that it enables. I am, I, I do
believe that there will be a huge amount of Convergence in the coming
years, and the total number of apps we have to have will go down. My
read on the industry in the space is that essentially, up until large
language models, we didn\'t really have the ability to automate even
sort of well. And now we have the ability to do it kind of sort of well
sometimes.

**\
19:43**\
Vrijen Attawar\
Which is why Vibe coding, as much as you\'ll hear a lot of CEOs talk big
fucking game about Vibe coding, it is actually incredibly hard because
almost always when you\'re Vibe coding, you are big designing and
building things that are outside of the training sample of the fucking
AI, because it\'s not trained on a new app that hasn\'t come about or a
new user mechanic. Right? So you\'re bounded by the. You are bounded by
the understanding of the tool. But the cool thing with something like
Zoe is because Zoe is able to. Like, I\'ll show you. These are custom
rules for Howie that I can just share with you and explain how they
work, and you can literally just paste them in Howie and they will,
like, work the same way.

**\
20:30**\
Vrijen Attawar\
But essentially what I do is I have in my Superhuman, which you\'ll see
in a second. I have. You\'ll see in the Superhuman over here. Email.
Email to someone that I\'ve written. Here we go. No, how he wasn\'t
included in that. Just one second. I\'ve been out of commission for a
bit, so my email is locked the up. Laura. Howie. Okay. Yeah. So, for
example, like, nor, like, if I had to guess how you have to use. You use
Howie right now, you probably have to be very specific in the writing of
the email. Right. What you want it to do.

**\
21:21**\
Brinleigh Murphy-Reuter\
I literally just started using it.

**\
21:23**\
Vrijen Attawar\
Okay. Most likely you will have to do that unless you take advantage of
preferences. Because what preferences do and what LLMs that are well
designed or able to do is very frankly, in a almost autistic way,
process instructions to the T, no deviation, blah, blah. Right. So
effectively what I do with. With Howie is I will embed these, like,
little. You can\'t see them here. One second. Yeah, Michael, Howie.
Like, over here, I interact with Michael. He said, great, I\'ll meet. So
I tapped on Howie because over here, I leave these, like, little tags
hidden at the bottom of my signature in white ink. And anytime I want to
have how we do something specific while making it seem like magic, which
I have literally had people go like, your Howie is magic. How are you
doing it?

**\
22:39**\
Vrijen Attawar\
It\'s because I will basically have all of the tags here. I\'ll just
delete the ones that are irrelevant. It works perfect in Superhuman
because Superhuman has dark mode, so it shows up white naturally without
me having to change it from white text.

**\
22:55**\
Brinleigh Murphy-Reuter\
You do this every time, though. If you look in Howie, all those things
show up at the bottom and you go in and delete them manually every time.

**\
23:04**\
Vrijen Attawar\
No, only for the first email in that thread. And then I just try to keep
that thread for all bookings with that person. With that person. Yeah.

**\
23:12**\
Brinleigh Murphy-Reuter\
Okay.

**\
23:13**\
Vrijen Attawar\
And the way Zoe comes into it and where I hope to implement Zoe Austin
Petersmith will respond to my goddamn email is I actually hope for Zoe
to intelligently inform Howie what the tag is in advance. So I don\'t
even have to do that shit in the fucking signature anymore. You know,
Howie will just know when I want it to activate. Like, I even have it
set up with two settings for offer and await, where sometimes how we
will wait for you to respond with your preferences, and sometimes it
will offer preemptively because one of those is more strategically
relevant than the other in particular contexts. Right. So, like,
obviously to be able to do that seamlessly, subtly. Big unlock. So
that\'s. It\'s this kind of, like, blend of, like, little stuff, big
stuff that has been quite valuable.

**\
24:03**\
Brinleigh Murphy-Reuter\
Okay. Okay. This is great. I am feeling overwhelmed, though, at all of
these things. So what I, like, I\'m going to sign up for Superhuman.
I\'ll get the desktop app, which I\'ve never used before, so I need to,
like, learn how to use it. And then what? So then my Zoe works with my
Superhuman and my Howie and my transcripts. Should I also get Firefly?
Because some of my meetings are in teams, some of my meetings are in
Zoom, Some of my meetings are on Google Meet. So do I need, like, a
different recording app to work better with Zoho?

**\
24:53**\
Vrijen Attawar\
I would just need to look up how Google stores stuff, but I suspect its
transcription is good and I suspect they\'re going to be able to store
it in a specific place in drive. So for anything that\'s off Zoom and
off thingy, but on your desktop, I would use granola.

**\
25:13**\
Brinleigh Murphy-Reuter\
Okay. Granola.

**\
25:15**\
Vrijen Attawar\
So I maintain two. And between granola and fireflies, everything usually
gets covered. For IRL meetings, I\'ll use a physical device, like a
Plaud.

**\
25:26**\
Brinleigh Murphy-Reuter\
A what?

**\
25:27**\
Vrijen Attawar\
Applaud A Plaud.

**\
25:32**\
Brinleigh Murphy-Reuter\
A Plaud. And that\'s a physical device.

**\
25:38**\
Vrijen Attawar\
It is a physical device that magnetically attaches to the back of your
phone and acts like a video. Like not a video recorder. Like an audio
recorder.

**\
25:45**\
Brinleigh Murphy-Reuter\
That flawed. Okay. Why can\'t I just turn on granola? Like from my
phone.

**\
25:53**\
Vrijen Attawar\
Sweet summer child. That is because granola for in person meetings is
unfortunately ass at speaker identification. So if that\'s something you
care about in an in person meeting, then granola won\'t be good enough.
So these are like the nuances of like transcription software, actually
that like different ones invested in different sort of skill points
essentially, which is why some are frankly better at transcription and
fucking ass at integration and others have like Fireflies has focused on
the. Like let\'s integrate and let\'s have like a buttload of
connections and make it relatively easy to spin up and run. Which is why
I\'m. I\'m partial to Fireflies.

**\
26:36**\
Brinleigh Murphy-Reuter\
Okay, so wait, so what am I buying then? Granola. And I\'m getting
applaud.

**\
26:44**\
Vrijen Attawar\
So to keep things very simple for you, what I wanted to more so give you
a sense of is the possibilities and the directions that we can go. I
think what is a really easy place to start that would actually be also a
very sort of great use case for me would be just building out a very
basic meeting processing pipeline.

**\
27:10**\
Brinleigh Murphy-Reuter\
Okay.

**\
27:11**\
Vrijen Attawar\
I would be happy to like essentially do that for like 100 bucks and
I\'ll like sort of customize it to your stuff as well. But it\'ll be
good sort of like incentive for me to finalize and post produce that
workflow because that\'s kind of my marquee workflow at the moment.
Okay. The other advantage of sort of going through me with Zoe is that
you get 50% off on API pricing, which you quite frankly at the outset
won\'t be using enough off for it to make a difference.

**\
27:40**\
Vrijen Attawar\
But if you really like Zo and you really start coding with Zo because
you spend Zo money to build out Zo, you will want that 50% discount
because like I spent almost two grand, two and a half grand building out
everything I have, which luckily they gave me an 80% discount, so it
didn\'t sting that bad. But yeah, that is the. So. So I\'m already
working on sort of packaging these up, making these really easy. Are you
trying to hire anyone anytime soon? Probably that would be. The other
one I can be, you know, helpful with is a. Essentially an at. I\'m
basically just rebuilding the ATS on Zoe and going to give it away to
founders for free as a lead gen thing and have Zoe sponsor it
effectively, because that is them getting their software out there,
right, Embedding in founders workflows.

**\
28:41**\
Vrijen Attawar\
So it\'s a cool kind of symbiotic win, win situation for Me. All of
which is to say you don\'t worry too much about the arduousness of
having everything integrate. My recommended starting point would be mull
over whether you want to take me up on the offer of at least setting up
a meeting pipeline for you.

**\
28:59**\
Brinleigh Murphy-Reuter\
On Zoe and that meeting pipeline, just to be clear, basically reads my
transcripts and then decides what I need to do next.

**\
29:10**\
Vrijen Attawar\
Does everything from decide what does everything from summarize to tell
you what you and everyone needs to do next to generate the knock on
deliverables that are required as a result of that meeting in your
voice. So I\'ll throw in a bonus because it takes like a couple minutes.
I can train it up on your voice if you spend the time collecting up a
bunch of emails for me. And we can actually get it pretty fucking close
to your writing style with just like one off effort.

**\
29:45**\
Brinleigh Murphy-Reuter\
Let\'s do it, man.

**\
29:46**\
Vrijen Attawar\
Yeah, I hope that excites you. I think it\'s going to be fucking great.
And yeah, it would just be very cool to work with you. I know Logan
loves you so much. I\'m like. I\'m feeling a little left out. I\'m like,
why am I not friends with Brinley?

**\
29:59**\
Brinleigh Murphy-Reuter\
You know, we\'re friends. We\'re friends.

**\
30:01**\
Vrijen Attawar\
We are friends, but we should better friends.

**\
30:04**\
Brinleigh Murphy-Reuter\
We should best friends.

**\
30:05**\
Vrijen Attawar\
Exactly, exactly. That would be the ultimate twist of the knife. If I
were to. If I were to become a better friend to you because of the way
I. I think I might crumble Logan\'s whole world. So let\'s not do that.
Or let\'s do it and say we did it just to really fuck with her. Cool.
Let me put this stuff together. I\'ll send a follow up email because now
you know, I have no fucking excuse. And I\'ll summarize sort of the core
points. I\'ll also just for your own sort of way to assess the quality
of the output, I\'ll actually package the entire output that came from
this conversation with no edits. So. So you can see what the approximate
baseline quality of the output would be.

**\
30:51**\
Vrijen Attawar\
So I\'m luckily super arrogant because my shit works great if I\'m
focused and I take enough Adderall and set it up correctly. So yeah,
that part is easy for me.

**\
31:06**\
Brinleigh Murphy-Reuter\
Okay. Amazing. I\'m really excited about this. I guess. Let me know what
other integrations I should be doing on my end to make sure that you
have all the components you need. Like. Like I said, like granola.

**\
31:20**\
Vrijen Attawar\
Well, one, whatever. One. One actually really good sort of unlock. I
could Suggest to you if you want to, if you\'re trying to get into the
productivity game. Because I literally have not had a chance to
recommend this to anyone. Everyone that knows about this has already
paid for all of these tools. Get the Lenny Richicky. Look at the Lenny
Richicky newsletter subscription for a year. It gives you a free year of
linear Superhuman repl it Perplexity desk script. Those are just the
ones up over here. I think one of the audio recorders is in there as
well. They just give you a stack load of free shit, but it only works if
you\'ve never paid for that product before.

**\
32:05**\
Vrijen Attawar\
So if all of these are sort of new to you, then like Superhuman, I will
honestly say I as a founder can swear by you don\'t even need me to set
it up. Just fucking use Superhuman. And you will not only learn more
about UX than any other product will ambiently teach you will also love
writing emails.

**\
32:25**\
Brinleigh Murphy-Reuter\
Oh, wow. Okay.

**\
32:26**\
Vrijen Attawar\
It\'s legit. It\'s. It\'s legit.

**\
32:28**\
Brinleigh Murphy-Reuter\
So I use Superhuman instead of my Gmail account. Is that right?

**\
32:31**\
Vrijen Attawar\
Yeah, you use Superhuman instead of Gmail because Superhuman has a lot
of. Superhuman is basically how to navigate your email with your
keyboard. Like how finance bros navigate Excel with their keyboard. Wow.
Yeah, it\'s incredible. The feeling of power is unique. Wow.

**\
32:51**\
Brinleigh Murphy-Reuter\
Okay. Amazing. I\'m excited to try this.

**\
32:54**\
Vrijen Attawar\
Yeah, Superhuman would be an immediate unlock. And then what I\'ll also
do is I will generate the and yeah, I don\'t even need to remember my
fucking deliverable thing will remember. I\'ll send you a copy of my
Howie rules and preferences. Review them. I\'ve shown you my
implementation. Review those settings, see which ones apply to you, and
then basically break them down into bite sized chunks and feed them to
Howie. I say bite sized chunks because I just don\'t know how good their
back end is at integrating complex multivariate instruction. So the more
condensed and focused you can give the clumps, the better your results
will be. Is the implementation advice there?

**\
33:41**\
Brinleigh Murphy-Reuter\
Okay. Okay.

**\
33:43**\
Vrijen Attawar\
Oh, and one last thing. Because I know we\'re approaching time, all I
really ask for comp over dollars is that you say nice things about the
work that I do. If you believe in it. If you believe in it. Only if you
believe in it, you got it. But yeah, I do ask that because I have mostly
been keeping all of my AI powers under wraps and I\'m feeling now\'s the
time to come out.

**\
34:08**\
Brinleigh Murphy-Reuter\
Swinging to open it up.

**\
34:10**\
Vrijen Attawar\
Yeah, I love it. I love it.

**\
34:12**\
Brinleigh Murphy-Reuter\
Okay, well, I\'ll look out for your follow up email then and let\'s get
going. Let\'s do it.

**\
34:18**\
Vrijen Attawar\
Let\'s do it. I\'ll catch you soon.

**\
34:19**\
Brinleigh Murphy-Reuter\
Okay, bye.
