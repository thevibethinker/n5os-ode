**\
00:00**\
Ilse Funkhouser\
Hello. Hello.

**\
00:03**\
Vrijen Attawar\
Hello. Hello.

**\
00:05**\
Ilse Funkhouser\
Hello.

**\
00:08**\
Logan Currie\
Hello.

**\
00:09**\
Ilse Funkhouser\
Hey, Fireflies V. Did you disable my ability to talk to fireflies?

**\
00:17**\
Vrijen Attawar\
I did, yeah.

**\
00:18**\
Ilse Funkhouser\
It makes me so sick. Did you get any notes in Swahili one day?

**\
00:24**\
Vrijen Attawar\
No, I didn\'t get any notes in Swahili, but good attempt.

**\
00:31**\
Logan Currie\
Oh, that\'s funny.

**\
00:34**\
Vrijen Attawar\
I have. I have silenced. Silenced him.

**\
00:39**\
Ilse Funkhouser\
We were. We were enjoying it greatly.

**\
00:42**\
Logan Currie\
That\'s funny.

**\
00:44**\
Vrijen Attawar\
Yeah. I\'m glad I got to. I\'m glad I got to be there, though, for you
to realize that was my intent.

**\
00:53**\
Ilse Funkhouser\
No, I noticed it the other day, and it made me sad you weren\'t there. I
was trying to add. Yeah.

**\
01:02**\
Vrijen Attawar\
How\'s your day going?

**\
01:06**\
Ilse Funkhouser\
Good. I\'m getting a ton done because I keep working too long. So
that\'s.

**\
01:11**\
Logan Currie\
Did you. Ilsa was talking to me really late night. I was like, go to
bed.

**\
01:16**\
Ilse Funkhouser\
I\'m working like 13 hours and it\'s not healthy.

**\
01:19**\
Logan Currie\
That\'s not good. Take off early and go to a beach, please and thank
you. It\'s a. It\'s a holiday. It\'s a holiday weekend.

**\
01:29**\
Ilse Funkhouser\
It should be Monday.

**\
01:32**\
Logan Currie\
Monday. Just. It\'s Labor Day. I feel very strongly about Labor Day in
the sense that nobody should be doing.

**\
01:42**\
Ilse Funkhouser\
See that. But the NRLB is. Is going away because of the stacked court,
so good job maintaining labor rights or anything.

**\
01:55**\
Logan Currie\
I did not see that. Can you see?

**\
01:57**\
Ilse Funkhouser\
Federal 5th Circuit judge ruled that the National Labor Review Board.
Review board, it\'s called. Is unconstitutional after literally over a
hundred years of precedent of it being like, no, this is totally
constitutional and an important thing. Apparently now it\'s just. No
trump has the ability to destroy it. Cool. Yeah. I\'m not freaking out.

**\
02:22**\
Logan Currie\
I\'m freaking out. I\'m gonna see here. I was just reading. I don\'t
know where it went. I\'m making my way through this big tome called
Work. It\'s literally called Work. And it\'s very interesting. It\'s
based like a socio. Socio anthropological look at work throughout human
history. And it\'s like. Like what we spend energy on to get energy and
like it. The word work was invented in the 19th century to describe like
a phys. The physics of like, motion, essentially. Anyway, like, all this
stuff. And you\'re like, oh, just very interesting. And you\'re like,
this is. Yeah. Gets very philosophical.

**\
03:08**\
Ilse Funkhouser\
But that explains because erg, which is a unit of measurement of, like,
love literal work. That\'s ancient Greek for like, work or tasks. So
that makes a lot of sense.

**\
03:20**\
Logan Currie\
Yeah. Yeah.

**\
03:21**\
Ilse Funkhouser\
Well.

**\
03:25**\
Logan Currie\
It\'S very slow going. I read like two pages a day. Oh, v. That\'s good.
That\'s very funny.

**\
03:34**\
Vrijen Attawar\
Thank you.

**\
03:37**\
Logan Currie\
I appreciate any and all pop culture references. So that is a joke just
for me and I cherish it in my heart.

**\
03:46**\
Vrijen Attawar\
Absolutely. You gotta. You gotta contain comedic multitudes in a team
like this. Oh, man. How\'s. How\'s your morning? Besides being
overworked?

**\
04:02**\
Ilse Funkhouser\
I didn\'t say I was overworked. I said I was doing a lot of work.

**\
04:07**\
Logan Currie\
I said overwork.

**\
04:11**\
Ilse Funkhouser\
I finally moved us over to the new Responses API and it was a pain in
the ass. But the problem was using ChatGPT5 in addition to taking up so
many goddamn tokens. Even the new O3 models and stuff reasoning takes so
long that you run into issues with connectivity. And with just standard
timeouts, they have this thing called background mode where you just
pull and you\'re like, hey, are you done yet? Hey, are you done yet?
Hey, are you done yet? Until it\'s done, that way you don\'t run into
any connectivity issues. But, like, that was a whole, you know, whole
piece of. But at least now we\'re on newer tech. That\'ll be. It\'ll
make it easier for us to do newer and newer things in the future. So,
cool reminder. Danny\'s gonna be gone all next week. Well, pretty much
all week.

**\
05:13**\
Ilse Funkhouser\
So I\'m gonna be able to focus on a lot of the email stuff and if you.
It\'s going to be a very good week for you guys to use me to do any sort
of sales engineering stuff you need. So if you need data, real data, a
lot of one off things. But the big thing I\'m doing is Logan, you might
know this. What? Happily employed what\'s her face. Ainsley\'s request
was that, hey, my leads are viable for up to 10 days. And that poses a
problem for us because historically I\'ve treated it as. As soon as V
gives me a job, we treat it as like, valid for two days and then we just
ignore it again, right? So now the problem is she added like 50 jobs
originally. And I\'m like, okay, cool. I sent out 10 emails. Those are
gone forever.

**\
06:14**\
Ilse Funkhouser\
And she\'s like, wait, what if someone signs up today? They won\'t get
those 50 jobs sent to them. So what I\'m doing is I\'m building up the
system to keep track in Firestore, who have we checked the role against
and who have we sent it to so that for however long a job is alive?

**\
06:47**\
Vrijen Attawar\
Are you. Oh, no, it\'s me. You\'re both frozen.

**\
06:50**\
Ilse Funkhouser\
So it\'s cool. And at that point, it\'s still, I still have to deal with
some caching stuff. But in theory, the process won\'t be like whatever,
you get the idea. The other benefit is the new fill in the gap system.
If you\'re doing it from an application that you start in the system.
Like if you just create new application based in the job description,
unfortunately it takes like four minutes. Two and a half of those
minutes are spent doing that really deep analysis of the job, breaking
it up into responsibilities, attaching soft skills and hard skills to
those responsibilities, assessing importance, creating assessment
criteria, whatever.

**\
07:32**\
Ilse Funkhouser\
But I\'ve set it up and I have to finish setting it up where if an
application comes from a lead, something that I\'ll be sending out, I
attach that to the lead and so that it only takes, especially if you\'ve
only told like one story or zero stories, it only takes like you know,
this much time, you know, 30 seconds, whatever to generate all of that,
which saves us a lot of money. It\'ll save us like 30 cents per user as
well as probably maybe more. I don\'t know, I\'ll double check the
actual costs. But it saves everyone time and it saves us money. So it\'s
a good thing all around. It does however mean that the more we can get
people to use jobs that we distribute, the better, more or less.

**\
08:26**\
Ilse Funkhouser\
So that\'s another reason why having that magic link system of like,
hey, is there someone that you know who would be interested in this
role? Send it here. That saves us money and it, you know, Danny, I
thought that you were. Why aren\'t you relaxing and preparing for your.
For your everything Go away. You\'re muted as well.

**\
08:48**\
Danny Williams\
Oh, is it working?

**\
08:50**\
Vrijen Attawar\
Yeah, it\'s working. Cool.

**\
08:54**\
Danny Williams\
No, I mean I\'m still working today. I. I\'ll be preparing on the
weekend. No worries.

**\
09:02**\
Vrijen Attawar\
What are you most excited about?

**\
09:08**\
Danny Williams\
I don\'t know. I mean I kind of just going for the networking I guess to
like meet a bunch of people and it will be. The whole like panel thing
is like a last minute thing. I made some friends at Amazon and they
basically dragged me into it. And then now nice. I\'m doing that and
that\'s. I\'m more nervous about that than anything. I don\'t really
know how that\'s gonna go, but apparently I\'m gonna know what they\'re
gonna ask. So it\'s like nice. It\'s going to be a bit easier, but it\'s
like a pretty big crowd, so I\'d be kind of scary.

**\
09:48**\
Logan Currie\
Can I put my career coach and career brand strategist hat on? For a
minute and please, please ask somebody to take a lot of pictures for
you. Yeah. And to take.

**\
10:00**\
Danny Williams\
Because it\'s going to be recorded.

**\
10:02**\
Ilse Funkhouser\
So yeah, phenomenal.

**\
10:04**\
Logan Currie\
But also get some, like get somebody with a decent camera or just a
decent on camera and just take some snaps. You\'re gonna want those like
later. So.

**\
10:12**\
Danny Williams\
Yeah, okay. Yeah, I have a friend who\'s gonna be there from Porto maybe
I have a few. Actually a couple people I know are going to be there, so
maybe I like at least one of them has got to have a camera.

**\
10:27**\
Logan Currie\
Yeah, yeah, just like a few snaps or whatever and then like it doesn\'t
need to be obnoxious. But yeah, I, the branding side of me comes out
there, but also I look forward to. I mean, I assume all these people are
like total badasses when we need to go like tap into top talent.
Danny\'s gonna be our.

**\
10:48**\
Vrijen Attawar\
Danny\'s gonna be our like 11th.

**\
10:52**\
Logan Currie\
I like us. Yeah, yeah. I like this.

**\
10:56**\
Danny Williams\
Yeah. I think there\'s gonna be someone from Microsoft in the panel as
well from the Office because they build like Office with react native
stuff. So that should be interesting. Yeah, I mean I do, yeah, I do know
quite a few people, I think like at least vaguely, you know, so for
sure. But I mean these people, a lot of these people are already working
at like Amazon or Microsoft. So.

**\
11:25**\
Vrijen Attawar\
Yeah, they already peaked out.

**\
11:29**\
Logan Currie\
I mean you were just the on the incoming like talent wars though that
like it\'s now like there but it\'s like it\'s gonna. A lot of the top
performers. So it\'s like I think there\'s space for career span to kind
of like signal like fantasy football style. Like who\'s.

**\
11:46**\
Danny Williams\
So when Charisman, you know, kicks off and like, you know, becomes a
unicorn and then all the hits the fan with the whatever is going to
happen in the next few years, then, you know, I\'ll bring them in.
Don\'t worry.

**\
12:02**\
Vrijen Attawar\
During the, during the same talent wars.

**\
12:04**\
Logan Currie\
Of 2030, we can signal to other people and say like, okay, this is your
crazy ass Kobe Bryant style signing bonus. Like, we\'ll take a.

**\
12:17**\
Vrijen Attawar\
I really hope for the employee\'s sake that is the kind of future that
we live in where you get a signing bonus instead of bleeding money to a
recruiter. There something Logan and I, or I think maybe Ilsa and I
talked about.

**\
12:32**\
Ilse Funkhouser\
At some point of like we\'ve all pitched.

**\
12:35**\
Vrijen Attawar\
Yeah, yeah. It\'s. I think it makes a lot of sense to like Split the
take with the candidate one day.

**\
12:44**\
Ilse Funkhouser\
Yeah.

**\
12:44**\
Vrijen Attawar\
But.

**\
12:45**\
Logan Currie\
Yeah, well, it\'s because we\'re the agent, we\'re not the recruiter.
Like, we are representing the talent. So, like, we are, like, we can.
It\'s a, It\'s a flip. It\'s for Uno Reverse card. Yeah.

**\
13:00**\
Vrijen Attawar\
Which it\'s like giving. It\'s like giving every single. Yeah, it\'s
like giving every single member of your community a career agent. Right,
Jerry.

**\
13:11**\
Logan Currie\
We\'re Jerry Maguire. We are Jerry Maguire.

**\
13:14**\
Vrijen Attawar\
Yeah, I. I do think that\'s. That\'s potentially a pretty sort of
compelling, like, line of messaging as well.

**\
13:24**\
Ilse Funkhouser\
Yeah.

**\
13:27**\
Logan Currie\
I mean, I, I don\'t think. Yeah, I\'m. I look. I look forward to in
person beer chats about the future of all of this.

**\
13:40**\
Danny Williams\
There\'s more. The more wine or beer that goes in, the more, like,
existential grad comes out.

**\
13:46**\
Logan Currie\
Going to start off. We\'re going to start off like a little bit tactical
and then by the end of the night we\'re going to be like. And then
humanity.

**\
13:54**\
Ilse Funkhouser\
I will make sure that I bring copious amounts of Madeira. So I will
bring bottles of Madeira for us to drink. Yes.

**\
14:02**\
Vrijen Attawar\
Love it, love it.

**\
14:03**\
Ilse Funkhouser\
Which will give us hangovers because it\'s a fortified wine, but still.

**\
14:07**\
Vrijen Attawar\
Oh, God.

**\
14:09**\
Ilse Funkhouser\
Oh, God.

**\
14:09**\
Logan Currie\
Yeah, I\'ll prepare. I\'ll bring, I\'ll bring the ad though. But. All
right. What is this link that you are sending me?

**\
14:19**\
Vrijen Attawar\
Oh, it\'s. It\'s. As always, there\'s a relevant XKCD for every
occasion.

**\
14:28**\
Logan Currie\
Even know what this is?

**\
14:31**\
Vrijen Attawar\
Bomber was this, like, tech executive from the 2000s. He was like,
employee number three or four at Microsoft and eventually made enough
money to buy the Clippers. He\'s like, but. But Microsoft sucked ass
during his, like, reign. They were just the worst and very like, yeah,
very like NBA running the show kind of situation.

**\
15:01**\
Logan Currie\
You see what\'s happening out my window, there\'s just like a guy on a
crane going. Going past. There was like a man at my window on the second
floor and I was like, astounding. Any long weekend plans, Ilsa? I guess.
Or. Or virgin. What are you doing with your parents this weekend, V?

**\
15:30**\
Vrijen Attawar\
We are going to get a Airbnb with Amanda\'s mom somewhere. Somewhere
around where we got married, actually. Right around.

**\
15:40**\
Logan Currie\
Oh, cool.

**\
15:41**\
Vrijen Attawar\
Yeah, just sort of hang out, have a. Have a chill weekend in. Go. Go do
some shopping or the outlets.

**\
15:49**\
Ilse Funkhouser\
It\'s a little tardy. Do your parents drink?

**\
15:55**\
Vrijen Attawar\
No, no. I actually know my dad drinks, but very recreationally. It\'s
not. It\'s not. It\'s not.

**\
16:04**\
Ilse Funkhouser\
It\'s so funny. But, like, if it\'s, like, if you say that. Oh, yeah,
someone in their 20s drinks recreationally, that means something totally
different than, like, you know, my dad. Yeah. I love it. Well, that\'s
fun.

**\
16:20**\
Vrijen Attawar\
Yeah. Yeah. Just time away from the cats, that\'s all.

**\
16:24**\
Ilse Funkhouser\
That is sad. It was sad to hear that you weren\'t stealing Amanda to
come with. Well, these. Amanda wasn\'t coming to Porto.

**\
16:33**\
Vrijen Attawar\
I. I tried. I put up a good fight, but it\'s right around Climate Week,
so she\'s. She\'s pretty.

**\
16:41**\
Ilse Funkhouser\
When the climate change happens.

**\
16:46**\
Vrijen Attawar\
Man, ain\'t that the truth. In this household. Every week is fucking
Climate Week. Every goddamn week is Climate Week.

**\
17:01**\
Logan Currie\
We\'re going camping, which I always have to, like, psych myself up for,
because I enjoy it when I\'m there. But, like, then I wake up and I\'m,
like, on a. In a tent and my phone is dead and I\'m cold and there\'s no
shower. So, like, it\'s. It\'s. It\'s good and it\'s good and bad at the
same time.

**\
17:21**\
Danny Williams\
Camping is only good in the parts where you\'re not in the tent.

**\
17:24**\
Logan Currie\
Yeah, exactly.

**\
17:26**\
Danny Williams\
Outside of that, it\'s horrible. And then you\'re just like, why didn\'t
I get a hotel?

**\
17:30**\
Ilse Funkhouser\
Like, what am I doing?

**\
17:31**\
Logan Currie\
Yeah, yeah, agreed. Agreed on all counts. Agreed on all counts. But were
supposed to be driving, like, five hours, and then we changed plans
because my cousin\'s sick, so we are now only driving two hours, which
is much more reasonable. Yeah, yeah. Especially with children who do not
like being in the car for that long.

**\
17:59**\
Vrijen Attawar\
I have to jump. I have to prepare for this next call, but I\'ll catch
you.

**\
18:05**\
Logan Currie\
Bye.
