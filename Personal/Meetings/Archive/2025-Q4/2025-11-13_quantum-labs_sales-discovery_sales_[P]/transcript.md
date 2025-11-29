# **Transcript 2: External Sales Meeting**

**Participants:** Vrijen Attawar (CareerSpan CEO), Sarah Chen (VP of
Engineering, Quantum Labs - Series B SaaS startup), Marcus Williams
(Recruiting Lead, Quantum Labs)

**Duration:** \~15 minutes

**Vrijen:** Sarah, Marcus---thanks so much for making time today. I know
you\'re both slammed with the Series B growth push.

**Sarah:** Of course. And yeah, slammed is an understatement. We\'re
trying to go from 35 to 85 engineers in the next nine months and
it\'s\... honestly terrifying.

**Vrijen:** I can imagine. That\'s a 2.4x headcount increase. Before we
dive into CareerSpan specifically, I\'m curious---what\'s your biggest
pain point right now with hiring? Is it pipeline, is it quality, is it
speed?

**Marcus:** Can I say all three? *laughs* But if I had to pick one,
it\'s quality. We\'re getting decent volume from our ATS. We\'re posting
on all the boards, working with three agencies. But the signal-to-noise
ratio is brutal. I\'m spending 60% of my time screening candidates who
look good on paper but just don\'t have the depth we need.

**Sarah:** And here\'s the thing---we can\'t afford to compromise.
We\'re building real-time data infrastructure. If I hire someone who\'s
only done batch processing or doesn\'t understand distributed systems at
a fundamental level, it creates tech debt that costs us six months down
the line. I\'ve made that mistake before. Not doing it again.

**Vrijen:** That resonates. So the agencies you\'re working with---are
they surfacing candidates with the right depth? Or are they just keyword
matching?

**Sarah:** Honestly? Keyword matching. They send us people who have
\"Kafka\" and \"Kubernetes\" on their resume, but when we get them in a
technical interview, it\'s clear they\'ve only used these tools in
narrow contexts. They can\'t design systems. They can\'t reason about
trade-offs.

**Vrijen:** Got it. And Marcus, you mentioned you\'re spending 60% of
your time on screening. What does that process look like right now?

**Marcus:** So we have an initial phone screen---30 minutes where I\'m
basically trying to figure out if they understand what we\'re building
and if they can have a technical conversation. If they pass that, they
go to Sarah\'s team for a technical deep-dive. But here\'s the problem:
about 40% of people who pass my screen still fail Sarah\'s technical
round. Which means I\'m not screening effectively, and we\'re wasting
Sarah\'s engineers\' time on interviews that aren\'t going anywhere.

**Sarah:** And every hour my senior engineers spend interviewing is an
hour they\'re not shipping. We just pushed our Q4 infrastructure
milestone by three weeks because half my staff engineering team was
doing interview loops.

**Vrijen:** That\'s a really expensive problem. Okay, so let me tell you
how CareerSpan works differently, and you tell me if this maps to what
you need. We don\'t start with resumes. We start with what we call
\"story packs\"---these are structured narratives where candidates walk
through their craft at a deep level.

**Sarah:** What do you mean by \"craft at a deep level\"?

**Vrijen:** So instead of a bullet point that says \"Built microservices
architecture using Kafka,\" the candidate walks us through a specific
project: Why did they choose Kafka over other messaging systems? What
trade-offs did they consider? What broke when they hit scale, and how
did they debug it? We\'re capturing their decision-making process, their
depth of understanding, and their ability to communicate technical
nuance.

**Marcus:** Okay, I like that in theory. But who\'s doing this curation?
Are you just relying on candidates to self-report?

**Vrijen:** Great question. This is where our Community Quality Score
comes in. Every story pack is validated by our community of senior
practitioners---CTOs, Staff+ engineers, people who have been in the
trenches. They\'re essentially peer-reviewing the depth and authenticity
of what candidates are claiming. We\'re not just taking their word for
it.

**Sarah:** Wait, so you have\... like a panel of senior engineers
reviewing candidates before they even get to us?

**Vrijen:** Exactly. And here\'s the key---we\'re not trying to replace
your technical interview. We\'re trying to make sure that by the time
someone gets to your technical interview, there\'s a 90%+ chance
they\'re actually the right caliber. We\'re doing the expensive
filtering work upstream.

**Marcus:** What kind of time are we talking about? Because one of the
agencies we work with promises \"48-hour shortlists\" but they\'re
basically just scraping LinkedIn and sending us whoever responds.

**Vrijen:** We deliver curated shortlists within 24 hours. But the
difference is, we\'re not scraping. We have a vetted community of
candidates who have already gone through our story pack process and
community validation. When you submit a search, we\'re matching against
that pre-validated pool.

**Sarah:** 24 hours seems fast. How many candidates are we talking about
in a shortlist?

**Vrijen:** Three to five. We\'re not flooding you with 50 resumes.
We\'re giving you a tight shortlist of people who match your technical
depth requirements and cultural context. Quality over volume.

**Marcus:** Okay, I\'m interested, but I need to understand the catch.
What\'s your success rate? Like, if you send us five candidates, how
many typically make it through a full interview loop?

**Vrijen:** So we track this pretty closely. Across our customer
base---mostly Series A to C startups like yourselves---we\'re seeing
about 60% of candidates we send make it through full interview loops to
offer stage. Compare that to your current 40% phone screen to technical
round pass rate, and you\'re looking at significant time savings.

**Sarah:** 60% is compelling. But what if we\'re more specialized than
your typical customer? We\'re not just looking for \"senior backend
engineers.\" We need people who specifically understand distributed
consensus algorithms, have dealt with data replication at scale, and can
reason about consistency models. Does your community have that depth?

**Vrijen:** It\'s a fair question. Let me ask you this---what would a
story pack need to demonstrate for you to feel confident that someone
has that depth? Because we can literally add those dimensions to the
search brief.

**Sarah:** I\'d want to see them walk through a time they had to choose
between strong consistency and eventual consistency. I\'d want to
understand their mental model for thinking about partition tolerance.
And ideally, I\'d want to see that they\'ve actually dealt with
production incidents related to distributed systems, not just academic
knowledge.

**Vrijen:** Perfect. So when we build your search brief, we\'d include
those exact dimensions in the story pack prompts. Candidates wouldn\'t
just say \"I know distributed systems\"---they\'d walk through specific
scenarios where they made those trade-offs. And then our community
validators, who include people from companies like Datadog, Stripe, and
Confluent, would assess the depth of those responses.

**Marcus:** What\'s the pricing structure? Are we talking retained
search fees, or\...?

**Vrijen:** We\'re not a traditional agency. We charge per search, not
per hire. \$4,500 per search, and you get up to five validated
candidates. If you want to hire three of them, great---no additional
fees. We\'re aligned on quality, not on stringing out placements.

**Sarah:** \$4,500 per search\... how does that compare to your
agencies, Marcus?

**Marcus:** Our agencies are 20-25% of first-year salary. For a senior
engineer at \$180K, that\'s \$36K to \$45K per hire. So if CareerSpan
can deliver quality, this is dramatically cheaper. But what if the
search doesn\'t yield anyone we want to hire? Are we out \$4,500?

**Vrijen:** Good question. We have a quality guarantee. If none of the
candidates in your shortlist make it past your technical interview
stage, we\'ll run a second search at no additional cost. We\'re betting
on our curation quality.

**Sarah:** Okay, I like the risk profile. But here\'s my
concern---speed. You said 24 hours for a shortlist. But then there\'s
interview scheduling, which realistically takes another week. Then
interview loops, which are another two weeks. Then offer negotiation.
We\'re still looking at 4-6 weeks time-to-hire even if your candidates
are great.

**Vrijen:** Totally valid. The 24-hour shortlist is just the first step.
But here\'s where I think we can help you move faster: because our
candidates have already done the deep story pack work, your initial
screening call with Marcus can be way shorter. Instead of 30 minutes of
\"tell me about your background,\" he can jump straight to cultural fit
and logistics. Does that save you a week? Maybe. But compounded over 50
hires, that\'s meaningful time savings.

**Marcus:** True. And if the technical pass-through rate is actually
60%, that means Sarah\'s team does way fewer interviews overall. That\'s
huge.

**Sarah:** I\'m intrigued. What would a pilot look like? I don\'t want
to commit to 50 searches upfront. Can we start with two or three
critical roles and see how it goes?

**Vrijen:** Absolutely. We typically start with a pilot of 2-3 searches.
You\'d pay per search as you go, no long-term contract. I\'d recommend
we start with your highest-pain role---probably Senior Distributed
Systems Engineer, based on what you\'ve told me---and see if the quality
matches expectations. If it does, we scale from there.

**Sarah:** What\'s the onboarding process? How much time do we need to
spend with you to build the search brief?

**Vrijen:** Usually one hour. We\'d do a deep-dive on the role---not
just the skills, but the context. What are they walking into? What\'s
the team dynamic? What kind of problems will they be solving in their
first 90 days? The richer the context, the better we can match. Marcus,
I\'d probably want you and Sarah on that call, plus maybe one of your
senior engineers who can speak to the technical nuance.

**Marcus:** I can do that. Sarah, what do you think?

**Sarah:** I think it\'s worth a shot. Honestly, if you can deliver even
two solid hires out of the next five roles we need to fill, this pays
for itself in time savings alone. Let\'s do a pilot.

**Vrijen:** Awesome. I\'ll send over a pilot agreement today---just
covers the first three searches, \$4,500 each, quality guarantee
included. And we\'ll schedule that kickoff call for next week. I\'ll
send a calendar invite. Sound good?

**Sarah:** Sounds good. Thanks, Vrijen.

**Vrijen:** Thank you both. Excited to help you scale the team. Let\'s
go build something great.

**Snap Summary:**

✅ **Internal Meeting:** Product discussion on adding async \"Ask a
Question\" feature to reduce friction between story pack views and
interview requests. Decision to A/B test with 20% traffic, plus mobile
performance fixes.

✅ **External Meeting:** Sales call with Quantum Labs (Series B). Pain
points: quality screening, engineer time drain. Pitched CareerSpan\'s
story packs + community validation. Closed pilot: 3 searches at \$4,500
each with quality guarantee.
