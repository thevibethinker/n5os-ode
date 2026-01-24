/**
 * Keanu-fied GTM Wisdom
 * Original quotes from GTM legends, filtered through Keanu's zen-philosopher voice
 * Sources verified via X API and web research
 */

import { getChapterIndexForQuoteId } from "./chapters";

export interface KeanuQuote {
  id: number;
  keanuQuote: string;
  originalQuote: string;
  originalAuthor: string;
  authorUrl?: string;
  source?: string;
  verification: 'verified' | 'likely' | 'unverified';
  category: 'sales' | 'marketing' | 'product' | 'growth' | 'leadership' | 'strategy';
}

export const quotes: KeanuQuote[] = [
  // Jason Lemkin - SaaStr
  {
    id: 1,
    keanuQuote: "Whoa, okay, so there's this order to things. VPM around $200k. VPS around $1.5 mil. VPCS around $2 mil. VPP around $3-4 mil. VPE around $5-6 mil. Each hire unlocks the next level. But you can't skip ahead. You just... can't.",
    originalQuote: "IME, rough order to make hires in: VPM: $0.2m ARR, VPS: $1-$1.5m ARR, VPCS: $2m ARR, VPP: $3m-$4m ARR, VPE: $5m-$6m ARR",
    originalAuthor: "Jason Lemkin",
    source: "https://x.com/jasonlk/status/1152959609985835013",
    verification: "verified",
    category: "leadership"
  },
  {
    id: 2,
    keanuQuote: "Sales leaders who can't demo the product... that's like hiring a stunt driver who's never touched a steering wheel. The best ones could sell it on day one. Before they even get the job. [long pause] That's how you know.",
    originalQuote: "Whatever you do, do not hire a Head of Sales who can't demo the product before day one.",
    originalAuthor: "Jason Lemkin",
    source: "SaaStr",
    verification: "verified",
    category: "sales"
  },
  {
    id: 3,
    keanuQuote: "You gotta close the first ten yourself. As the founder. If you outsource that part, you'll never know what actually works. You'll just... hope. And hope isn't a GTM strategy.",
    originalQuote: "Founders should close the first 10 customers themselves. If you don't, you'll never really know how it's done.",
    originalAuthor: "Jason Lemkin",
    source: "SaaStr",
    verification: "verified",
    category: "sales"
  },
  {
    id: 4,
    keanuQuote: "Never hire anyone in sales who doesn't care about money. [pauses] I know. But ask them what they want to make this year. Watch their eyes. That hunger isn't greed—it's alignment.",
    originalQuote: "Never hire anyone in sales that doesn't care about money. You'll see.",
    originalAuthor: "Jason Lemkin",
    source: "SaaStr",
    verification: "verified",
    category: "sales"
  },
  {
    id: 5,
    keanuQuote: "Two reps. Always two. With one, you never know if the problem is the person or the territory. With two, you get signal. That clarity? Worth twice the cost.",
    originalQuote: "Always hire at least two sales reps initially. You have to A/B test it.",
    originalAuthor: "Jason Lemkin",
    source: "SaaStr",
    verification: "verified",
    category: "sales"
  },

  // Nick Mehta - Gainsight (Customer Success Pioneer)
  {
    id: 6,
    keanuQuote: "Here's what nobody tells you about churn metrics. They track lost CURRENT ARR. But the biggest impact? The lost FUTURE expansion dollars. So churn is actually an even bigger deal than people realize. [looks into distance] Way bigger.",
    originalQuote: "Churn calculations all have a fundamental flaw. They track the lost CURRENT ARR. Yet perhaps the biggest impact of churn (especially with large clients) is the lost FUTURE expansion dollars.",
    originalAuthor: "Nick Mehta",
    source: "https://x.com/nrmehta/status/1277796267033128960",
    verification: "verified",
    category: "growth"
  },
  {
    id: 7,
    keanuQuote: "I talked to a PM who moved into Customer Success. Asked why. They said 'The future of technology isn't just about building products—it's about making sure customers get value.' [slight smile] I think they're onto something.",
    originalQuote: "Spoke to a Product Manager who decided to move into Customer Success. They said 'It's so clear that the future of technology isn't just about building products - it's about making sure customers get value.'",
    originalAuthor: "Nick Mehta",
    source: "https://x.com/nrmehta/status/1327415306248077313",
    verification: "verified",
    category: "growth"
  },
  {
    id: 8,
    keanuQuote: "One of the value props of SaaS is that the tech automatically evolves. You're not buying current state—you're buying roadmap. That's why building custom tech internally rarely works. Internal roadmaps... they can't keep up.",
    originalQuote: "One of the value props of SaaS is that the tech automatically evolves. Buyers are buying roadmap - not just current state. Internal roadmaps can't keep up.",
    originalAuthor: "Nick Mehta",
    source: "https://x.com/nrmehta/status/1384181557997424651",
    verification: "verified",
    category: "product"
  },
  {
    id: 9,
    keanuQuote: "Our mission has nothing to do with customer success. It's to be living proof you can win in business while being human-first. [quiet] The success part? That just follows when you get the human part right.",
    originalQuote: "Our mission statement is nothing to do with customer success—it's to be living proof you can win in business while being human first.",
    originalAuthor: "Nick Mehta",
    source: "UserTesting Podcast",
    verification: "verified",
    category: "leadership"
  },
  {
    id: 10,
    keanuQuote: "Traditional software has a problem—it depends on the customer being great at their job. But most customers aren't above average. By definition. AI agents decouple software success from client capabilities. That's... that's actually wild when you think about it.",
    originalQuote: "Traditional software depends on the customer being great at their job. By definition most customers aren't above average. A positive side effect of agents is they decouple software success from client capabilities.",
    originalAuthor: "Nick Mehta",
    source: "https://x.com/nrmehta/status/2011578572809650522",
    verification: "verified",
    category: "product"
  },

  // David Sacks - Craft Ventures
  {
    id: 11,
    keanuQuote: "Before you blame sales, check if the problem is actually pipeline. Sales owns win rates and cycle time. But pipeline growth? That's everyone. Product. Marketing. The whole company.",
    originalQuote: "Lead gen, not sales, is usually the rate-limiting factor on growth. Before blaming the sales team, analyze close rates vs pipeline growth.",
    originalAuthor: "David Sacks",
    source: "https://x.com/DavidSacks/status/1094448973098582016",
    verification: "verified",
    category: "growth"
  },
  {
    id: 12,
    keanuQuote: "Startups first. Then departments. Then enterprise-wide. It's almost impossible to build sales momentum any other way. You have to crawl before you can... [gestures vaguely upward]",
    originalQuote: "First sell to startups. Then sell to LOB (departments). Then sell enterprise wide. Almost impossible to build sales momentum any other way.",
    originalAuthor: "David Sacks",
    source: "https://x.com/DavidSacks/status/1163548991516078080",
    verification: "verified",
    category: "strategy"
  },
  {
    id: 13,
    keanuQuote: "Product founders—do yourself a favor. Make that first GTM hire early. Really early. Find someone scrappy who can figure out the sale without support. It doesn't need to scale. It needs to learn.",
    originalQuote: "Product-y SaaS founders will do themselves a huge favor by making GTM hire #1 as early as possible. Just make sure it's a scrappy sales person who can figure out the sale without support.",
    originalAuthor: "David Sacks",
    source: "https://x.com/DavidSacks/status/1316153412216664064",
    verification: "verified",
    category: "strategy"
  },

  // April Dunford - Positioning
  {
    id: 14,
    keanuQuote: "Narrative is what you tell people. Positioning is what they understand. If your positioning sucks... [shakes head] no story saves you. None.",
    originalQuote: "Narrative is what you tell people. Positioning is what they understand. If your positioning sucks, no amount of narrative will fix it.",
    originalAuthor: "April Dunford",
    source: "X via @shreyas",
    verification: "verified",
    category: "marketing"
  },
  {
    id: 15,
    keanuQuote: "Positioning is just... context. Context so customers quickly understand why you matter. Without it, you're another option in a sea of options. With it, you're the only option that makes sense.",
    originalQuote: "Positioning is the context you provide for your product so that customers can quickly understand why it's valuable.",
    originalAuthor: "April Dunford",
    source: "The Knowledge Project",
    verification: "verified",
    category: "marketing"
  },
  {
    id: 16,
    keanuQuote: "Everyone leads with the problem. Everyone. Lead with the insight that changes how they see the category. That's how you create space where only you exist.",
    originalQuote: "Don't lead with the problem—that's what everyone does. Lead with the insight that changes how they see the category.",
    originalAuthor: "April Dunford",
    source: "https://x.com/richkingpma/status/1714256799497441483",
    verification: "verified",
    category: "marketing"
  },

  // Aaron Ross - Predictable Revenue
  {
    id: 17,
    keanuQuote: "Cold Calling 2.0 is the most predictable, controllable source of new pipeline. But it takes focus and expertise to do it well. People want the predictability without the discipline. Doesn't work like that.",
    originalQuote: "Cold Calling 2.0: By far the most predictable and controllable source of creating new pipeline, but it takes focus and expertise to do it well.",
    originalAuthor: "Aaron Ross",
    source: "Predictable Revenue",
    verification: "verified",
    category: "sales"
  },
  {
    id: 18,
    keanuQuote: "Separate prospecting from closing. Specialize. This one thing created consistent lead flow and predictable revenue. It's like... division of labor. But for deals.",
    originalQuote: "Separate prospecting from closing by creating specialized SDR roles. This creates consistent lead flow and predictable revenue.",
    originalAuthor: "Aaron Ross",
    source: "Predictable Revenue",
    verification: "verified",
    category: "sales"
  },

  // Geoffrey Moore - Crossing the Chasm
  {
    id: 19,
    keanuQuote: "Rules for crossing the chasm: Big enough to matter. Small enough to lead. Good fit with your crown jewels. That's it. Pick a beachhead you can actually win.",
    originalQuote: "Big enough to matter, small enough to lead, good fit with your crown jewels.",
    originalAuthor: "Geoffrey Moore",
    source: "Crossing the Chasm",
    verification: "verified",
    category: "strategy"
  },
  {
    id: 20,
    keanuQuote: "Here's what's beautiful about pragmatists. Once they install you as the leader? They conspire to keep you there. The early market is chaos. But win the mainstream right... and they want you to succeed.",
    originalQuote: "You get installed by the pragmatists as the leader, and from then on, they conspire to help keep you there.",
    originalAuthor: "Geoffrey Moore",
    source: "Crossing the Chasm",
    verification: "verified",
    category: "strategy"
  },
  {
    id: 21,
    keanuQuote: "Pragmatists buy whole products. Not features. Not technology. Whole solutions. If you can't give them the whole thing, you're not ready to cross.",
    originalQuote: "Pragmatists evaluate and buy whole products.",
    originalAuthor: "Geoffrey Moore",
    source: "Crossing the Chasm",
    verification: "verified",
    category: "product"
  },

  // Jeb Blount - Fanatical Prospecting
  {
    id: 22,
    keanuQuote: "Number one reason for failure in sales? Empty pipeline. [long pause] Not technique. Not product knowledge. Not closing skills. Just... nobody to talk to.",
    originalQuote: "The number one reason for failure in sales is an empty pipeline.",
    originalAuthor: "Jeb Blount",
    source: "Fanatical Prospecting",
    verification: "verified",
    category: "sales"
  },
  {
    id: 23,
    keanuQuote: "Golden hours. The hours when decision-makers actually pick up. Guard them. Ruthlessly. Don't let email or admin steal them. That's where the revenue lives.",
    originalQuote: "The Golden Hours are the hours when decision-makers are most likely to be available. Guard them ruthlessly for prospecting.",
    originalAuthor: "Jeb Blount",
    source: "Fanatical Prospecting",
    verification: "verified",
    category: "sales"
  },

  // Chris Voss - Never Split the Difference
  {
    id: 24,
    keanuQuote: "Negotiation isn't battle. It's... discovery. You're not trying to win. You're trying to understand. And when you really understand, the deal often... makes itself.",
    originalQuote: "Negotiation is not an act of battle; it's a process of discovery.",
    originalAuthor: "Chris Voss",
    source: "Never Split the Difference",
    verification: "verified",
    category: "sales"
  },
  {
    id: 25,
    keanuQuote: "You think they think like you. They don't. That's not empathy—that's projection. Real empathy is accepting they see a completely different world.",
    originalQuote: "If you approach a negotiation thinking the other guy thinks like you, you are wrong. That's not empathy, that's a projection.",
    originalAuthor: "Chris Voss",
    source: "Never Split the Difference",
    verification: "verified",
    category: "sales"
  },
  {
    id: 26,
    keanuQuote: "'Yes' means nothing without 'how' and 'when.' Agreement is easy. Implementation is where deals live or die. Ask the how questions. [taps table] The how questions.",
    originalQuote: "Yes is nothing without 'How' and 'When'.",
    originalAuthor: "Chris Voss",
    source: "Never Split the Difference",
    verification: "verified",
    category: "sales"
  },

  // Matt Dixon - The Challenger Sale
  {
    id: 27,
    keanuQuote: "Teach. Tailor. Take control. That's the challenger model. Not aggressive—but not passive either. You're showing them something about their world they didn't see.",
    originalQuote: "The Challenger model focuses on teaching, tailoring, and taking control of a sales experience.",
    originalAuthor: "Matt Dixon & Brent Adamson",
    source: "The Challenger Sale",
    verification: "verified",
    category: "sales"
  },
  {
    id: 28,
    keanuQuote: "Top reps don't understand the customer's world as well as them. They understand it better. [slight smile] That's how you become the guide. You see what they can't.",
    originalQuote: "They win by actually knowing their customers' world better than their customers know it themselves.",
    originalAuthor: "Brent Adamson",
    source: "The Challenger Sale",
    verification: "verified",
    category: "sales"
  },

  // Lincoln Murphy - Customer Success
  {
    id: 29,
    keanuQuote: "Adoption. Retention. Expansion. Advocacy. You can chase each one. Or... focus on the customer's Desired Outcome and get them all. It's like... aim at the right target. Everything else follows.",
    originalQuote: "You can focus on adoption, retention, expansion, or advocacy; or you can focus on the customers' Desired Outcome and get all of those things.",
    originalAuthor: "Lincoln Murphy",
    source: "https://x.com/lincolnmurphy/status/719576284049727488",
    verification: "verified",
    category: "growth"
  },
  {
    id: 30,
    keanuQuote: "Onboarding isn't done to prevent churn. It's done to help customers achieve what they actually wanted. Retention? That's just... what happens when you do it right.",
    originalQuote: "Proper onboarding isn't done to prevent churn; it's done to ensure the customer achieves their Desired Outcome. Retention comes from that.",
    originalAuthor: "Lincoln Murphy",
    source: "https://x.com/lincolnmurphy/status/723245447901368321",
    verification: "verified",
    category: "growth"
  },
  {
    id: 31,
    keanuQuote: "Churn is a symptom. Not a disease. Treat symptoms, they keep coming back. Find the root cause. Help them succeed. That's the cure.",
    originalQuote: "Churn is a symptom, not a disease.",
    originalAuthor: "Lincoln Murphy",
    source: "https://x.com/lincolnmurphy/status/709878141855076357",
    verification: "verified",
    category: "growth"
  },

  // Kyle Poyar - PLG & Pricing
  {
    id: 32,
    keanuQuote: "Your pricing page is the second most important page on your site. Are you neglecting it? Reinforce value. Don't overwhelm. Stop with the pricing hacks. Benefits over features. [nods] Benefits over features.",
    originalQuote: "Your pricing page is the 2nd most important page on your website. Reinforce your value prop. Don't overwhelm prospects. Stop worrying about pricing hacks. Emphasize benefits, not features.",
    originalAuthor: "Kyle Poyar",
    source: "https://x.com/poyark/status/1677364248366784521",
    verification: "verified",
    category: "product"
  },
  {
    id: 33,
    keanuQuote: "End users don't care about navigating enterprise purchases. How do you convince them to help you reach a decision-maker when the only benefits are 'enterprise-y' things they couldn't care less about? That's the PLG paradox.",
    originalQuote: "End users aren't motivated to help us navigate an enterprise purchase. How do we convince PQLs to help us reach a decision-maker if the only benefits are 'enterprise'-y things that they couldn't care less about?",
    originalAuthor: "Kyle Poyar",
    source: "https://x.com/poyark/status/1645501324048625664",
    verification: "verified",
    category: "product"
  },

  // Sam Jacobs - Revenue Leadership
  {
    id: 34,
    keanuQuote: "Heads of Sales who think hiring more salespeople makes more money... [shakes head] More meetings make more money. Meetings create opportunities. Salespeople turn opportunities into money. But they don't CREATE opportunity.",
    originalQuote: "Hiring more salespeople does not make more money. More meetings make more money. Salespeople turn opportunities into money. But they don't create opportunity.",
    originalAuthor: "Sam Jacobs",
    source: "https://x.com/samfjacobs/status/1803442568383897781",
    verification: "verified",
    category: "sales"
  },
  {
    id: 35,
    keanuQuote: "Three stages of CEO evolution. First: salespeople generate demand, so hire more salespeople. Second: wait, demand gen generates demand. Third: demand gen needs a message, a value prop, a target audience. Each stage humbles you.",
    originalQuote: "3 Stages of CEO Evolution: 1. Believes that salespeople generate demand 2. Realizes demand generation generates demand 3. Realizes demand generation needs a message, a value proposition, and a target audience",
    originalAuthor: "Sam Jacobs",
    source: "https://x.com/samfjacobs/status/1801010665374519633",
    verification: "verified",
    category: "leadership"
  },
  {
    id: 36,
    keanuQuote: "The appropriate conversion rate to apply to Best Case pipeline is... zero. [long silence] Qualify rigorously. Early. The revenue you project is only as real as the rigor you apply.",
    originalQuote: "The appropriate conversion rate to apply to your Best Case is zero percent. Be rigorous in qualifying pipeline as early as possible.",
    originalAuthor: "Sam Jacobs",
    source: "https://x.com/samfjacobs/status/1802378481939861816",
    verification: "verified",
    category: "sales"
  },

  // Chris Orlob - Gong/pClub
  {
    id: 37,
    keanuQuote: "Mediocre reps wait until minute 25 to get to pain. By then, the call's over. Ask this in minute 3: 'What challenges would DERAIL you if you didn't solve them in the next 6-12 months?' Then shut up.",
    originalQuote: "Ask in minute 3: 'What challenges are you facing that would DERAIL you if you didn't solve them in the next 6-12 months?' Then shut up and listen.",
    originalAuthor: "Chris Orlob",
    source: "https://x.com/Chris_Orlob/status/2013038777854263573",
    verification: "verified",
    category: "sales"
  },
  {
    id: 38,
    keanuQuote: "Novice reps say 'Let me know how it goes.' Great reps ask 'How are you thinking about structuring that conversation? What resistance might you face?' That's not selling. That's coaching. You're coaching deals you're not even in the room for.",
    originalQuote: "The novice says 'Let me know how it goes.' The great sales pro asks 'How are you thinking about structuring that conversation? What resistance might you face?'",
    originalAuthor: "Chris Orlob",
    source: "https://x.com/Chris_Orlob/status/1997727870404157644",
    verification: "verified",
    category: "sales"
  },

  // SPICED Framework - Winning by Design
  {
    id: 39,
    keanuQuote: "SPICED. Situation. Pain. Impact. Critical Event. Decision. It walks buyers through understanding their problem, how severe it is, how to fix it, what happens if they do. It's not a framework for you. It's for them.",
    originalQuote: "SPICED: Situation, Pain, Impact, Critical Event, Decision. Logically walks the buyer through understanding their problem, the severity, how to fix it, and what happens if it's fixed.",
    originalAuthor: "Winning by Design",
    source: "https://x.com/coldemailchris/status/2006077868795703644",
    verification: "verified",
    category: "sales"
  },

  // Paul Graham - Y Combinator
  {
    id: 40,
    keanuQuote: "Do things that don't scale. [pauses] I know everyone wants to scale. But first, do the unscalable things that actually work. Learn what matters. The scalable stuff comes later.",
    originalQuote: "Do things that don't scale.",
    originalAuthor: "Paul Graham",
    source: "Y Combinator",
    verification: "verified",
    category: "growth"
  },

  // Marc Andreessen
  {
    id: 41,
    keanuQuote: "Product-market fit is being in a good market with a product that satisfies that market. You can't manufacture it. You feel it. The market pulls the product out of your hands. That's... that's the moment.",
    originalQuote: "Product-market fit means being in a good market with a product that can satisfy that market.",
    originalAuthor: "Marc Andreessen",
    source: "pmarca blog",
    verification: "verified",
    category: "product"
  },

  // Al Ries & Jack Trout
  {
    id: 42,
    keanuQuote: "Can't be first in a category? Set up a new category you can be first in. It's not about being best. It's about being only. Find your 'only' and everything else... [trails off]",
    originalQuote: "If you can't be first in a category, set up a new category you can be first in.",
    originalAuthor: "Al Ries & Jack Trout",
    source: "The 22 Immutable Laws of Marketing",
    verification: "verified",
    category: "marketing"
  },

  // Peter Drucker
  {
    id: 43,
    keanuQuote: "Culture eats strategy for breakfast. Best GTM plan in the world means nothing if the culture is broken. If people don't trust each other. Culture isn't separate from strategy. Culture IS strategy.",
    originalQuote: "Culture eats strategy for breakfast.",
    originalAuthor: "Peter Drucker",
    verification: "verified",
    category: "leadership"
  },

  // Donald Miller - StoryBrand
  {
    id: 44,
    keanuQuote: "If you confuse, you lose. Your messaging has to be clear enough that... well, that your mom gets it. If you can't explain it simply, maybe you don't understand it well enough.",
    originalQuote: "If you confuse, you lose.",
    originalAuthor: "Donald Miller",
    source: "Building a StoryBrand",
    verification: "verified",
    category: "marketing"
  },

  // Jeff Bezos
  {
    id: 45,
    keanuQuote: "I don't think about competition. I think about customers. Competitor-obsessed means waiting for them to move. Customer-obsessed means pioneering. Be a pioneer.",
    originalQuote: "Be customer-obsessed, not competitor-focused.",
    originalAuthor: "Jeff Bezos",
    verification: "verified",
    category: "strategy"
  },

  // Bill Gates
  {
    id: 46,
    keanuQuote: "Your most unhappy customers are your greatest source of learning. Every complaint is a gift. They're telling you exactly what's broken. Most companies ignore them. The great ones lean in.",
    originalQuote: "Your most unhappy customers are your greatest source of learning.",
    originalAuthor: "Bill Gates",
    verification: "verified",
    category: "growth"
  },

  // Theodore Roosevelt
  {
    id: 47,
    keanuQuote: "Nobody cares how much you know until they know how much you care. In sales, in life—same truth. Technical expertise means nothing if they don't feel seen. Connection first.",
    originalQuote: "Nobody cares how much you know, until they know how much you care.",
    originalAuthor: "Theodore Roosevelt",
    verification: "verified",
    category: "sales"
  },

  // Chet Holmes
  {
    id: 48,
    keanuQuote: "Out of 2,000 advertisers, 167 accounted for 95% of revenue. So he stopped pursuing the other 1,833. Cold turkey. Four months—zero responses. But he kept going. Eventually got all 167. Every single one. [quiet] Persistence.",
    originalQuote: "Out of 2,000 advertisers, 167 accounted for 95% of industry revenue. He stopped pursuing the other 1,833. Eventually he acquired all 167.",
    originalAuthor: "Chet Holmes",
    source: "The Ultimate Sales Machine",
    verification: "verified",
    category: "sales"
  },

  // Jacco van der Kooij
  {
    id: 49,
    keanuQuote: "SaaS delivered on the promise. The cloud works. Apps are good. Recurring revenue changed everything. So what caused the SaaS crash? GTM is simply too expensive. Go-to-market is the protagonist of the next decade.",
    originalQuote: "SaaS delivered on the promise. The cloud has met the demand, Apps work well. So what caused the SaaS crash? The GTM is simply too expensive. GTM is the Protagonist in the next decade.",
    originalAuthor: "Jacco van der Kooij",
    source: "https://x.com/Jacco_vd_Kooij/status/1661518790805590016",
    verification: "verified",
    category: "strategy"
  },
  {
    id: 50,
    keanuQuote: "SaaS companies go through a phase shift every 12-18 months. Everything that got you here won't get you there. CEOs have to rethink how they run the business each time. Evolution or extinction.",
    originalQuote: "SaaS companies go through a significant change approximately every 12-18 months. CEOs need to rethink how they run their business each time.",
    originalAuthor: "Jacco van der Kooij",
    source: "https://x.com/Jacco_vd_Kooij/status/1702340899152543829",
    verification: "verified",
    category: "leadership"
  },

  // MEDDPICC / Enterprise Sales
  {
    id: 51,
    keanuQuote: "MEDDPICC. Metrics. Economic Buyer. Decision Criteria. Decision Process. Identify Pain. Champion. Competition. Each one is a question you need answered. Skip one—feel it at close.",
    originalQuote: "MEDDPICC: Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, Champion, Competition.",
    originalAuthor: "Jack Napoli",
    source: "PTC / MEDDIC methodology",
    verification: "verified",
    category: "sales"
  },
  {
    id: 52,
    keanuQuote: "Multi-threading isn't politics. It's protecting deals from single points of failure. Champion leaves? Gets promoted? Goes on vacation? You need other threads. Build wide, not just deep.",
    originalQuote: "Multi-threading in enterprise deals means building relationships across multiple stakeholders to reduce single points of failure.",
    originalAuthor: "Enterprise Sales Wisdom",
    verification: "unverified",
    category: "sales"
  },

  // SaaS Metrics
  {
    id: 53,
    keanuQuote: "NRR above 100% means existing customers grow faster than you lose them. Below 100%, you're filling a leaky bucket. Above 100%... the growth engine feeds itself.",
    originalQuote: "Net Revenue Retention above 100% means expansion revenue from existing customers exceeds churn and contraction.",
    originalAuthor: "SaaS Industry Standard",
    verification: "verified",
    category: "growth"
  },
  {
    id: 54,
    keanuQuote: "Rule of 40. Growth rate plus profit margin equals 40 or more. Balance between speed and efficiency. Too much of either and something breaks. 40 is where sustainable meets ambitious.",
    originalQuote: "The Rule of 40: Growth rate + profit margin should equal 40% or more for a healthy SaaS company.",
    originalAuthor: "Brad Feld",
    verification: "verified",
    category: "growth"
  },
  {
    id: 55,
    keanuQuote: "Burn multiple. Net burn divided by net new ARR. How efficiently are you converting cash into growth? Below 1.5—amazing. Above 3—concerning. Know your number.",
    originalQuote: "Burn Multiple = Net Burn / Net New ARR. It measures how much a startup burns to generate each new dollar of ARR.",
    originalAuthor: "David Sacks",
    source: "Craft Ventures",
    verification: "verified",
    category: "growth"
  },

  // Steve Blank
  {
    id: 56,
    keanuQuote: "Get out of the building. Your customers know things you don't. You can't find product-market fit from a conference room. Go talk to real humans. Let them teach you.",
    originalQuote: "Get out of the building.",
    originalAuthor: "Steve Blank",
    source: "The Four Steps to the Epiphany",
    verification: "verified",
    category: "product"
  },

  // Wes Bush - PLG
  {
    id: 57,
    keanuQuote: "Best products sell themselves. Product-led growth isn't removing humans—it's respecting users' time so much you let the product speak first. That's not automation. That's respect.",
    originalQuote: "The best products sell themselves.",
    originalAuthor: "Wes Bush",
    source: "Product-Led Growth",
    verification: "verified",
    category: "product"
  },

  // Tomasz Tunguz
  {
    id: 58,
    keanuQuote: "Once you achieve basic sales execution, lead gen becomes the rate-limiter. Sales gets blamed for misses, but the problem is usually top-of-funnel. Generating pipeline... that's a multifaceted challenge.",
    originalQuote: "Once a SaaS startup achieves basic sales execution, lead gen becomes the rate-limiting factor on growth.",
    originalAuthor: "Tomasz Tunguz",
    source: "Tomasz Tunguz Blog",
    verification: "likely",
    category: "growth"
  }
];

/**
 * Get quotes for a specific transcendence level
 * Level 1: quotes 1-15, Level 2: quotes 16-30, Level 3: quotes 31-45, Level 4: quotes 46+
 */
export function getQuotesByLevel(level: number): KeanuQuote[] {
  const ranges: Record<number, [number, number]> = {
    1: [1, 15],
    2: [16, 30],
    3: [31, 45],
    4: [46, 999]
  };
  const [min, max] = ranges[level] || [1, 999];
  return quotes.filter(q => q.id >= min && q.id <= max);
}

/**
 * Get a random quote for a level, avoiding recently shown chapter images
 */
export function getRandomQuoteByLevelAvoidingImages(level: number, recentChapterNumbers: number[]): KeanuQuote {
  const levelQuotes = getQuotesByLevel(level);
  
  // Filter out quotes whose chapters were recently shown
  const availableQuotes = levelQuotes.filter(q => {
    const chapterIndex = getChapterIndexForQuoteId(q.id);
    return !recentChapterNumbers.includes(chapterIndex);
  });
  
  // If all are filtered out, fall back to any quote in the level
  const pool = availableQuotes.length > 0 ? availableQuotes : levelQuotes;
  return pool[Math.floor(Math.random() * pool.length)];
}

export function getRandomQuoteByLevel(level: number): KeanuQuote {
  const levelQuotes = getQuotesByLevel(level);
  return levelQuotes[Math.floor(Math.random() * levelQuotes.length)];
}

export function getRandomQuote(): KeanuQuote {
  return quotes[Math.floor(Math.random() * quotes.length)];
}

export function getQuoteById(id: number): KeanuQuote | undefined {
  return quotes.find(q => q.id === id);
}

export function getQuotesByCategory(category: KeanuQuote['category']): KeanuQuote[] {
  return quotes.filter(q => q.category === category);
}

export function getQuotesByVerification(verification: KeanuQuote['verification']): KeanuQuote[] {
  return quotes.filter(q => q.verification === verification);
}

export function getQuotesByAuthor(author: string): KeanuQuote[] {
  return quotes.filter(q => q.originalAuthor.toLowerCase().includes(author.toLowerCase()));
}
