**\
00:01**\
Vrijen Attawar\
Sweet. Let me actually show you as a start stuff that I have going for
on auto. So this was the demo I was trying to do. This is part of
effectively a process where it will ingest a transcript from Google
Drive, it will generate a follow up email according to this tool. So
I\'ve actually found that their prompt tool calling is quite good. It
pretty reliably sort of executes on that. You\'ll also notice this vibe
operator mode on or Persona on which I\'ll provide context for in a
second. But effectively what it does over here and you see here
generating these B blocks. This has probably been the most used feature
I\'ve had is being able to generate these little B blocks automatically
that have like my custom version of like how I like meetings analyzed.
What is the strategic context?

**\
01:11**\
Vrijen Attawar\
Like what is the. What were some of the key moments from the call that
resonated like who said what? So setting up this kind of a pipeline,
even one which has something like this like a really solid. You know,
hopefully you don\'t know the underlying but hopefully you can even tell
just through the writing. It\'s like way more personalized than. Than
most. Most things out there. Yep. So you know a lot of what.

**\
01:41**\
Aaron Mak Hoffman\
Are you pulling in as context to write that?

**\
01:44**\
Vrijen Attawar\
So the.

**\
01:45**\
Aaron Mak Hoffman\
The outside of the meeting information.

**\
01:48**\
Vrijen Attawar\
So that is where I maintain and what I\'m trying to sort of develop is
this idea of there being basically the raw information, a middle layer
if you want to think of that as a content library. And then on the
farthermost side there\'s like knowledge base.

**\
02:07**\
Aaron Mak Hoffman\
Yep.

**\
02:08**\
Vrijen Attawar\
I almost think of it as like the knowledge base are my sacred texts.
They\'re the ones that like is the highest level that information should
reach arts from sort of the bottom or sort of upstream I guess if you
want to think about it and is raw data and it like processed at
different stages such that it distills and there is this like central.
So what you see over here is this like central understanding of who I
am, you know. So like it has context for like how I engage with LinkedIn
and I use this tool called Condo. So it has context for that. Or I have
these like go to market hypotheses that it was compounding for a while.

**\
02:51**\
Vrijen Attawar\
So this I didn\'t really manage to get it working super well but
effectively like every day or so it would identify like what were the
lessons learned around go to market today. Stack that like append onto
this file and then.

**\
03:08**\
Aaron Mak Hoffman\
Are you doing that with your writing as well?

**\
03:10**\
Vrijen Attawar\
I am. So with writing what I basically more so have done is I\'ve set up
a system where it. How do I best illustrate this? So actually it would
be illustrated over here, right. I have this like voice system where
effectively what it should have done over here is not working optimally
is it should have switched to the Vibe writer Persona to write the
follow up email. So that\'s my like best use case for Personas is like
different lenses and if you build in switching into your Personas, you
can have it like organically switch for you along the way.

**\
03:51**\
Aaron Mak Hoffman\
So are the Persona switches reliable?

**\
03:56**\
Vrijen Attawar\
They can be made more reliable with explicit instructioning within the
Persona to switch on the appropriate occasion.

**\
04:05**\
Aaron Mak Hoffman\
Okay, so the Personas can automatically switch because I. I\'ve only set
them up to manually switch them and I didn\'t know if you could add a
specific Persona to a prompt, for example. You can.

**\
04:20**\
Vrijen Attawar\
Yeah. So you would effectively. Let\'s see how it built it out for me. I
mean I\'ve been like really when I say vibe coding, I mean like I\'ve
rarely been looking at the underlying which is starting to catch up with
me now. But let\'s see. Vibe Builder. Oh, is this just commands now?
Okay, that\'s okay. Vibe Builder, let\'s see. Okay, because this is file
search now. Okay, so like this mode, this is version 2.0 supposedly. So
so the builder Persona is like meant to be like hey, this is what
you\'re supposed to use when you are building out any code in within
Zoe. So it has like all of my standards and stuff. But one second.
Persona Vibe.

**\
05:18**\
Aaron Mak Hoffman\
Yeah, that\'s interesting because for me I\'ve found that having a
repository of prompts that are doing that work for me, like here\'s how
you use the meta API, here\'s how you write a replication prompt,
here\'s how you distill a category of distillation, like a process. So
I\'ve sort of put all my processes that I do on a repeatable basis as
prompts and then embedded those into rules or agents if they\'re running
recurrently. If it\'s a rule though that I\'m doing spontaneously. Yeah,
I found that to be really reliable versus trying to put in the Personas.
Is there a reason why?

**\
06:06**\
Vrijen Attawar\
Oh, I see where the.

**\
06:08**\
Aaron Mak Hoffman\
Because like you can\'t pull out of a Persona, so.

**\
06:11**\
Vrijen Attawar\
Oh, I think I see where the disconnect is. So I do the same thing that
you do with regards. So same things that you\'re describing with regards
to having like the stuff embedded in rules. Right. Where you actually
want to have Your. I\'m trying to think of an example like this one, I
think like references specifically or it has embedded. Some of them have
embedded within them the prompt file itself. So it pulls the file and
sort of calls it, which is where I have go to prompts. Like, I think
we\'re doing roughly the same thing. What I like about the Persona is
that it\'s more of like a perspective on the underlying. So Vibe
Operator is meant to help navigate the file system and it sort of has
like shortcuts.

**\
07:05**\
Vrijen Attawar\
So it has like a copy of the system file, like the system map. You know,
it has like these little things that make it better for navigation
versus one that\'s better for building code where you can give it
general principles. Like one. One problem I\'ve run into a lot is the AI
will forget it\'s an AI and it will like, act like. It will constantly
be asking for, like external API keys in order to. One second here.
There we go. That\'s much more normal. It\'ll sort of ask for external
API keys constantly, when in fact you can just. You have to like, tell
it or at least in my experience encourage it. Like, hey, just interpret
it. And you will be able to solve the answer. Like, you know, you\'ll be
able to get whatever you want.

**\
07:54**\
Vrijen Attawar\
And so putting that in the Vibe Builder Persona has led to like, some
improved performance. Like, stuff like that is what I stuff into the
person.

**\
08:03**\
Aaron Mak Hoffman\
Okay.

**\
08:04**\
Vrijen Attawar\
Yeah. And then it\'s fun to see it, like, switch along the way. So if
it\'s like, hey, use the researcher Persona to look this stuff up. The
other one that\'s been really useful is Vibe Teacher. Because if
there\'s something I don\'t know, I essentially tell the Vibe Tutor the
Vibe Teacher, hey, like, for me, becoming more technical is a priority.
So I can switch into Vibe Teacher and say, hey, actually, can you, like,
explain what just happened or what you just did or what you just built
and it will switch to that mode and sort of explain it to me.

**\
08:35**\
Aaron Mak Hoffman\
Nice.

**\
08:36**\
Vrijen Attawar\
Yeah. And how.

**\
08:37**\
Aaron Mak Hoffman\
Yeah. Can I see how they are automatically switching? Yeah.

**\
08:42**\
Vrijen Attawar\
So it is basically the.

**\
08:47**\
Aaron Mak Hoffman\
Thing inside of. Is that a rule or is that a setting inside of.

**\
08:52**\
Vrijen Attawar\
There\'s both. There\'s rule. There\'s a rule related to switching
where.

**\
08:59**\
Aaron Mak Hoffman\
It\'S like, if I\'m asking to be taught explain something, use this
Persona.

**\
09:05**\
Vrijen Attawar\
Yeah. So for example, this one\'s saying, switch back to Vibe Operator.
Report completion, execute switchback. Right.

**\
09:14**\
Aaron Mak Hoffman\
You can\'t link it explicitly.

**\
09:17**\
Vrijen Attawar\
You can\'t link it explicitly. You can just give it the Persona key, I
guess. Or the Persona id, and that tends to help. Then there should be
another one that says. Yeah, there you go. Okay. Oh, this is a unique
one that I was like trying over the last few days is like a vibe level
upper, which I need to find a less clunky way of saying it, but is
effectively like when I\'m stuck trying to debug something or
troubleshoot something and. Or like I\'ve just built something and I
want like a new perspective on it. I have a Persona that\'s specifically
oriented to sort of like asking like, contra, you know, counterintuitive
questions or like take like an opposing stance or an adversarial stance
or something like that. Just as a way to like spark some more creativity
out of the machine.

**\
10:08**\
Aaron Mak Hoffman\
Nice.

**\
10:10**\
Vrijen Attawar\
So that I\'ve found has been quite interesting as well. But. Yeah.

**\
10:16**\
Aaron Mak Hoffman\
And then is there any customer facing things that you\'ve done with Zoe?

**\
10:21**\
Vrijen Attawar\
Not yet, no. Yeah, it\'s a little. It\'s a little. It\'s just not ready
for prime time enough to like, worry about putting in front of
customers.

**\
10:31**\
Aaron Mak Hoffman\
Yeah, I found the, you know, I\'m very tempted to pipe my client
communications through Zo and have just a site, a Zoho site that they
are messaging through so that I can just get everything via text and
just text my clients via textile and everything like that. And they get
a nice, like, little area where they can go. But I\'ve been a little
scared. I\'m like, I don\'t know yet.

**\
11:00**\
Vrijen Attawar\
It\'s a little, it\'s a little tough, like, especially depending on how
much you\'re touching the underlying like, code, which I\'m not. I\'m
like, really not.

**\
11:13**\
Aaron Mak Hoffman\
Yes.

**\
11:13**\
Vrijen Attawar\
Is. It is very touching, is very touch and go, I think in a lot of
contexts. But I mean, to the extent that like, it is. It\'s good enough
to make like a serviceable system where the level of personalization
overrides the clunkiness of it, like, not working right every single
time, you know.

**\
11:37**\
Aaron Mak Hoffman\
If the use case is leaning into that, you know.

**\
11:40**\
Vrijen Attawar\
Yeah. And I love the like for me. Pardon me, the like, this use case of
even just like this stopped working a few days ago. And so I have yet to
fix it. But like, you know, there was a point where it was like running
through my emails and like capturing essential information and actually
like populating the CRM.

**\
12:15**\
Aaron Mak Hoffman\
Yeah.

**\
12:16**\
Vrijen Attawar\
On a pretty consistent basis. So like, getting stuff like that spun up
and ready to work is good. I think another problem with theirs is that
like, if you build Up a lot of technical debt. It is a absolute
untangle.

**\
12:29**\
Aaron Mak Hoffman\
Yeah, I. I learned that lesson doing stuff in Replit, so I\'m. I\'m,
like, very aware of that. And my planning phase is, like, three times
longer than the build phase, but it allows me to reduce a lot of that
garbage.

**\
12:43**\
Vrijen Attawar\
How do you plan? Like, I would love to learn some, like, best practices,
because I kind of just dove in. But, yeah, without putting the pressure
of best practices, obviously. Like, what are your. What are things that
you\'ve found to be, like, more helpful in getting consistent Vibe
coding done?

**\
13:03**\
Aaron Mak Hoffman\
Yeah, for me, like, there\'s two categories. There\'s replacement stuff,
which is all, like, what I would say is, like, you know, built for. For
massive amounts of people and data. And then there\'s stuff I\'m doing
in Zoe. Right. So, like, I don\'t know if you checked out the website I
built, but that was, like, just Vibe coded inside.

**\
13:24**\
Vrijen Attawar\
Though.

**\
13:27**\
Aaron Mak Hoffman\
And that was, like, pretty chill. Like, essentially what I did was,
guess.

**\
13:33**\
Vrijen Attawar\
I can\'t close out of this.

**\
13:37**\
Aaron Mak Hoffman\
Is I have all of these different things that I hoard, right? My
playlists, my principles and beliefs, my recipes.

**\
13:49**\
Vrijen Attawar\
Love it. Love it.

**\
13:51**\
Aaron Mak Hoffman\
Right. And they all have a simple database and a readme that I can use
to. This is huge. I can always take control if I need to and understand
the technical if I need to. When I make a Vibe code, like a Vibe prompt
to code something, I\'m always having it make something that I can
understand along with it so that if I need to, I can grab this document
and give it to the AI and say, hey, I want this, and I can actually,
like, take control versus just having it spit out this crazy prompt that
I\'m just like, it has a bunch of code and I just dump it in the AI and
I don\'t really know what\'s going on.

**\
14:41**\
Vrijen Attawar\
So what do you tell it when you ask for these readmes? Like, do you
basically tell it like, hey, one of your grounding principles is to,
like, always make content, always include, like, a readme or something
like that. Like, what was the tactical implementation?

**\
14:55**\
Aaron Mak Hoffman\
Yeah, it\'s, you know, I want to implement this, go out and research it,
look at these files that have already planned previous steps or other
features or other parts of it. So it has some understanding of the code
base. Because I also don\'t link it to GitHub. That\'s like, the next
level for me is like having Zoe and Replit all pointed to the same
GitHub, but that\'s a little bit scary for me. So I\'m still like
putting it all in docs, but I\'m essentially like, hey, go gather all
the stuff, make his plan. And I always have it planned before I write
stuff. I look at the plan because it\'s always a natural language. I\'m
like, oh, you went too far here. This you missed, blah, blah.

**\
15:38**\
Aaron Mak Hoffman\
And then I\'ll say, okay, now write a technical implementation document
and a readme that a non technical person like myself understand if I do
need to go into the code base at some point. And it does a wonderful
job.

**\
15:53**\
Vrijen Attawar\
Wonderful. That is such, that\'s going to be such a huge unlock. That\'s
such a like nice and elegant way of sort of like breaking it down. It\'s
like you have the paper trail.

**\
16:05**\
Aaron Mak Hoffman\
Like it\'s just like your stages of like in between compression and then
ultra distilled compression. It\'s the same concept with the code. It\'s
like full insane PRD that I\'m never going to look at into the agent to
code. And then my middle compression, which is essentially all my
planning docs, so it covers all in natural language, the different
features, the different UI stuff, the different integrations. And then I
have the readme which is like my ultra distilled version that I can
always.

**\
16:38**\
Vrijen Attawar\
How do you maintain synchronous? Like how do you maintain sync between
what the system is doing in the technical docs? Like do you find that it
forgets to update the technical docs or do you keep the, do you have
like safeguards in place to prevent that?

**\
16:53**\
Aaron Mak Hoffman\
So if I\'m understanding you correctly, like.

**\
16:59**\
Vrijen Attawar\
Like you\'ll make a change to the underlying process, let\'s say yeah,
but.

**\
17:04**\
Aaron Mak Hoffman\
But like underlying code in replit, for example.

**\
17:07**\
Vrijen Attawar\
Yeah, yeah. So like let\'s say you make a change to the script or even
on Zo, how do you make sure that it knows to then update the technical
doc saying hey, this was the change that I made, I just prompt it.

**\
17:22**\
Aaron Mak Hoffman\
So that\'s sort of the advantage of me like trying to keep everything in
docs is like for example my big behemoth app is this one and in it I\'ll
have. Have different things. So like for example this is like the
massive PRD that like go through all the technical stuff that I\'m not
really going to read and I\'m always linking that inside of ZO to create
something like a build prompt. So for example this is like stage one
compression where it\'s really laying out the plan and I\'m having it
reference all these other planning docs that I\'ve already made. So for
example, you can see here like I have creative strategist portal
experience, deep dive and it\'s all about just the experience and the
features in natural language, how it should look and feel and function.
This zero technical stuff. Editor portal, same thing.

**\
18:25**\
Aaron Mak Hoffman\
Media buyer portal, same thing. Then I can just add these as context
inside of Zo instead of the massive dump of stuff that I had before this
stuff to implement the technical doc, which would be this, then this I
create the final doc, right?

**\
18:47**\
Vrijen Attawar\
Which is like so the build prompts are always your starting point when
you\'re trying to do something of that nature in your system so that it
has a consistent grounding point and then you proceed from there.

**\
19:04**\
Aaron Mak Hoffman\
Say that one more time.

**\
19:05**\
Vrijen Attawar\
So you when you\'re about to build something, yeah. It will start by
adding one of your pre established build prompts plus whatever you\'re
trying to achieve there and build out that plan and then have the.

**\
19:21**\
Aaron Mak Hoffman\
AI implement it if it\'s the same project, Right. But if it\'s.

**\
19:26**\
Vrijen Attawar\
Oh so okay, so you maintain that on a per project basis.

**\
19:29**\
Aaron Mak Hoffman\
Yeah, exactly. So if it\'s a new thing, for example, when I first
started this, all I did was loading company context, right? That\'s how
it started. So context, problem solution, workflow and processes and
then like the specific integrations that I want. I wrote this pretty
much all manually and gave it to Zoe and said hey, like start thinking
of how to actually put this all together, right.

**\
19:59**\
Aaron Mak Hoffman\
And then from there I went through and nitpicked things and added both
of both the company context and this, which is what I came up with and
said okay, in a new chat, with just these two docs added, let\'s build
out the creative strategist portal, just the experience itself so I can
understand as non technical person what it will feel like look like and
I will be able to then direct it and say hey, actually we don\'t need
this feature. Hey we actually need this. And you missed it. It builds
out all those. Then from there again new chats for each one of these
portals with clean context. I\'m then going into the next stage which is
like the super technical. Well even more granular than that is. I broke
it up into stages. Build stages.

**\
20:53**\
Vrijen Attawar\
Interesting.

**\
20:56**\
Aaron Mak Hoffman\
But essentially it\'s like here\'s what\'s the best way to then build
this? Right, Because I can build it all.

**\
21:03**\
Vrijen Attawar\
At once and you\'re building the same thing again and again. Is that
right? Like you\'re building different variations of like the same app?

**\
21:11**\
Aaron Mak Hoffman\
No I\'m building one massive app that runs our entire company.

**\
21:15**\
Vrijen Attawar\
Oh, wow. Okay. Okay.

**\
21:17**\
Aaron Mak Hoffman\
And they all have these different portals and different features and
workflows. I mean, this is like a full blown wow.

**\
21:23**\
Vrijen Attawar\
So you\'re using Zoe to create the code for that app, is that right?

**\
21:28**\
Aaron Mak Hoffman\
Yes, I\'m using it to create the structure of the code. Replit Agent is
really creating the code. Right. It\'s going in and writing everything.
I want to use Replit Agent for this super advanced stuff because it has
guardrails with the way that they built their lang graph and it can
integrate with its hosted system because it\'s all in the cloud and do
all that. So I don\'t actually have Zoe write the actual code. I have it
just the structure of the code.

**\
22:02**\
Vrijen Attawar\
Right. Which plays to its strengths as well as like a storage and like
PKM sort of system context.

**\
22:09**\
Aaron Mak Hoffman\
Like pulling in all that stuff at the right time, in the right amount of
distillation is like key to then be able to go into replit with clean
prompts and know it\'s all going to be built out. Like, I didn\'t have
this two months ago and I was building a bunch of internal apps and it
would take. Talk about technical debt. Like it would take, you know, 40
to 60 hours to build something. That now takes me three. Because I am
just using the context in the right ways in the planning stage to
distill down the most perfect, well thought out plan I could possibly
have for how to construct the app and then just handing it over to repl
it. And it\'s purely executing.

**\
22:51**\
Aaron Mak Hoffman\
I find Replit it can\'t talk about agentic like shortcomings, like it\'s
still not there when it comes to recalling the right things at the right
times, using the right reference docs, when it needs to like pulling all
that context together itself.

**\
23:08**\
Vrijen Attawar\
Not even need to set it up for success for it to be successful.

**\
23:12**\
Aaron Mak Hoffman\
Yeah, I need to do the hard work, which is not that hard because of like
pulling in the right context and building the strategy first outside of
Replit. Because it\'ll just like, yeah, it\'ll do what it can do best,
but it\'s trying to do everything all at once. And I find with vibing
anything right, you want to break it up into manageable sections.

**\
23:35**\
Vrijen Attawar\
Yeah, yeah, absolutely. Hey, one technique that might be cool that
you\'d be interested in. Yeah, that I can show you and then I may have
to jump. But that I think you\'ll find super interesting is. So I set up
Zoe to And I\'d made a comment about this to Shirley on the discord, but
essentially set up this thing in Zoe where I have. So the start of each
conversation, it will initialize session state, which is essentially a
file that I\'ve instructed it to generate within its workspace. Because
what you can then do is, I think it\'s conversations DB what you can
then do is maintain a database of every single conversation that you\'ve
had and. And like, what it was about, what the discussion was about. So
this is.

**\
24:38**\
Vrijen Attawar\
I think my oldest ones were still a little glitchy, but it tells you
where the state file is.

**\
24:46**\
Aaron Mak Hoffman\
So is there a reason why this is better than just leveraging the chat
history natively with rag?

**\
24:54**\
Vrijen Attawar\
So this. With rag, Mostly because I found this to be a lot more reliable
than just telling it, hey, five conversations ago or a couple of
conversations ago, I discussed xyz, which I think having it maybe a
little further in just to see. Yeah, yeah. So some of these, I think
some of the null ones are like the agent triggering. But effectively
this. All of this effort then, is to then allow for. What do you call
it? Let me show you an example, this idea of a build orchestrator. So I
effectively set it up to. Every time it plans something out to
essentially create these little worker files and track all of them in
the orchestrator workspace.

**\
25:55**\
Vrijen Attawar\
So this becomes like an organizing sort of agent, and it spins off new
conversations that can then be tracked through that database in a more
reliable way. So through that sort of tracking, I\'m essentially able to
say, oh, pull out all the conversations where we discussed X, Y and Z,
and it is going to be able to look somewhere concrete, sort of reference
all of that in a more consistently reliable way than just like kind of
the stochastic, like, throw of, you know, toss in the air. That is like,
retrieval in most cases.

**\
26:32**\
Aaron Mak Hoffman\
Yeah, yeah, because that\'s super interesting. I found that I just have
an agent that runs every day and just goes into my chat history for the
last 24 hours and updates a database.

**\
26:46**\
Vrijen Attawar\
Oh, interesting.

**\
26:47**\
Aaron Mak Hoffman\
Just query that database directly anytime I want. But it won\'t. It
won\'t, like, allow me to find necessarily that chat history, but I\'ll
be able to extract anything that I needed from it. Right. So, like, for
example, like, updating things I\'m working on my website, I just want
that to happen without me having to do anything. And so it\'ll go in,
pull those things into the database, and then I have another agent that
is running daily that will go into that Database. See the things that
I\'m working on and update.

**\
27:18**\
Vrijen Attawar\
Oh wait, could I. Cool. Could I see that on your website?

**\
27:20**\
Aaron Mak Hoffman\
Yeah, yeah, you can see on my website.

**\
27:22**\
Vrijen Attawar\
Do you mind linking me up?

**\
27:25**\
Aaron Mak Hoffman\
Yeah, it\'s just my project\'s timeline. It\'s just very. It only also
like can see what I\'ve done in Zoe, which I\'ve only been in Zoe for a
month or two.

**\
27:40**\
Vrijen Attawar\
That\'s so cool. Hell yeah.

**\
27:42**\
Aaron Mak Hoffman\
This is so like all these things will like automatically update.
They\'ll shut off as inactive if they haven\'t been in my conversation
history for the last month and allows it.

**\
27:53**\
Vrijen Attawar\
So cool. You basically set up a database to look at everything you\'re
talking about and then place it in these categories and then boost it to
your website.

**\
28:05**\
Aaron Mak Hoffman\
Yeah, different. Different databases for different things. Right.
Because like I use Zoe with texting a ton. So like, because it\'s so
convenient. So I\'ll like text it. Hey, like, you know, share this
playlist and it\'ll put it on my Spotify playlist database, which will
then automatically push to my Zoe site. Right?

**\
28:25**\
Vrijen Attawar\
Yeah.

**\
28:26**\
Aaron Mak Hoffman\
Then there\'s things that are more dynamic, like the projects I\'m
working on where I don\'t want touch it, I don\'t want to text Zo when
I\'m updating, when I\'m changing what I\'m working on. Instead it\'s
just pulling from that chat history database automatically and. And
updating the site, you know.

**\
28:40**\
Vrijen Attawar\
Gotcha, gotcha. Very cool. Dude, this was so interesting. I really
appreciate you. You shown me that same. Yeah.

**\
28:50**\
Aaron Mak Hoffman\
So real quick. So Zo can create new chats and close conversations, like
by itself.

**\
28:58**\
Vrijen Attawar\
So not yes and no. I\'ve been asking them. I believe it can because
it\'s like definitely error spawned like shitloads of conversations for
me.

**\
29:10**\
Aaron Mak Hoffman\
Okay.

**\
29:11**\
Vrijen Attawar\
So I know it\'s possible. I\'ve even had. Yeah. And I\'ve even had some
crossover. So all of this BS that I\'m doing was actually inspired by
the desire to do that was to have it trigger new conversations so that I
can just spin off a worker and have five threads run in a row. Do you.
Do you find that it like stalls a lot on long agent runs?

**\
29:34**\
Aaron Mak Hoffman\
Just in the last day, really.

**\
29:37**\
Vrijen Attawar\
I get a lot of stalling.

**\
29:39**\
Aaron Mak Hoffman\
Yeah. Just in the last day and a half or so. I will say I really want
them to do parallel chats. So you can have multiple chats running at
once.

**\
29:48**\
Vrijen Attawar\
Yeah.

**\
29:49**\
Aaron Mak Hoffman\
I don\'t know if that would help for you too. But like for me, like I
set up a bunch of APIs to do external workflows, and sometimes they\'ll
take 30 minutes to run. And I don\'t want to. I want to move on to a new
conversation zone, keep doing stuff. But I.

**\
30:01**\
Vrijen Attawar\
You never have multiple conversations at the same time.

**\
30:06**\
Aaron Mak Hoffman\
It\'ll stall for me. If I switch to a new conversation and submit
another query, it\'ll stall the old one.

**\
30:14**\
Vrijen Attawar\
Okay, so that explains why I have been having such a bad time, because
I\'m always rotating between three conversations.

**\
30:23**\
Aaron Mak Hoffman\
It\'ll stop it if it\'s mid query.

**\
30:26**\
Vrijen Attawar\
Yeah, gotcha. Okay. So I guess it\'s able to do that to a minimal
extent, and I\'m just constantly pushing it to its limits, which is why
it\'s crashing on me so much.

**\
30:37**\
Aaron Mak Hoffman\
Yeah, I think so. I sent that in as, like a feature request. I was like,
yo, parallel. Parallel is so nice, especially for long ride and stuff.
Like I do, you know?

**\
30:46**\
Vrijen Attawar\
So nice. Yeah. And I actually reckon you can get away with too, because
what I generally do is I have one version. What I observed is that if
you\'re not watching it, like, if you don\'t have that open, it will
stall out. Yeah, that\'s.

**\
31:00**\
Aaron Mak Hoffman\
That\'s been my experience as well.

**\
31:02**\
Vrijen Attawar\
Yeah. So I just keep one browser open, one window open, like an ad. Like
the desktop app open like an ass.

**\
31:08**\
Aaron Mak Hoffman\
Holy. I mean, that\'s one way to do it.

**\
31:11**\
Vrijen Attawar\
That\'s what I mean, dude. The. The. Sometimes the old ways are the. The
best way.

**\
31:16**\
Aaron Mak Hoffman\
Holy. That\'s. That\'s so crazy.

**\
31:19**\
Vrijen Attawar\
It\'s actually. It\'s so funny you should say that because now I\'m
thinking, like, I\'m a maniac. I have. There are times where I have
multiple times zo tabs open at the same time, and I\'m just. Honestly,
just like crop. Rotating between them. Just reactivating them.

**\
31:34**\
Aaron Mak Hoffman\
Yeah, that\'s what I do with replit.

**\
31:36**\
Vrijen Attawar\
Oh, is that really? Yeah, yeah.

**\
31:38**\
Aaron Mak Hoffman\
If I\'m working on different projects, like, I\'ll have to rotate them
like that, so. No, you\'re not. Not crazy. What\'s crazy is that Zoe
just doesn\'t let you do that.

**\
31:46**\
Vrijen Attawar\
Yeah. What\'s crazy, really, is that because that\'s where our instinct
is. Right? Exactly. Yeah. That\'s like, what it is. Aligned with user
expectations. Dude. So cool. I got a run for an event, but this was
awesome. Thank you for your time and, yeah, always good chatting.

**\
32:02**\
Aaron Mak Hoffman\
Thank you.

**\
32:03**\
Vrijen Attawar\
Yeah. Catch you soon.

**\
32:04**\
Aaron Mak Hoffman\
All right, bye.

**\
32:06**\
Vrijen Attawar\
Ciao.
