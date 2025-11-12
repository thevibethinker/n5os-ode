**\
00:02**\
Vrijen Attawar\
Hey, Elaine.

**\
00:04**\
Elaine P\
Hello.

**\
00:05**\
Vrijen Attawar\
Hey. Lovely to meet you.

**\
00:07**\
Elaine P\
Yeah, likewise. Thanks for your time. I was really impressed with Howie.

**\
00:12**\
Vrijen Attawar\
Thank you. Yeah, Howie is pretty good. And then I have a layer of magic
of my own on top of that. It works pretty seamlessly in my hands at
least.

**\
00:24**\
Elaine P\
Is Howie an app that it\'s already been created?

**\
00:28**\
Vrijen Attawar\
Yeah. So Howie itself is a fantastic product by this guy, Austin
Petersmith. I\'m a pretty heavy user of Howie, but it\'s a, it\'s like
an AI. It\'s an email based AI assistant that helps with scheduling and
then there are some optimizations that I\'ve developed for myself that
make it a lot more seamless than the average user. So that makes it feel
a little bit more seamless than normal.

**\
01:01**\
Elaine P\
Right, right, right. So then are you a self taught coder?

**\
01:05**\
Vrijen Attawar\
So, you know, maybe a month ago I wouldn\'t have said that, but over the
last month at least a big part of sort of what where we\'ve been taking,
honestly just the journey Logan and I as co founders have been on has
seen us move more towards building out sort of MVPs of our own. We have
an amazing product that we have built and ready, but we are frustrated
at having to sell out to sell the product a little bit as far as bending
to the desires of hiring or of talent. And so it\'s a long story, but
we\'re basically trying to build out our brands as sort of individuals
because we have a deep expertise in AI and careers and productivity and
use that to fund the product and sort of bootstrap instead of trying to
go down the VC route.

**\
02:00**\
Elaine P\
Right. Interesting, huh? So you have a team that\'s already created your
product.

**\
02:08**\
Vrijen Attawar\
Yeah. So we\'ve basically built a AI career coach that uses
conversational coaching to help you develop your professional story. So
it helps you articulate your experiences, helps you think through
things, and then it consolidates that into a centralized understanding
of who you are that can be flexibly leveraged to match you to jobs,
match you to networking opportunities. Some of these bits have yet to be
built, but for the most part the coaching and the central sort of
matching engine has been built out. So, you know, it\'s a great product,
but you know, in our heart of hearts, we don\'t want to charge
candidates and then that made us go to employers because if you\'re not
going to charge candidates, you have to charge employers. But frankly we
don\'t want to be selling to employers.

**\
03:00**\
Vrijen Attawar\
We would rather just have a product that we know is amazing out there
and figure out a way to monetize because the data that we\'re collecting
is incomparable. The granularity, the level of insight, the things that
you can do with the data that we\'re collecting. Because we spent a lot
of attention and time knowing what data were going to capture before we
set up the pipeline to the individual to chatbot pipeline that\'s led to
us having a much more robust matching system on the back end.

**\
03:37**\
Elaine P\
It sounds like you probably already leveraged RAG technology.

**\
03:42**\
Vrijen Attawar\
We actually have gotten incredibly far without even having to use rag
because what we and this would honestly also be, my advice is if you can
effectively navigate how you comp like RAG is a major and finicky
undertaking. And so what I would say is if you can emulate RAG and build
out an MVP that has through a combination of elbow grease and like
clever scripting, can sort of emulate that rag ness. I think that would
be a sort of better approach because that\'s something that we spend a
lot of time thinking about. And I think it was the right decision to go
more lightweight because it also allowed us to I think just be a little
bit more constraining with ourselves about how we deployed AI. And I
think in the long run that kind of discipline leads to a more consistent
output.

**\
04:41**\
Vrijen Attawar\
A lot of folks will just say, okay, let\'s throw a state of the art
model at it. Let\'s run Sonnet 4.5. Well, Sona 4.5 costs 20 to 40 times
as much as the models that we use to produce equivalently sophisticated
conversational behavior. We use DPT 4.1 and little bits of DPT 5.1 mini
to actually achieve what we do. That\'s been our philosophy.

**\
05:14**\
Elaine P\
I was going to ask you if you\'re using LLM, you\'re using deep, is.

**\
05:19**\
Vrijen Attawar\
That the deep we are using? Essentially we\'re primarily using OpenAI
models. But if you\'re familiar with the distinction between reasoning
and non reasoning models, we are essentially using reasoning. We\'re
creating a chain of individual steps that all use the very cheap non
reasoning models. But if you arrange the steps in the right way and code
it to go from step to step effectively, you can simulate much more high
complexity behavior at a fraction of the cost. And you can feel free to
look this up. But the big thing that hasn\'t caught up to the market as
far as the economics of large language models is that all of a sudden
software doesn\'t scale. The economics don\'t scale in the way that
traditional software has. Right now there\'s a cogs associated with all
LLM output.

**\
06:16**\
Vrijen Attawar\
So to an extent, if you\'re working with a great AI engineer, what they
will do is build an MVP that uses the dumbest possible AI to build and
use design patterns that accommodate the dumbest possible AI that they
can get away with. Because that is a much more thoughtful and resilient
way of developing your AI infrastructure.

**\
06:44**\
Elaine P\
Yeah, that\'s interesting. Well, couple of thoughts. One, I have made
like three or four career pivots.

**\
06:52**\
Vrijen Attawar\
Oh, yeah?

**\
06:54**\
Elaine P\
Yes.

**\
06:55**\
Vrijen Attawar\
Your.

**\
06:55**\
Elaine P\
Your area is something I\'m very familiar with. I\'ve always struggled
with that. I\'ve kind of probably picked up on brand only the last two
years about what is my brand. It\'s hard. And I think even the last two
years the job market has changed so much. So I\'m. I\'m not even sure.
But yeah, I think. Long story short, I lived overseas for eight years,
so when I came back, I lived in. I worked at international schools. So
Saudi Arabia, Korea, South Korea.

**\
07:29**\
Vrijen Attawar\
I went to international school in. I went to international school in
Bangladesh. I went to an IB school.

**\
07:35**\
Elaine P\
Oh, did you? Yeah, I work at IV schools.

**\
07:39**\
Vrijen Attawar\
Yeah, yeah. It\'s not often you meet an IB person in the us. It\'s a lot
rarer on these shores. Yeah.

**\
07:46**\
Elaine P\
Or anyone who\'s been overseas, period.

**\
07:48**\
Vrijen Attawar\
Exactly, exactly. Yeah. So it\'s. It was. Yeah, no, Logan is my co.
Founder and I, we actually met in Singapore a decade ago.

**\
07:56**\
Elaine P\
Oh, nice.

**\
07:57**\
Vrijen Attawar\
Yeah. So that\'s where. So we also had. I\'m originally from India, so
technically overseas right now, you know, sort of moved to the US for
college and then moved to Singapore in my 20s for work and did that for
a couple of years. It was career coaching essentially. And so we\'re
extremely motivated by the idea that, you know, we\'re extremely
motivated by the idea that hiring is deeply broken and all the
incentives are set up for everyone to fail together. And so to the
extent that we think a better way is possible, I think previously we
thought, okay, we build the product and then we preach.

**\
08:36**\
Vrijen Attawar\
And I think now our sort of strategy as of today, frankly, is let\'s
preach about what needs to be different and, you know, build our
identities and our brands around that because that\'s something that we
intuitively sort of do well. My co founder, myself, well, she does it
well. I don\'t know about myself, but she does it well. And yeah, we
just want to. I think that\'s going to be a much more powerful sell, is
sort of selling our expertise and stuff. And, you know, we\'re not
pretty, we\'re not shabby. At the kind of output or the content that we
create either.

**\
09:09**\
Elaine P\
Well, I think to my point too is probably the change in AI. So, yeah,
AI, whether it\'s. I started with OpenAI, I think I\'m using CLAUDE now
in Gemini. So open AI, you can create your own project and that\'s where
you can upload all your files. And so, yeah, that\'s basically a RAG
concept. So I would try.

**\
09:32**\
Vrijen Attawar\
So they\'re literally using rag.

**\
09:34**\
Elaine P\
Yeah, I would upload all my different resumes because I made so many
pivots and all this. And so I would try to ask, okay, you\'re me now,
you know, what should I be selling myself? But for some reason it would
still. Still not work well. I think it was still always generic.

**\
09:50**\
Vrijen Attawar\
Right. I can tell you why it doesn\'t work well.

**\
09:54**\
Elaine P\
Okay.

**\
09:55**\
Vrijen Attawar\
Is that it\'s going to be relevant to you in case you\'re trying to
learn more about large language models. So, you know, large language
models are. I\'m just going to ask. I don\'t mean to ask it to be
condescending. I just want to make sure I understand where your sort of
level of understanding is. So you\'re familiar with stuff like context
windows, you\'re familiar with stuff like the kind of probabilistic
nature of large language models, how they aren\'t actually thinking.
Right. So with all of that said, the. Effectively, the view that we have
of like large language models is that they are good enough in the hands
of someone that knows how to work them or not. They\'re good enough.
They\'re incredible. They\'re good enough in the average person\'s hands
for some tasks or most tasks.

**\
10:42**\
Vrijen Attawar\
But the vast majority of people can\'t produce great work with AI. AI
isn\'t so good as it actually gets you there. It is deceptively bad,
actually at what it does. And so I think the essence of developing a
good sort of AI system is how do you give it enough context to produce
great output in what you did, you were just giving it resumes, which if
you think about it, are a very narrow slice of who you are. Right. It is
what, a decade, two decades worth of like experience, whatever it may be
compressed into a page, two pages, that is years compressed into maybe
25 to 30 lines. Right. That is a very narrow surface level view of many
major experiences. The career stand approach is opposite. We make you
talk, we take your resume and we do that extraction semantically.

**\
11:35**\
Vrijen Attawar\
But then we also make you talk about your experiences deeply. And when
you talk about your experiences deeply, there\'s Nowhere to hide. You
actually get a lot more context and you get the interrelationship
between skills and qualities and attributes, which is what\'s important.
Right. It\'s not your ability to do project management per se that
affects your ability to do project management or to be a good project
manager because there\'s 101 other adjacent skills that a good
combination of those skills would make for a good project manager at a
particular company. And that\'s the problem that we\'re trying to solve
is this sort of multi point matching problem where we have to
incorporate the requirements of the job that are fuzzy, the requirements
of the individual and the team which are also fuzzy, and the background
of who someone is, which is also fuzzy.

**\
12:28**\
Vrijen Attawar\
So it\'s a very sort of long story short, the reason that ChatGPT
doesn\'t work is because it\'s shallow data. And no matter how good
their tech or their large language model is, when it doesn\'t have that
context and it isn\'t specialized to make the most of what it has, it\'s
always going to be generic. But you know, I can show you what our
product produces and it is astounding. You know, it literally rewrites
word for word because a generic AI, because it doesn\'t know you, its
only options are word substitution rephrasing. But it can\'t go more
specific. Right. It has to maintain the same level of genericness or
become more generic to be compatible with the truth. Especially if you
tell it to not hallucinate. I\'m sure you noticed the moment you told
it, don\'t make anything up, the results got way worse.

**\
13:15**\
Elaine P\
Right, Right.

**\
13:18**\
Vrijen Attawar\
So it\'s there in case you\'re interested. I actually love learning
about large language models, so there\'s a lot of resources I\'m happy
to share that are sort of really great intermediate to advanced
resources. But yeah, no, it\'s a fascinating topic and obviously you can
get me talking about it all day.

**\
13:39**\
Elaine P\
Yeah, no, I am pretty impressed with how much you know. So yeah, if you
could share in your resources, of course. My point, my point too is
you\'re probably smart about avoiding RAG because the transformation of
PDFs, the text extraction is really hard. So I guess your code does a
really good job in extracting those.

**\
14:04**\
Vrijen Attawar\
Yeah, yeah. I mean, even with text extraction, like there is, if you
think of it as like a body of text. Right. What are the levers? Okay, I
have a large body of text. I can break it into small chunks, process
smaller chunks at a time and then stitch it together. Or I could do the
whole chunk together, but then I\'m spreading the cognitive points
across a lot of information. In the previous example, I\'m concentrating
the cognitive points on small bits of information, but I\'m losing the
broader context. Right. I could use a more powerful model that has
bigger brains and more cognitive points to spare, or I could break it
down into smaller parts and use a dumber model that makes it cheaper. So
all of those levers are actually the variables that you have to
consider.

**\
14:47**\
Vrijen Attawar\
But there are some design patterns that are perhaps more optimal in the
early stages than others. And to the best of my knowledge, in most
situations, going dumber, simpler, stupider. The, like the best test.
And are you non technical?

**\
15:05**\
Elaine P\
I. I guess I am technical.

**\
15:08**\
Vrijen Attawar\
Sorry.

**\
15:09**\
Elaine P\
I.

**\
15:09**\
Vrijen Attawar\
The reason you\'ve done three career switches. You got to take a second
to think about it.

**\
15:16**\
Elaine P\
No, it\'s a bit of imposter syndrome. So, yeah, no, I, I started in the
semiconductor industry. So it\'s making the chips, right, that\'s
powering all this. And then I went to overseas to work at international
schools. And then when I came back to the U.S. i. I worked in the
software industry. Program project manager. But my point with that too
is like, well, no, the last two years, because programming. I don\'t
know if you heard of Makerspace. I\'ve always been involved with
programming, but Cursor has been really empowering where I can actually
develop software. Right.

**\
15:55**\
Vrijen Attawar\
Don\'t let fucking anyone tell you otherwise. I think the reality is
that, look, as I was saying earlier, in 9 out of 10 hands, AI is doing
more harm to that person\'s ambitions than good. Right? But if you are
willing to be humble and disciplined and apply AI effectively and learn
about the design patterns and the techniques and the processes that make
for good AI development, then, and heck yeah, anyone can do it because I
just built out a project. I finished building it in about three weeks or
so. It\'s about 200,000 lines of code, is an extremely dense chunk of
functionality that I spent a lot of time and thought. In many ways,
it\'s the culmination of over a year\'s worth of effort or thinking or
learning. But that is something that, you know, we would have never been
able to be.

**\
16:52**\
Vrijen Attawar\
We wouldn\'t have been able to be developers in that sense. Right?
There\'s actually a really cool tool I use called Zoe that I\'m actually
an ambassador of. So I\'m not getting a huge financial. I\'m not getting
really any financial kickback from this. I just get like a higher
discount when I promote Zo But Zo is incredible. It\'s a tool that I. I
haven\'t ever sort of like, been an advocate for any tool or an active
supporter of any tool. But Zoho is an incredible product that I use
literally every day. So it\'s another cool, very empowering thing for
folks like you and me that are on the edge of becoming more technical
because of what AI allows us to do.

**\
17:40**\
Elaine P\
I\'m trying to look it up, check it out in one sentence. How would you
describe it? Zoe is a personal computer.

**\
17:48**\
Vrijen Attawar\
It is a computer in the cloud that you control by prompting.

**\
17:55**\
Elaine P\
So it\'s a computer in cloud. So like a laptop functionality.

**\
17:59**\
Vrijen Attawar\
It is literally like a laptop. You can prompt it to connect to an API,
you can prompt it to set up folders in root, you can prompt it to set up
automation for. I mean, hey, you want to check this out? This is going
to blow your mind. This is what I spent the last two weeks building. 1/2
Share this tab instead. So this is. I actually was just showing off to
my co founder. So this is what I\'ve sort of built out in Zoho. This is
Zoho. You know, I\'ve built out basically a personal operating system.
So I have like all of my files, all of my background, everything like
that stored away over here. And then I have these automated processes
that run that do all sorts of background processing for me.

**\
18:50**\
Vrijen Attawar\
So just to show you an example, hopefully this one ran correctly right
now. So I just got off of a meeting, right? So I had a meeting with
Michael Maher. So this will have. If it loads correctly, this should
have processed my meeting and generated a transcript. Let\'s just see if
it\'s.

**\
19:17**\
Elaine P\
Meetings.

**\
19:24**\
Vrijen Attawar\
Boom. There we go.

**\
19:25**\
Elaine P\
Go.

**\
19:30**\
Vrijen Attawar\
Second. Okay, so let me actually show you this. So what you can do with
Zo, for instance, is define your own commands or define your own set of
instructions, and then basically set them up as like individual markdown
documents. So I have a specific instruction for, I don\'t know, doing
partial. There we go. So adding a daily digest, right? I can just call
this instruction and it will spin up a daily digest that accesses
everything from my email that has a specific workflow associated with
it. It validates the design, it generates the script, and it implements
it in a way that is specific to the operating system that I\'ve crafted
within. So this is basically just a. It basically just gives you a Linux
device in the cloud and it says if you want to create a folder, prompt
the AI.

**\
20:56**\
Vrijen Attawar\
If you want to make one folder, talk to another, prompt the AI and so if
you have an intuition for software architecture, you can build something
very complex in a way that to me is way more intuitive than Zapier or
any of that stuff.

**\
21:11**\
Elaine P\
Stuff, yeah. You were just probably leading to my thought too. It\'s
like I heard you say convert to markdown. So it actually can take any
sources and convert them.

**\
21:25**\
Vrijen Attawar\
Yeah, yeah. To get it to do it reliably, I would author a command and
then set up a command system so that it reliably runs that. So the
problem is the same issues that happen with AI happen with Zoe. Right.
Where it has a limited context window. If you don\'t tell it, hey, these
are the files to think about. It\'s not going to think about them.
Right. So you have to create a system where it always knows what the
next step is. And I\'ve done that through a combination of setting up
some documentation, files, meetings. Yeah, here it was, career span. So
let\'s show you this. Right. Deliverables. So these are all the
commands, but I\'m trying to find a. Let\'s see Wisdom. I know which one
to go to. Yeah, here we go. Yeah.

**\
22:33**\
Vrijen Attawar\
So like this Wisdom Partners meeting, I was able to generate a
stakeholder profile automatically. So every time I meet with someone,
like when I meet with you, it will automatically generate the
stakeholder profile after our call. Based on the things you said in this
call, it\'s going to identify your background, what your strategic value
is or relevances to career Spanish, what kind of insights came up in my
conversations with you? Every time I talk to you, it will automatically
update this. So you can do some like really cool stuff with Zo if you
sort of set it up correctly. I have honestly spent maybe my cat\'s
surgery\'s worth of money and tokens trying to set this up, but it\'s
totally worth it now actually, frankly, I\'m.

**\
23:26**\
Vrijen Attawar\
Once I perfect this, I\'m actually thinking of charging maybe somewhere
between a thousand or two thousand dollars to help build this for like a
custom implementation for someone. So that\'s where I, you know, that\'s
my sort of like short term plan to start making some money immediately
is to essentially sell access to this.

**\
23:47**\
Elaine P\
Yeah, no, it\'s interesting because now I feel like there\'s a lot of
tools but like Otter AI would just literally take the transcription,
like whatever said, and then output it. This is like the next step of
developing a profile. I think that people would say you can do that in
LLMs. But the drawback with LLM is probably, like you said, the Scope
would be too narrow. So even if we upload all the emails of a CEO, or
because I heard this example that they took all the emails, his
presentations, and they were able to develop his Persona and so they can
predict his style. But I think they leverage LLM. But.

**\
24:33**\
Vrijen Attawar\
All of it leverages LLMs for sure. Like the example I was going to show
you. Let me see if I have a good example of a meeting. Like, for
example, when you\'re saying leveraging LLMs, you could dump everything
into projects and try to do it. But the difference is this is agentic
right over here, it says, hey, let me check pending requests and let me
load requests at every step. There is a reason why it\'s looking at
these specific files. I\'ve built out the infrastructure so that at each
step it knows, okay, now I need to generate this block. Now I need to do
this. Now I need to do this. Have you tried Zapier? Has it ever really
worked for you?

**\
25:18**\
Elaine P\
No, because I think it\'s not free. Right.

**\
25:22**\
Vrijen Attawar\
Zapier can be free. Most folks. Ultimately, even though it\'s marketed
as like very accessible most people, I have yet to find someone that
really uses it outside of, like on web forums, because everyone I\'ve
heard that\'s tried it absolutely hated it and didn\'t end up using it.

**\
25:39**\
Elaine P\
Okay, okay.

**\
25:41**\
Vrijen Attawar\
That\'s not to say it\'s a bad. By the way. That\'s not to say it\'s a
bad tool or you can\'t use. I don\'t want to discourage you from using
Zapier if that\'s the best technical option for you. I\'m just saying
that for my brain and the way it works, this seemingly more complex
thing was more intuitive to set up than Zapier, which I\'ve spent like
hours of my life on Zapier and gotten nowhere.

**\
26:04**\
Elaine P\
Yeah. Is Zapier the one that uses blocks that you can.

**\
26:08**\
Vrijen Attawar\
Yeah, there\'s a bunch, but Zapier is probably the most famous one.

**\
26:12**\
Elaine P\
Okay. When you mentioned you wrote like 200,000 lines of code, did you
use cursor or something?

**\
26:23**\
Vrijen Attawar\
I did it all within Zoho. So that\'s the cool part.

**\
26:26**\
Elaine P\
Are you serious?

**\
26:27**\
Vrijen Attawar\
Yeah. So this is all self contained within though, so everything you
need from the LLMs, like look at the bottom, I can select whichever LLM
I want and call different LLMs depending on what the situation is. So
now I know which LLM works best in which situation because I have an
intuition for it. So I generally switch between Sonnet GPT5 and Grok4,
frankly. So you know, check out Zoe. It\'s a little intense, but if you
take a liking to it, there\'s nothing like it in the world.

**\
27:05**\
Elaine P\
Its format is actually very slow. The layout looks like cursor, which is
also my favorite silk rockboard. That\'s very cool. I\'ll definitely
check it out.

**\
27:17**\
Vrijen Attawar\
If you use my promo code, you get 50% off. It\'s basically like having
half off on all of your LLM API price.

**\
27:26**\
Elaine P\
So this VAT 5 goes automatically to your promo code?

**\
27:30**\
Vrijen Attawar\
Yep. You get 25 bucks, I believe, and 50% off of any subscription.

**\
27:36**\
Elaine P\
Okay, I have to bookmark that. Okay, cool. My last question is, how do
you learn about the design patterns?

**\
27:44**\
Vrijen Attawar\
Just a lot of. Lot of trial and error. Lots of just, like, doing it.
Like. I have spent maybe easily a thousand hours of just, like, directly
and indirectly learning about how to work AI in the last year. It\'s a
lot of experimentation, I would.

**\
28:09**\
Elaine P\
Say, of the direct large language model. Experimentation.

**\
28:16**\
Vrijen Attawar\
Experimentation. Learning how large language models. It\'s like if
you\'re a race car driver, you have a different intuition for how the
car moves. Or if you play basketball, the way the basketball feels in
your hand and your body is different from how you and I would do.
Actually, I don\'t know if you have a background in basketball. I
don\'t, certainly, for me. But the interesting thing, or I think the
advantage, is that once you just shoot enough or play with AI enough,
you\'ll notice. Oh, it\'s going to be bad at answering this question.
Oh, I should change the phrasing. I\'ll actually. I\'m going to. Because
now I have such an easy pipeline. I\'ll be sure to send you a couple of,
like, YouTubers that I like. There\'s a guy called Nate B. Jones for the
more technical stuff.

**\
29:05**\
Vrijen Attawar\
There\'s Three blue, one brown, I think is what they\'re called.
There\'s. There\'s a couple of really great YouTubers that I can
recommend if you\'re interested in learning some more intermediate to
advanced level stuff.

**\
29:18**\
Elaine P\
Yeah, awesome. I think I recognize three blue, one brown. Maybe not. Is
that the one that kind of explains.

**\
29:24**\
Vrijen Attawar\
Yeah, yeah, that\'s exactly the one. That\'s exactly the one. Yeah. So
they\'re awesome. He\'s awesome. And then there\'s a couple of other
interesting ones I have to. I have to jump, unfortunately. But I hope
this was helpful. I hope this was sort of encouraging. And, you know,
it\'s just such a pleasure to be chatting with you.

**\
29:43**\
Elaine P\
Yeah, yeah, likewise.

**\
29:44**\
Vrijen Attawar\
Yeah, definitely add me on LinkedIn. And please let your friend know
that we spoke as well. They were definitely hoping to help you out, so
hopefully they felt they were able to do that.

**\
29:54**\
Elaine P\
Yeah, Defin, I\'ll let her know. Yeah, for sure.

**\
29:57**\
Vrijen Attawar\
Yeah. Let\'s stay connected. Yeah. Add me on LinkedIn. I\'ll catch you
soon.

**\
30:02**\
Elaine P\
Okay. Bye.

**\
30:03**\
Vrijen Attawar\
Bye. It.
