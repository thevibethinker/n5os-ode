**\
00:01**\
Ben Guo\
Hey, man.

**\
00:01**\
Vrijen Attawar\
Hello.

**\
00:03**\
Ben Guo\
Hey, Dan.

**\
00:04**\
Vrijen Attawar\
Hey, can you hear me?

**\
00:06**\
Ben Guo\
Yep. Yeah, how about me?

**\
00:08**\
Vrijen Attawar\
I can hear you. How you doing, my man?

**\
00:10**\
Ben Guo\
Yeah, doing good. How are you doing?

**\
00:12**\
Vrijen Attawar\
Doing okay. Doing okay. Having a relatively so far.

**\
00:17**\
Ben Guo\
Nice. I like how your AI has a name.

**\
00:21**\
Vrijen Attawar\
Yeah. I don\'t know if you\'ve seen Silicon Valley, but.

**\
00:23**\
Ben Guo\
Oh, right. I didn\'t know his last name. That\'s funny.

**\
00:26**\
Vrijen Attawar\
Yeah, yeah, that\'s. That Jared. Yeah. I guess it gets a good chunk. A
lot of tech. Yeah. How about you, man? How\'s your Friday going along?

**\
00:37**\
Ben Guo\
Yeah, yeah, doing good. Working on this launch video. So. Yeah, just
writing a script and trying to get the content together for the
filmmaker.

**\
00:46**\
Vrijen Attawar\
Nice, nice. That must be a really thrilling experience.

**\
00:50**\
Ben Guo\
Yeah, that\'s fun. I mean, it\'s just getting started, so we\'ll see.

**\
00:55**\
Vrijen Attawar\
Yeah. I mean, as with all things, it starts thrilling and then it
becomes aggravating and then it ends up wherever. But, you know. Sweet.
Well, I appreciate you jumping on. I was trying to collect my thoughts
and get some notes squared away as well around things to get help with.
I\'ll sort of show you. I don\'t think I\'ve actually ever done, like, a
proper screen to screen with someone, but. Oh, this is. Oh, this is
demonstrator Zoe. This is Zoe number two.

**\
01:26**\
Ben Guo\
Oh, nice.

**\
01:27**\
Vrijen Attawar\
Yeah. So this was me. Sorry. So this was essentially my thinking was.
And I guess it\'s a good. As good a place to start as any. Essentially,
my thinking was I initially thought, okay, I could just, like, send
stuff out from this account. Right. But obviously this very quickly
became a clusterfuck. And the cleanup of this clusterfuck,
unfortunately, clusterfucked some other things. So all of which sort of
led me to realize, okay, I have a good shell. And, like, we\'re
definitely at the point of complexity where even if I deploy workers
and, like, deploy the builds in, like, very specific, disciplined ways,
there are a couple of, like, conceptual things that I probably need to
clarify. I\'ll start with the first one, which is how does Zoe
distinguish between.

**\
02:24**\
Vrijen Attawar\
How does it know when I\'m telling it to just run something through its
LLM versus it is just being given an instruction. Does that resonate?
Like, I. Because when I build things, those first reflex, to the extent
that I had to bake it into the architectural design was give me an API
key. And I was like, no, but you are an LLM. You can run it. We have
this back and forth a lot where it will default to. And I suspect
that\'s because most products are not also LLMs. So the training data
doesn\'t reflect not using an external API key.

**\
03:07**\
Ben Guo\
Yeah. So I guess some of the stuff they\'re trying to get Zoe to do, it
will kind of act like it has to call like the OpenAI API or something or
like get confused about that. I see, I see what you\'re saying.

**\
03:19**\
Vrijen Attawar\
Yeah, yeah, yeah. So it\'s, it\'s interesting. I don\'t know if you\'ve
reported that behavior before.

**\
03:25**\
Ben Guo\
Yeah, we. Yeah, I, I\'ve experienced stuff like this and I think like
right now the best approach really is just like very specific prompting
about it. Like you are acting as this like. And like do this very
specific thing and like only output like what. Whatever you want. Yeah,
that\'s kind of the best way for now to like kind of get it to act this
way. It doesn\'t have like an LLM tool right now. Although I have
considered that. And not reasonable to like give it a LLM tool. Yeah,
I\'ll consider that.

**\
04:02**\
Vrijen Attawar\
Actually it\'s a little bit of a self referential problem. I understand.
I mean, yeah, as I was like thinking about it, I was like, what I\'m.
What we\'re effectively asking you guys to do is like solve prompt
hacking. Right. In a sense. Because how do you distinguish between
underlying A instruction B, text, C, just like ref. I don\'t know.
It\'s.

**\
04:25**\
Ben Guo\
Yeah, yeah. Prompt injection is a separate thing. Definitely unsolved
and tricky. But I think like something that would solve your thing that
I\'ll try to do when I get the chance is just giving Zo a tool to kind
of ask another LLM. I think that\'s totally reasonable as a tool I\'ve
considered before and that might be interesting for other purposes.
Maybe you want to asso. To ask an ensemble of LLMs for answers and
summarize that type of thing is interesting too.

**\
04:58**\
Vrijen Attawar\
What was it? Ray showed me something that looked very cool in response
to me talking about Personas which. Which was essentially this. These
sort of whoops. Yeah, yeah, totally vibe Personas. And then eventually
what I did was. And this seems to be working okay. But I again can\'t
necessarily discern is a more general vibe operator Persona that will in
certain situations. So for example, here it is. It activated writer mode
to like performing analysis based on that writer context. So I actually
can see of. I could conceive of a interesting functionality from y\' all
where you say like you. You almost. If you\'re writing a book was the
example I gave Ray. You want like first the writer, then the editor,
then the Proofreader. Then the, you know, at some point a researcher
comes in.

**\
05:57**\
Vrijen Attawar\
Like, you do kind of want a different layer on top of things.

**\
06:02**\
Ben Guo\
Yeah. Okay.

**\
06:03**\
Vrijen Attawar\
Functionality.

**\
06:04**\
Ben Guo\
I see what you\'re saying now. Yeah, I guess like another way at like
what you\'re doing is the kind of like, switch Persona thing, which.
Which Ray did add recently. So Zo can now dynamically like switch its
Persona during a chat.

**\
06:17**\
Vrijen Attawar\
Oh, sweet.

**\
06:18**\
Ben Guo\
Which, which maybe could help you, like if you prompted it to like
switch to this Persona, which does this thing and then switch back.
Like, that could probably also work.

**\
06:27**\
Vrijen Attawar\
Yeah. You know what would be a cool sort of like very lightweight
synergy would be to get a heads up on something like that, which I guess
I effectively did both earlier and today. But then what I could do is
effectively just come up with something lightweight as like a. Hey, how
does this work in context, like in the context of your show? What\'s a
cool thing you can do?

**\
06:50**\
Ben Guo\
That would be awesome. Yeah, totally. Because that\'s.

**\
06:52**\
Vrijen Attawar\
And that\'s something that we could encourage all ambassadors to do is
like, hey, I immediately when you guys give me a feature, I think of
like 10 cool things I could do with it.

**\
07:00**\
Ben Guo\
Yeah.

**\
07:01**\
Vrijen Attawar\
Just spitting that out I think would be.

**\
07:03**\
Ben Guo\
That\'s a great idea. I love that. Yeah. Yeah. We\'ll also try to better
about giving heads up on feature things. Yeah, I know there\'s a big
layout thing as well recently. I\'m sorry for any issues that caused. I
know UX changes.

**\
07:17**\
Vrijen Attawar\
Yeah, no, it\'s. It\'s. It feels, it feels very exciting. It feels very
cool to be able to assist with that kind of like, little stuff because
I\'ve always appreciated it when folks did it for us. Plus, like, this
is just so cool. It like, I mean, this is such a great. This is like a
really solid post off of like basically no prompt. I said talk about
meta. Metacognition and career growth.

**\
07:40**\
Ben Guo\
Oh yeah.

**\
07:41**\
Vrijen Attawar\
And it\'s a very decent post.

**\
07:43**\
Ben Guo\
That\'s pretty cool. It\'s cool. LinkedIn post is good material for
LLMs. It\'s probably pretty structured and easy to do. Yeah, yeah.

**\
07:52**\
Vrijen Attawar\
So the workflow that I suggest to folks for this. So this was something
Zoe actually is one of the best unlocks and like original ideas I\'ve
gotten from Zoe, which is worth probably sharing an alternative post or
something. I was like trying to find a better way to have it emulate my
voice and I kept. I was the first thing I asked the AI ChatGPT. It said
okay, set like dials. Right. A pretty sort of intuitive thing for an AI
to say is okay, set like a 6 out of 10. Warmth. Give it some examples.
Zoe\'s suggestion was start with a neutral version and apply a
transformation and create a document that tells you how to transform
neutral text into your text and then give it a repo of like
colloquialisms and like things that can slot in and substitute.

**\
08:42**\
Vrijen Attawar\
So a transformation approach to writing is actually way better in my. In
my experience.

**\
08:48**\
Ben Guo\
That\'s cool.

**\
08:49**\
Vrijen Attawar\
Yeah, it was. It was really neat.

**\
08:51**\
Ben Guo\
Like the. Probably a denser representation of your voice instead of like
a bunch of examples. It\'s like. Yeah, like pulls out the real parts.

**\
08:58**\
Vrijen Attawar\
Yeah, exactly. Exactly. So that was really cool as well. If you guys are
looking for another hackathon idea. I was trying to bug Logan to do a
vibe writing competition.

**\
09:10**\
Ben Guo\
Oh yeah. Vibrating. Be super fun.

**\
09:12**\
Vrijen Attawar\
Right. Set up the prompt. You get one shot. And what\'s the best thing
you can produce in like a one shot? But you can set up the system to be
whatever.

**\
09:20**\
Ben Guo\
Totally. Yeah, that\'s. That\'s a great idea. I like that. That would be
fun. Participate in that. Just like firstly, that would be fun to do.

**\
09:28**\
Vrijen Attawar\
Yeah, that sounds like so fun to do. So it\'d be fun to bust that out.
But yeah. So the. The other couple of things to clarify. This has stated
zero. This is known.

**\
09:40**\
Ben Guo\
Yeah, we have compaction now, so it\'s a little weird, but yeah, known
issue. It\'s. It\'s odd. I. I would not worry about that number.
Basically. Yeah, yeah.

**\
09:53**\
Vrijen Attawar\
I. I basically learned. I\'ve learned it was. Learned to forget the
number. Like learn to live. Love the number. Yeah, this had some
spunkiness. I observed pretty consistently as of like maybe week two
weeks ago is gone. Does that sound reminiscent where I would go to
reasoning high and it felt like it was slipping to reasoning zero, like
to level one. Like I just noticed more often than not when I had it to
three, it wouldn\'t think it would just produce immediately. Like.

**\
10:26**\
Ben Guo\
Yeah, I think there was some issue around like kind of the. Yeah. The
selected model or like maybe the reasoning as well. Like kind of not
being the actual one used. I think that is better now.

**\
10:39**\
Vrijen Attawar\
It is.

**\
10:40**\
Ben Guo\
Okay, cool.

**\
10:41**\
Vrijen Attawar\
Yeah, it\'s definitely better. But I wanted to check that just to make
sure I wasn\'t. Yeah, I wasn\'t the crazy one.

**\
10:45**\
Ben Guo\
Yeah. Not crazy at all. Yeah. Yeah. Basically anything you spot, you\'re
probably not crazy.

**\
10:52**\
Vrijen Attawar\
Totally fair. Totally fair. Yeah. So there was that. Was there any
questions around this? No. Okay, so now I could tell it. Switch to vibe
teacher or vive.

**\
11:04**\
Ben Guo\
You could be able to. And then it\'ll do it with the tool call. Yeah.

**\
11:07**\
Vrijen Attawar\
Teacher Persona and explain how you did this. Interesting. That\'s so
cool.

**\
11:17**\
Ben Guo\
Yeah, I think it will. Nice. Yeah, Cool. So it sees its Personas. Nice.

**\
11:23**\
Vrijen Attawar\
Great. But is this. Is this. Oh, no, it\'s still on Vibe Operator. This
is the. Or are my instructions overriding whatever you guys have in the
background?

**\
11:34**\
Ben Guo\
No. No. Interesting. That might be a bug. Let me see.

**\
11:39**\
Vrijen Attawar\
Builder. It should work on the demonstrator because I didn\'t set up
that capability on the demonstration demonstrator. Debug.

**\
11:47**\
Ben Guo\
See.

**\
11:49**\
Vrijen Attawar\
Oh, Yep, it does. So it works on the demonstrator.

**\
11:53**\
Ben Guo\
Interesting. Yeah. That\'s a little odd. It\'s possible that if you
prompted it again on the other side, it would do. It should be the same
state on both, but. Yeah.

**\
12:06**\
Vrijen Attawar\
So we\'re currently on Vibe Operator. You know what? Let\'s do this.
Let\'s try this. Activate the Vibe. Okay. Oh, no, sorry, hold on.

**\
12:34**\
Ben Guo\
That\'s cool.

**\
12:35**\
Vrijen Attawar\
Yeah, no, I shouldn\'t say that will, like, literally lead it to.

**\
12:39**\
Ben Guo\
Oh, yeah, that\'s. Yeah, got it.

**\
12:43**\
Vrijen Attawar\
As you can see, I\'ve been tinkering with getting it to do things for me
on the back. Back end.

**\
12:49**\
Ben Guo\
It\'s cool that you\'re doing this, like, conversation workspace thing.
That\'s neat. Oh, yeah. There we go. Well, that\'s. Okay. So it\'s doing
all your initial stuff, I guess, and then I don\'t know why it\'s.

**\
13:03**\
Vrijen Attawar\
Oh, no. Yeah, it\'s.

**\
13:04**\
Ben Guo\
So this is in the wrong way, I guess.

**\
13:07**\
Vrijen Attawar\
Yeah, this is the. So this was another glitch worth mentioning is that
files aren\'t necessarily being able to be seen right now when I click
into them.

**\
13:15**\
Ben Guo\
Interesting. Yeah, that\'s not good.

**\
13:26**\
Vrijen Attawar\
Yeah, the. The one thing that actually was a really big unlock recently
was setting up a database with.

**\
13:39**\
Ben Guo\
Got it. Okay. So here it seems like it\'s. It\'s kind of like running a
bunch of commands because of, like, I think, like, your rules. And
it\'s, like, getting confused about kind of how to do the Persona thing,
it seems. Which is interesting. Yeah.

**\
13:54**\
Vrijen Attawar\
Yeah. That\'s hilarious. That my absolutely rigid. My rigidness has made
it.

**\
14:03**\
Ben Guo\
Yeah, that\'s. That\'s interesting. Well, it explains why, like, in the
news state and like the other Zo. It did kind of do it. Yeah, I guess.
Yeah. It\'s getting a little confused. Yeah. The file thing is. Is bad.
I think maybe we fixed that, but I\'ll make sure.

**\
14:19**\
Vrijen Attawar\
Yeah, the file thing is. But to be fair, it\'s. It\'s been relatively
recent, less than the last 24 to 48. So this is why I wanted to just
get.

**\
14:27**\
Ben Guo\
Yeah.

**\
14:28**\
Vrijen Attawar\
Over the week.

**\
14:29**\
Ben Guo\
Yeah, yeah, I know. We rolled out that layout change, like, pretty.
Pretty aggressive or just, like, pretty quickly without enough review,
so. Cool, dude.

**\
14:40**\
Vrijen Attawar\
It\'s cool. It\'s cool. Sometimes you got to break some eggs.

**\
14:44**\
Ben Guo\
Yeah, yeah, exactly. Now\'s the time before we have more users, I guess.

**\
14:48**\
Vrijen Attawar\
Exactly. Exactly. No, it\'s. It\'s. It\'s. It\'s. It\'s a thing. It\'s a
thing. Lord knows that we. The number of times I had this one person
that had done 18 conversations on Careerspan, and then we decided to
deprecate that whole database and whole system of storing it, and were
like, I\'m sorry, you\'re gonna have to paste it back in. I offered to
paste it back in as her account. She was like, no, that\'s fine. But,
yeah, happens. Yeah. So this is so a couple of other things, I guess. So
I listened to your approach to use GitHub, and that part was pretty
good. There\'s going to be more of a conceptual question, I guess.

**\
15:31**\
Ben Guo\
Yeah, yeah.

**\
15:32**\
Vrijen Attawar\
But what I\'ve been effectively trying to do is I initially tried to
just move large chunks over, Quickly realized that was a bad idea, wiped
it, moved over a much smaller chunk, which is why this is, like, a lot
more organized, but only. Only kind of, as you can see, which I guess
I\'ll start there and ask, like, any tips, tricks, good solutions for
files and how much they move around and just generally metamorphose.

**\
16:01**\
Ben Guo\
So you\'re asking, like, your agent is, like, kind of, like, always
moving files around and doing stuff that you don\'t.

**\
16:07**\
Vrijen Attawar\
Want, or is that in the process of doing things like. Okay, I\'ll scope
it down. So, one. A lot of things are created arbitrarily.

**\
16:19**\
Ben Guo\
Yeah.

**\
16:21**\
Vrijen Attawar\
And folders are created oftentimes in places where I don\'t want,
despite there being multiple layers of instructions telling it how to
adhere to a file structure, which I think, again, if that experience is
representative, I would say maybe one of the more challenging aspects
that y\' all will have to solve because, like, people are. People will
find it emotionally difficult if their files are not the same.

**\
16:48**\
Ben Guo\
Right. Yeah. Yeah, for sure. Yeah. It definitely can be a little tricky.
Yeah. That the agent is, like, kind of messing around with stuff and
then, like, maybe putting stuff in weird places. Yeah. Beyond. So, like,
prompting is one way you can also set up kind of, like, cleanup agents
or, like, organizations where you\'ve, like, experimented with the kind
of like, final approach that is kind of like, complex, but it is
possible is you could set up like a service to watch a file. We have a
recipe around that. But you can, like, set the service, like, watch
like, file changes in like, a folder or something. That could be a way
to, like, trigger something to run whenever changes happen. But that
doesn\'t necessarily mean it\'ll get better. It\'ll just like, more
often.

**\
17:42**\
Ben Guo\
So I think I would experiment first with like, kind of a scheduled task
that, like, kind of does clean up, which I imagine you\'ve tried
already.

**\
17:49**\
Vrijen Attawar\
Yeah, I\'ve tried a couple of scheduled tasks. I think this is, this is
all roads are sort of leading to the same conclusion, which is that I
need to. I need to get a little bit more technical. Now, I recognize
I\'m not crazy enough to think that\'s going to happen over a weekend,
so I want to preface by saying that. But I would love to know what are
like, I think you and Ben are actually the perfect or. Sorry, you and
Rob are actually the perfect people to ask about, like, the. How to,
like, take the energy of vibe coding and turn that into a more technical
path forward.

**\
18:30**\
Ben Guo\
You know, I understand the gist of what you\'re saying now. Yeah. So I
think, like, essentially, like, you\'re kind of trying to, like, create
like, an organizational system using, like, files and folders where
there might be like, kind of other ways to represent the same
information that might be, like, kind of easier to manage and. Yeah,
okay, cool. This is definitely true. And one, I guess, like, there\'s
kind of like a range of different options, like tools that I would pull
in my tool belt. I think, like, let me figure out a good place to put
this that is like, maybe I\'ll just write in the slack.

**\
19:09**\
Vrijen Attawar\
Yeah, please.

**\
19:11**\
Ben Guo\
So I think, like, I\'m gonna just like, off the cuff kind of think about
this. But so I think YAML is a good. Is a good format for kind of like
structured, like, single file representation that you might consider
for, like, you can kind of like make a text file, like, more dense and
structured that way. That\'s like, generally useful. CSV obviously, is
like, kind of tabular and like, nice. And then like, kind of like the
bigger hammer would be like, SQLite, which Zoe can definitely, like,
kind of work with. And like, that is probably. SQLite is probably like
the main tool that I kind of like, look to for. Like, I want to organize
some, like, information on my Zoe without it being like, kind of in a
bunch of folders.

**\
20:01**\
Vrijen Attawar\
So this is great because just on like two days ago, I came to the
realization I was like really trying to dig into like the technicalities
of, okay, how does Zoe like edit a document? And I was digging into
like, okay, what can Zo do? It was then that I sort of put it together
that, oh, it will either regenerate the whole freaking thing or I can
give it space. Specific lines is what it said. Or it said start and
bottom is easy if you put stuff at the starter at the bottom. Like,
that\'s what. I\'m sorry. So I\'m at the stage where I\'m starting to
like internalize the transition zone between like LLM behavior and
script code, traditional behavior and sort of starting to see the
boundaries there. So what would be the. What would be like low lift?

**\
20:52**\
Vrijen Attawar\
Like, if I were to say, like, you could have. You could describe someone
as like, oh, they picked up Zoe and then they learned like X, Y and Z
thing. Or like looked at these resources and that was sufficient to self
bootstrap up to a more technical level. What would be your go to
resources? Don\'t say, don\'t say Harvard 50 or CS?

**\
21:12**\
Ben Guo\
No, no. I think CS classes are not really kind of like the right fit.
It\'s a good question. I think I think about this as well. Like, how
there\'s like a lack of material on this, like, particular, like, yeah,
kind of transition because, you know, I don\'t think you need to like
learn all the things, but it\'s like a small chunk of stuff. Like
there\'s like kind of scripting and like file formats and then there\'s
like kind of like just website terminology. Like, what words do you use?
Like, make the site look a certain way. I think it\'s mostly those
categories. I want to offer you just a better resource, but I\'m trying
to think about.

**\
21:54**\
Ben Guo\
I think you said the right thing there, which was that it is about the
boundary of how far you can get with a squishy LLM just doing stuff in a
squishy file format, like a markdown file versus a squishy LLM doing
something in a structured file format like YAML and then a kind of LLM
generating a script to like always do the same thing in a structured
way.

**\
22:21**\
Vrijen Attawar\
Right.

**\
22:21**\
Ben Guo\
Kind of like maximum, like determinism.

**\
22:24**\
Vrijen Attawar\
Right.

**\
22:25**\
Ben Guo\
And like, I think like over time or like, maybe it\'s kind of depending
on what I\'m doing, like, I will like gravitate towards like kind of
maximum determinism because it just like is more stable and easy to
manage, but it can be really Nice to experiment in this like kind of
like squishy LLM mode. Yeah.

**\
22:45**\
Vrijen Attawar\
Right, right. So that\'s, so that is actually immensely clarifying
because then what I essentially need to do is go, I need to look at the
damn code. First of all, I think it was really clarifying to know that
like that Zo not getting that it\'s an LLM is a. Like. Yeah, like
that\'s a. That\'s a expected or like a. An understandable thing given
where it is. It\'s interesting because I just had a conversation around
that where I was asking it was it this one? Undoubtedly this one. This
was generate 15 blocks. Okay. So it generated a bunch of blocks. Okay.
So I provided.

**\
23:27**\
Ben Guo\
Yeah.

**\
23:28**\
Vrijen Attawar\
Okay. This was the one.

**\
23:29**\
Ben Guo\
Cool.

**\
23:30**\
Vrijen Attawar\
If I were to look at where it had that realization. I think it was all
the way at the beginning that it said there we go. It was all the way at
the beginning. So I turned on this mode. It said okay, I\'m going to
look at meeting orchestrator. Worker 1 was done. Okay. Worker 2 is
clean. It found these issues.

**\
23:56**\
Ben Guo\
And yeah.

**\
23:58**\
Vrijen Attawar\
Contains these all. Yeah, sorry, just one second. It was actually.

**\
24:02**\
Ben Guo\
No, no worries.

**\
24:03**\
Vrijen Attawar\
Where I\'ll show you where I was running into Trouble. Launch Worker 2.
Yeah, it has this thing where it has this like section where it
basically says like I guess the ultimate question I\'m trying to ask is
if it\'s a file and there\'s just an instruction in there and I tell the
AI load this file and launch it. I know reasonably that it\'s going to
take that and turn that into instruction and just intuit that I know I
need to like interpret and run that. Then on the other extreme are these
situations where I\'m telling it, okay, this is the functionality I
want. Its base preference seemingly is to make those out of Python,
which is one sort of seems like baseline behavior. You guys have
programming into it.

**\
25:02**\
Ben Guo\
Yeah.

**\
25:03**\
Vrijen Attawar\
The issue that I interact with there is that it will choose to rely on
regex based scanning for things or regex based rules which are a little
bit. Which like because I\'m vibe coding I\'m not in a discipline enough
fashion handling file names and stuff. Right.

**\
25:20**\
Ben Guo\
Totally. Yeah.

**\
25:21**\
Vrijen Attawar\
So that I think is where the problems start. And then effectively so
then at some point in my process I\'ll realize that and I\'ll say okay,
no, actually this, this part you need to use a large language model and
I think that\'s where it will like these screw ups will happen. Right.
It\'s in that process where in on some occasions it will remember that
it\'s a large language model and just generate stuff. In other
situations, it will expect a script or not see a script and make
something up or. You know what I mean?

**\
25:50**\
Ben Guo\
Yeah, yeah. I think like, one. One correct tweak that I would do to your
verbiage is when. So you probably shouldn\'t, like, kind of tell it to
use an LLM because I think that will just confuse it.

**\
26:01**\
Vrijen Attawar\
Interesting. Okay.

**\
26:02**\
Ben Guo\
Yeah, So I think I\'m trying to think about, like, the way that I
instruct my.

**\
26:07**\
Vrijen Attawar\
So.

**\
26:12**\
Ben Guo\
I think, like, you might kind of, like, tell it to, like, use its own
internal training data or like, kind of. I guess, like, basically for
me, the kind of dichotomy of Zoe is either it can use a bunch of tools
on your computer and do a bunch of tools to accomplish something, or it
can draw on its internal knowledge and ability to process things to
transform something into another thing. And yeah, I guess I try to be
pretty explicit about when I wanted to draw from internal knowledge and
output something or do not call tools or just do this transformation
from this thing to another thing.

**\
27:02**\
Vrijen Attawar\
So the transferable insight there, the tactical transferable insight
there is that. Just tell ZO to do it, as opposed to telling it to, like.
Yeah, go to, like, a large language model because that reinforces the
externalization of the large language functionality. As opposed to,
like.

**\
27:25**\
Ben Guo\
Yeah, it\'ll, like, try to, like, write a python script to, like, call
like, OpenAI or something, which probably is not the right thing to do.

**\
27:32**\
Vrijen Attawar\
Right, right, right, right. See, this is the kind of stuff that is,
like, so fascinating. Oh, my God.

**\
27:39**\
Ben Guo\
Yeah, yeah, it\'s. That\'s a trip for sure. I mean, even for me, you
know, it\'s. It\'s a. It\'s like a new system for anybody, really. This
whole ZO thing, it\'s a. I. I really.

**\
27:50**\
Vrijen Attawar\
I wanted to have, like a. I was. This would be sort of as an interesting
aside. So I\'ve been, like, planning out the demo, right? And I want to
make it, like, something really fucking sweet. So I\'m, like, trying out
different sort of like, ideas in my head. But one thing that I came up
with was like, trying to convey to people, AI is magic, but it is magic
in the. I\'m trying to think of the author is. Is magic in the tradition
of an author, where magic is. It\'s like a very fickle magic system,
right? Or it\'s a magic system where, like, it is on the hard or soft
side of, like, magic systems or like, sci fi. It\'s on the softer,
squishier side.

**\
28:35**\
Vrijen Attawar\
And so trying to communicate to people that if you try to learn AI, you
will apply a rule based approach to a fundamentally non rule based
thing. And I would encourage folks to. And so it\'s funny that you said
that because that\'s also what I wanted to communicate to people is when
you engage with though, build an intuition for how ZO thinks and works
and like learn to treat it, not saying treated like a person, but
treated like an entity that has like attributes and preferences and like
you\'re learning to work with something, you\'re not trying to like
program something.

**\
29:12**\
Ben Guo\
Yeah, no, everything you\'re saying is very right. Like I think what
you\'re saying really applies to working with any kind of like AI
agentic system. And yeah, it\'s about like kind of like surfing on the
wave of its like.

**\
29:26**\
Vrijen Attawar\
Yeah, that\'s exactly how I describe it. It\'s a, it\'s a feel sort of
thing.

**\
29:32**\
Ben Guo\
Yeah.

**\
29:32**\
Vrijen Attawar\
Which is why I think Vibe X took off so much because I think it\'s often
under addressed the degree to which it is a feel, intuition sort of
thing. Yeah, I think our pathy tries to like convey that, but people
just. Yeah, wrong.

**\
29:50**\
Ben Guo\
Totally. Yep. Yeah, there\'s a time and a place for like vibe stuff and
yeah, that was trying to be like the best place for vibing on a lot of
things. Yeah. I\'m back to your question about kind of like just like
what is like the verbiage vocabulary missing? Like I do want to like
think about this more. I\'m trying to think about like your system,
which I think I have like a pretty clear picture of. And like what are
like the words that like I would like communicate to your Zoe or like to
you on behalf of Russo. And it\'s like. So I guess like I, I see what
you\'re doing is kind of like building like kind of like a personal CRM.
And I think Zoe probably like knows about that.

**\
30:33**\
Ben Guo\
It sounds like you kind of have like a queuing system of some sort that
ZO has set up, which there are different approaches and like we should
probably have like stronger opinions on like what the best approaches.
But whatever you have probably works. Yeah. This idea of workers that
you have is pretty interesting. I think in the standard kind of
programming sense a worker is quite simple. Even a scheduled task in
your ZO is a form of worker that just kind of does the same thing and
picks up the things that are on a queue of jobs that it has to do. So I
imagine that you have set up a system where your Zoe kind of, like, kind
of like, searches for, like, what\'s on the queue and, like, stuff.

**\
31:19**\
Vrijen Attawar\
Precisely. Precisely. Because that\'s. That\'s my. That\'s my, like,
framework for how to get really high order. It\'s like. It\'s like the
mills of God grind slow. Sort of like, if you can slow process or slow
cook this information through Zoe, you end up using, like, less. Like,
there was a point where I kind of, like, flubbed the system, but there
was a point where I was consistently getting like 8 out of 10, 9 out of
10 out of 10, like, meeting content just on an iterative basis. So when
it, like, sets up right, and it runs, it actually runs really well
because you can. The amount of close control you can have at each, like,
step is phenomenal. But I think that\'s where maybe even I need to
start.

**\
32:10**\
Vrijen Attawar\
Like, you know, just, you know, sacking up and, like, effectively just
diving into the code. Right. And just saying, like, it.

**\
32:17**\
Ben Guo\
Yeah.

**\
32:17**\
Vrijen Attawar\
It\'s funny, at this point I see, like, little snippets and I can
actually interpret it.

**\
32:22**\
Ben Guo\
Yeah.

**\
32:22**\
Vrijen Attawar\
I probably shouldn\'t, like, feel so shy about just opening up the
actual file and, like, taking a look at it, trying to learn it.

**\
32:30**\
Ben Guo\
Totally. And so can also kind of explain stuff to you. Yeah, yeah. So
the job queue is the thing. I\'m just kind of like off the cuff saying,
like, if I were to do this is me, it\'s the only way, or, like,
whatever. But this is, like, kind of what comes to mind for me. I
probably would have, like, told Zo, like, set up a job queue in a
particular way.

**\
32:53**\
Vrijen Attawar\
What is. What is the way that you would have set it up? Like, yeah, I
have many more situations where I\'m going to need to do that.

**\
32:59**\
Ben Guo\
Totally. Yeah. I might try this thing called hui, which is just a really
simple Python job queue thing that so could definitely. I\'ll put. I put
it on our slack already.

**\
33:09**\
Vrijen Attawar\
Oh, nice. Amazing.

**\
33:10**\
Ben Guo\
And I\'ll just. Up there. I think that could work well. Another kind of,
like, still kind of like undocumented, but like a thing that so can do
when it writes scripts. And it\'s probably doing this for you already,
but who knows? But it can invoke itself from, like, code, so it can call
the ZO API, essentially call itself to do something, and then, like,
it\'ll, like, return that to itself and to the program, like the text
output.

**\
33:42**\
Vrijen Attawar\
How would that be different from the. From the LLM call tool that you
had Referenced earlier.

**\
33:48**\
Ben Guo\
Yeah, yeah. So this is in the context of like a script or like any kind
of code that Zoe writes, it can call Zoe, which sometimes can be useful.
We haven\'t developed this a ton yet, but you can do pretty primitive
things. You could tell Zo to. In Python context, you could call the Zo
API with the command like send me an email with this text and it\'ll do
that.

**\
34:17**\
Vrijen Attawar\
It will then send something to Zoe that Zoe will interpret agentically.

**\
34:21**\
Ben Guo\
Exactly, yeah.

**\
34:22**\
Vrijen Attawar\
Oh, that\'s so powerful.

**\
34:24**\
Ben Guo\
Yeah. Which is very nice. So that could make things generally for you
like probably a little more deterministic if you wanted.

**\
34:31**\
Vrijen Attawar\
Right, right. Because that\'s the thing, right? It\'s the intersection
of this like deterministic, not the boundary of those two worlds where
like a lot of my fuck ups happen. Yeah, this is really good. It\'s good
to know if I wanted to like move from just like, what do you call it,
just vibe coding and Zo to like something where there\'s an actual like
something closer to cursor, which I say not even having ever really
logged into cursor or like vaguely knowing that it\'s more of a, like
it\'s closer to generating the code than just like do this. What would
be a step in that direction via Zoe or in a way that would help me move
in that direction constructively?

**\
35:19**\
Ben Guo\
That\'s a good question. I would actually play around with this telling
Zoe to write scripts to call itself. You could probably start that up,
open the Python file and it\'ll be really simple and see what\'s going
on. And you can start with a really simple one. Just write me a script
that will email me some text and then maybe.

**\
35:42**\
Vrijen Attawar\
Yeah, yeah.

**\
35:44**\
Ben Guo\
So that it can like take an email as input and it can just email. I can
use the script to email anybody with like some text. And then you can
like there\'s this concept of like parameterizing stuff in code in
scripts where you can like kind of basically like extract things that
are like static into like kind of dynamic inputs. Like you say like make
the email a dynamic input or like. Right, right next of the email like a
dynamic. And then you can like kind of reuse the script and like kind of
use it as a utility in other places.

**\
36:15**\
Vrijen Attawar\
So you just have this like little box and you can just say, hey, go do
this complex thing, come back, put it in my box and it just ends up in
there.

**\
36:24**\
Ben Guo\
Yeah, yeah. So that\'s one good thing to experiment with.

**\
36:27**\
Vrijen Attawar\
That is a very Clear thing that I can do to. I can see how that will
like dramatically. That will clean up a lot of trouble actually, because
that will be a very standardized way that I can build off of stuff. I
mean, this is really exciting.

**\
36:47**\
Ben Guo\
Nice. Yeah. The other thing that I would maybe get you to try is trying
to use SQLite more in your workflow.

**\
36:54**\
Vrijen Attawar\
Yeah.

**\
36:55**\
Ben Guo\
SQLite and YAML, I think, yeah, those in combo could probably just be
pretty powerful.

**\
37:02**\
Vrijen Attawar\
What\'s the. What\'s the distinction between. Or in this context, is
there a reason to go with YAML vs JSON?

**\
37:13**\
Ben Guo\
Yeah, it\'s a subtle distinction. I find that YAML is like a little bit
easier for LLMs to write a proper YAML.

**\
37:21**\
Vrijen Attawar\
Okay.

**\
37:21**\
Ben Guo\
There\'s not so many like curly braces that it has to close and like
quotes that has to like reason about. There\'s like not as much syntax
around it.

**\
37:31**\
Vrijen Attawar\
Right.

**\
37:32**\
Ben Guo\
Makes it a little bit easier for alums to like. I mean, I think alums
can generate pretty good JSON at this point. Maybe I\'m just like burned
by like past dumb LLMs. I usually reach for YAML.

**\
37:43**\
Vrijen Attawar\
I completely get that. In fact, I use JSON because of how much I\'ve
heard my head of AI complain about how it\'s a bitch and a half to get
AI to spit out like consistently good JSON adherent, sort of like
output. So that makes that sort of tracks. Okay, YAML makes sense. And I
can see how even because I can, I\'m able to like think of the YAML text
I\'ve seen last and yeah, it\'s just a step closer towards like human
readable. Right. Vs JSON is maybe on the more computer readable side of
the equation.

**\
38:16**\
Ben Guo\
Totally. YAML is super simple. Yeah, it\'s just like the key and then a
colon and then like the value and. Yeah, it\'s. And then like
indentation, like kind of marks nesting of structures and.

**\
38:26**\
Vrijen Attawar\
Yeah, love it. Okay, I think I can make that switch. That\'s a really
good tip.

**\
38:31**\
Ben Guo\
Yeah, I think it\'s just like good to think about and maybe try in like
a really small context. But it can be a really good way to like, for
example, if you have like a bunch of like stuff in different places, you
can like kind of like index or create like an index of your stuff in
SQLite, for example. So like that maybe could help so like kind of like
find stuff faster. They could just like do a Query in the SQLite
database.

**\
39:00**\
Vrijen Attawar\
That makes. Yeah, I should do. Because you know what? I actually. Funny
you should Say that actually just the other day, set up this and it\'s
already come in pretty handy.

**\
39:14**\
Ben Guo\
DB.

**\
39:17**\
Vrijen Attawar\
Oh, you already have one.

**\
39:18**\
Ben Guo\
Okay, great.

**\
39:18**\
Vrijen Attawar\
Oh, sorry, this is in. But yeah, but I had it for a very specific use
case that I bring up because I actually think it would be relevant to
your. I think it would be highly relevant to your thing as well. Your
user, or like the broader user base was essentially this functionality
where I get it to initiate an entry to a conversational database every
time I open a new conversation and that it maintains in that database.

**\
39:53**\
Ben Guo\
I remember you said this. Yeah, we should just expose this conversation
stuff to Zoe. Like, I know that you\'ve kind of worked around it in. In
this way, which is really cool. But. Yeah, that. That\'s important to
do.

**\
40:06**\
Vrijen Attawar\
Yeah.

**\
40:08**\
Ben Guo\
Try to do this. Yeah.

**\
40:09**\
Vrijen Attawar\
Yeah. Because this was. This has made so like just being able to index
this and it. Actually, this is. Ironically, this is the only part of ZO
where I\'ve actually managed to make this, the system work. But, you
know, it will like, Great. Essentially track all that. Yeah. So it\'s.

**\
40:24**\
Ben Guo\
Yeah, that\'s awesome.

**\
40:25**\
Vrijen Attawar\
Yeah, I can see how now what you\'re saying is that just use that same
structure for most, if not all of my files. Right.

**\
40:33**\
Ben Guo\
Yeah, I think it\'ll be nice because. Yeah, many benefits. That\'s like.
So can, like, migrate stuff. You can like, it can like, basically be
your DB admin and like, if you, like, want to change stuff in the
database, like, the way it\'s stored or like, it\'ll probably be able to
help you kind of keep things more structured and. Yeah, it\'ll be easier
to like, do a lot of queries on top of data. Yeah.

**\
40:58**\
Vrijen Attawar\
Love it. Love it. Yeah, I can do that. Those are really good unlocks.
Any other sort of like, packages or it\'s. It\'s. Or like APIs or like
any other. Just like, things that are very basic in your. I\'m almost
thinking, like, world because I\'m not in the culture.

**\
41:15**\
Ben Guo\
Yeah. I guess like, one other unlock that, like, I use sometimes that
might be useful is when I want to, like, integrate something that like,
so we don\'t support on. So, like, as like a connection. I will, like,
tell Zoe to walk me through writing a script to call it, like, what\'s
everyone, like, integrate with the Twitter API or something. I\'ll tell
it to basically write a basic script that has different functions that I
want from the Twitter API and then it\'ll probably walk me through how
to get an API key. I\'ll put that into my. So Secrets and just walk with
Zoe through kind of getting it running and testing it. And then once
that works, that becomes basically a tool that so can use.

**\
42:02**\
Ben Guo\
I could also tell it to give me instructions on how to use this for
yourself and then rule or something. Right now, another way to do this
is like if once you have, like, a script that does something, you can
add it to a prompt in your prompts folder and you can just say, like,
call this tool. So sorry, it was kind of rambly, but.

**\
42:28**\
Vrijen Attawar\
No, go ahead.

**\
42:29**\
Ben Guo\
That we added. That\'s kind of useful for you. This is also kind of
fresh off the. Out of the oven is. There\'s a prompts folder in Files.

**\
42:38**\
Vrijen Attawar\
Oh, sick.

**\
42:39**\
Ben Guo\
And this is like, what recipes used to be. Oh, it\'s migrated.

**\
42:43**\
Vrijen Attawar\
Okay.

**\
42:44**\
Ben Guo\
Interesting.

**\
42:45**\
Vrijen Attawar\
Yeah.

**\
42:46**\
Ben Guo\
It hasn\'t been updated yet. That\'s possible.

**\
42:49**\
Vrijen Attawar\
Maybe I.

**\
42:51**\
Ben Guo\
Interesting.

**\
42:52**\
Vrijen Attawar\
Is there a manual update?

**\
42:54**\
Ben Guo\
Let\'s wait. Let\'s click on your recipes. Okay. Right. Okay. You
didn\'t make any recipes yet.

**\
43:04**\
Vrijen Attawar\
No. So this is what. What\'s happened here is I. God damn it. So I. I
think the demonstrator account is probably going to show it better,
right?

**\
43:15**\
Ben Guo\
Oh, yeah.

**\
43:16**\
Vrijen Attawar\
Cool.

**\
43:16**\
Ben Guo\
Great. Yeah.

**\
43:17**\
Vrijen Attawar\
So I have a section, but it\'s. I\'ve been having trouble migrating it,
which is the other thing. Like, I\'m kind of stuck in this weird place
where, for example, I wanted to move all of the command docs that I had
into recipes, and actually when I moved it into commands, it was fine.
But then moving it into recipes has been a bitch and a half.

**\
43:36**\
Ben Guo\
Oh, interesting. Yeah. Well, now they\'re called props. I\'m sorry.
There\'s like, a vinyl migration.

**\
43:43**\
Vrijen Attawar\
That\'s fine. That\'s fine. I\'m just gonna skip recipes then.

**\
43:46**\
Ben Guo\
Yeah, yeah. But it\'s a prompts folder now.

**\
43:50**\
Vrijen Attawar\
Hey, quick question. Can I ask. Was it because you guys realized the
cooks would get, like, you would basically have no cooks on. On, so.

**\
43:59**\
Ben Guo\
Yeah. Yeah, I think we. It\'s just, like. It was a little too, like,
cheeky, I guess. Yeah. The props. Like, what it is. Yeah. Just wanted to
call it what it is without trying to be fancy around it.

**\
44:12**\
Vrijen Attawar\
Call it what it is. I love it. Still here for it. No, that\'s. That\'s
fair. Okay, so I should watch out for that folder. Is it.

**\
44:20**\
Ben Guo\
Yeah. So you can just like, make things in the prompts folder. I guess
you have some. So, yeah, let\'s click one of them, like, list workflows,
maybe. Cool. Okay, great. Yeah. Okay, so let\'s. Let\'s click that plus
button over there or one of the pluses. On. Sorry. On. In the top. In
the kind of front matter, like below. Sorry, sorry.

**\
44:45**\
Vrijen Attawar\
Oh, below the front matter. Yep.

**\
44:46**\
Ben Guo\
Yeah, yeah. You can add a tool field.

**\
44:52**\
Vrijen Attawar\
Okay. Tool.

**\
44:56**\
Ben Guo\
Cool. And then now you can turn it on and this will make it a tool that.
Like that. So we\'ll now know about.

**\
45:05**\
Vrijen Attawar\
Cool.

**\
45:06**\
Ben Guo\
You kind of get it now.

**\
45:07**\
Vrijen Attawar\
Yeah, yeah.

**\
45:09**\
Ben Guo\
Sick.

**\
45:09**\
Vrijen Attawar\
Okay, okay.

**\
45:10**\
Ben Guo\
Okay.

**\
45:11**\
Vrijen Attawar\
This changes stuff.

**\
45:12**\
Ben Guo\
Nice. Nice. Okay, cool. This is going to be helpful for you probably in
different ways.

**\
45:20**\
Vrijen Attawar\
It is. Good job, guys. This one\'s a banger.

**\
45:25**\
Ben Guo\
Nice. Sweet. Yeah, I guess back to what I was saying. If I wanted to
give Zoe a Twitter tool, I would first make it write the script that
does all this stuff and then write a prompt that documents how to use
the script and then like put that in the content. And then I would have
to like describe the tool in the description field and be like, use this
tool when I say I want to, like, call it Twitter API or something.

**\
45:49**\
Vrijen Attawar\
Yeah, okay. Okay. Sweet. Sweet. Okay, that sounds good. In the last
couple of minutes, I know we\'re approaching close to time, but there
were a couple I wanted to send your way. You guys have a lot of untapped
potential with EdTech, I feel.

**\
46:09**\
Ben Guo\
Yeah, and I think so too. Yeah.

**\
46:12**\
Vrijen Attawar\
Yeah. And I. So me and my co founder, if anything, especially Logan, but
our networks are like strongest in ed tech. So ed tech is sort of always
back of the mind. There\'s a group called the Future of Higher Education
group, really High Signal Community. I actually posted about Zoe there
earlier. You should. You should like. I mean, it\'s another group.
Right. But like you. Yeah, yeah, check it out. You can use Logan in my
name. You\'ll absolutely get in, obviously. But the. There\'s a lot of
folks out there that are in universities. In fact, I can\'t believe I
didn\'t think of this. Tiff should probably, if she wants to like engage
with university folks, that would be a good place. Place to get in.

**\
47:01**\
Vrijen Attawar\
And one of the things I was trying to convey to her and part of the
problem with selling to higher ed is they don\'t have any money. And the
people that care about what you have to offer have no power generally.

**\
47:15**\
Ben Guo\
So it\'s a.

**\
47:15**\
Vrijen Attawar\
It\'s a to sell to. But the good thing about higher ed is one thing they
always have money for is classes. So we learned this after a year of go
to market. Right. Is that nothing career or like extraneous has money,
but they have dedicated money set up to do classes. So what I\'m working
towards is if you could Find universities or professors that are willing
to introduce Zoe in their class. You could probably also not only like,
make money off of those licenses, you\'d actually start embedding it in
environments. Because one thing these universities are looking for is
classes where people could do that are like converting. Right. Like, how
do you make people AI native?

**\
47:58**\
Vrijen Attawar\
So around a like strong Zo is like making AI natives through its system
through like giving you something that\'s like 10x as powerful as like
anyone else does. Like, you could. You could probably get a lot of play
in that direction. And yeah, I think it was promising and I think
there\'s a lot of folks that would be keen to speak to you guys about
that.

**\
48:23**\
Ben Guo\
Neat. Neat. Yeah, very cool. Yeah, I\'ll apply. I\'ll look for the slack
and fly to join it.

**\
48:28**\
Vrijen Attawar\
Yeah, yeah, check it out. Just something to get you noodling on.

**\
48:31**\
Ben Guo\
No, no, appreciate it. Yeah. And yeah, I think like kind of after this.
Well, I know that I said initially that like, I didn\'t want to do like
kind of regular sync with you, but I would like to like. I think it\'s
like you\'re a power user and I get a lot out of like, just like. I\'m
glad, man. No, totally. Yeah, I would love to. I guess we want to like
do it at a scheduled time or like whatever works for you.

**\
48:52**\
Vrijen Attawar\
Yeah, yeah, whatever. Whatever works. I\'m totally game. Yeah, I. I
absolutely love. I was on a call with Ben yesterday and it was like very
like hearing him describe some of the things that you guys are like
facing. It was like very reminiscent of us as well. The main thing I
concluded was he was describing how it\'s like how hard it is to not
sell to everyone when you have a truly general purpose, like all
powerful tool. And you know, our product is not comparable to Zoe in
that sense, but certainly the. Everyone is relying on the resume and
we\'re trying to normalize like conversation and conversation as data
entry and like this mental model is the data structure. Right. And so it
was also very hard to be like, do we focus on product managers?

**\
49:42**\
Vrijen Attawar\
Well, that feels like such a compromise because everyone could benefit
from self advertising, you know? Yeah, it was hard. It\'s. It\'s hard.
And everything in the world tells you to like, niche in.

**\
49:53**\
Ben Guo\
That\'s true. Yeah, yeah, we\'ll see. Yeah. At least we\'ll start as the
general tool and hopefully stay that way, but.

**\
50:00**\
Vrijen Attawar\
Yeah, yeah, no, it\'s. It\'s fun, man. It\'s. It\'s cool times. What are
you. What Are you excited about sharing on the, about the demo on
Wednesday?

**\
50:13**\
Ben Guo\
Yeah, I guess for me I\'m probably going to do a version of our launch
video content, just the intro, just test it out and trial the flow of it
and then get into showing the product in different ways. Yeah, it\'s a
good opportunity actually. Good timing to practice that flow and figure
out the actual demos that really make drive it home quickly.

**\
50:41**\
Vrijen Attawar\
Yeah, I, I had an idea and I\'m so okay with you taking it if you like
it, but just saying. Yeah, I had this idea of like Zoe is very. Zoe\'s
non visual in the sense that it\'s not a eye catching visual for this
record. Another parallel that our products have, right?

**\
51:05**\
Ben Guo\
Totally. Yeah.

**\
51:06**\
Vrijen Attawar\
And in a demo context we very much struggled with demoing our product
because it\'s like a lot of it is a slow burn process of like seeing
things come up. So I was essentially going to like try to set, I was
gonna set the deck up to like help me succeed on this. But essentially
like start with a one shot command and like a one shot recording and
essentially just set Zo off or set a couple of Zoes off and just like
talk theory as it\'s like running.

**\
51:36**\
Ben Guo\
Yeah.

**\
51:36**\
Vrijen Attawar\
You know, like a one shot sort of thing. Because I think that\'s really
where people see the power is like if it just gets done, you know. So
I\'m gonna try to work towards something like that over the weekend and
this so many things you mentioned today are gonna make things
deterministic enough to pull that off. So I\'m very happy.

**\
51:56**\
Ben Guo\
Amazing. Cool. Yeah, I\'m glad. Yeah, yeah. I also, I love the idea of
like kind of like live generating something while talking and then like
coming back to it and seeing what happened.

**\
52:05**\
Vrijen Attawar\
Yeah, yeah. I think, I think it\'s the appropriate level of flex in this
situation. So let me dig into some of that. I\'ll send you a demo as
well if I get something early.

**\
52:17**\
Ben Guo\
Cool. Yeah, yeah. And yeah, always feel free to hit me up for any of the
channels.

**\
52:21**\
Vrijen Attawar\
Thank you my man. I appreciate it.

**\
52:24**\
Ben Guo\
Yeah, cool. See you man.

**\
52:26**\
Vrijen Attawar\
Happy Friday. Bye bye.

**\
52:30**\
Ben Guo\
See you.
