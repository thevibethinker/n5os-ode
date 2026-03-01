# Zo-Native Prompt Examples

Examples of implementation-ready prompts a caller could paste into Zo. Each demonstrates a different capability.

---

## 1. Morning Briefing Agent (Scheduled Agent + Integrations)

> Create a scheduled agent that runs every weekday at 7 AM Eastern. It should:
> 1. Check my Google Calendar for today's events
> 2. Scan my last 10 Gmail messages for anything flagged urgent
> 3. Search the web for news about [my industry]
> 4. Send me a text message with: today's schedule, any urgent emails, and one relevant headline
>
> Keep the text under 500 characters. If no urgent emails, just say "inbox clear."

---

## 2. Client Follow-Up Tracker (Rule + Scheduled Agent + Gmail)

> Set up two things:
>
> First, create a rule: "When I mention a client meeting happened, log the client name, date, and any follow-up items to Documents/client-tracker.md"
>
> Second, create a weekly scheduled agent (Mondays at 9 AM) that reads Documents/client-tracker.md, identifies any follow-ups older than 5 days without resolution, and emails me a reminder list with suggested follow-up messages for each.

---

## 3. Content Idea → LinkedIn Draft (Skill + File Workflow)

> Build a skill called "linkedin-drafter" that does this:
> 1. I drop a rough note into Documents/Content-Ideas/
> 2. When I say "draft linkedin from [filename]", read the note
> 3. Ask me 3 clarifying questions: who's the audience, what's the one takeaway, what tone (professional/casual/provocative)
> 4. Generate a LinkedIn post under 1300 characters using my answers
> 5. Save the draft to Documents/Content-Drafts/ with today's date in the filename
>
> Never post anything automatically. Always show me the draft first.

---

## 4. Personal Health Check-In (Scheduled Agent + SMS)

> Create a daily scheduled agent at 8 PM that texts me asking: "How was your energy today? (1-5) Sleep last night? Any symptoms?"
>
> Create a rule: when I reply with numbers and health info via text, log it to Documents/health-log.md with the date.
>
> Create a second weekly agent (Sundays at 10 AM) that reads Documents/health-log.md, identifies any 3+ day trends (declining energy, recurring symptoms), and texts me a brief pattern summary with one suggestion.

---

## 5. Meeting Notes Processor (Persona + File Workflow)

> Create a persona called "Meeting Analyst" with this prompt: "You process meeting transcripts into structured intelligence. For every transcript, extract: attendees, key decisions, action items with owners, strategic insights, and open questions. Be thorough but concise. Format as markdown sections."
>
> When I upload a transcript to Documents/Meetings/Raw/ and say "process meeting", switch to Meeting Analyst, read the file, generate the structured output, and save it to Documents/Meetings/Processed/ with the same filename.

---

## 6. Price Drop Monitor (Scheduled Agent + Web Browsing)

> Create a scheduled agent that runs daily at noon and checks these product pages: [URL1], [URL2], [URL3].
>
> For each URL, read the page and extract the current price. Compare against the prices from yesterday (store them in Documents/price-tracker.md).
>
> If any price dropped by more than 10%, text me immediately with the product name, old price, new price, and the URL. Otherwise, silently update the tracker file.

---

## 7. Survey Results Dashboard (Dataset + zo.space + Agent)

> Help me set up a data pipeline:
> 1. Import my survey CSV (I'll upload it) as a Zo Dataset
> 2. Create a zo.space dashboard page at /survey-results that shows: total responses, average scores per question, and a breakdown of the top 3 most common free-text themes
> 3. Make the page public so I can share the link
> 4. Create a scheduled agent that re-imports updated CSV data every 12 hours and refreshes the dashboard
>
> Before building, ask me about: the survey structure, which questions are quantitative vs qualitative, and what insights matter most to me.

---

## 8. Inbox Triage System (Rule + Gmail + Airtable)

> Build an automated email triage system:
>
> Create a rule: "When processing emails, classify each as: ACTION (needs my response), FYI (read later), DELEGATE (forward to someone), or ARCHIVE (skip)."
>
> Create a morning scheduled agent (7:30 AM weekdays) that:
> 1. Reads my 20 most recent unread Gmail messages
> 2. Classifies each using the rule above
> 3. Logs all ACTION items to Airtable with subject, sender, and urgency (high/medium/low)
> 4. Emails me a summary: ACTION items first with one-line context, then counts for other categories
>
> Ask me first: which senders are always ACTION? Any domains to always ARCHIVE?

---

## 9. Weekly Business Metrics Report (Integrations + Scheduled Agent)

> Create a Friday 5 PM scheduled agent that compiles my weekly business report:
> 1. Count emails sent and received this week via Gmail
> 2. List all meetings from this week via Google Calendar
> 3. Check my Airtable "Sales Pipeline" for any deals that changed status this week
> 4. Search the web for any news mentioning [my company name]
> 5. Compile into a clean email report with sections: Communications, Meetings, Pipeline, Press
>
> Send via email with subject "Weekly Wrap: [date range]"

---

## 10. Personal Knowledge Base Builder (zo.space + Rule + File Workflow)

> I want to build a personal wiki:
>
> Create a rule: "When I share a URL with 'save this', download the article and save a clean summary to Knowledge/articles/ with the title as filename."
>
> Create a zo.space page at /wiki that reads all files in Knowledge/articles/ and displays them as a searchable, categorized list with titles, dates, and first-paragraph previews.
>
> Make the page private (just for me). When I click an article title, show the full summary.
>
> Before building, ask me: what categories do I want, and how should articles be tagged?
