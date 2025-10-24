# Content Library - Example Snippets to Add

Here are examples of snippets V should consider adding to the content library:

## Bio Variants

### Short Bio
```bash
python3 N5/scripts/content_library.py add \
  --id vrijen_bio_short \
  --type snippet \
  --title "Vrijen Bio (Short)" \
  --content "CEO & Co-Founder of Careerspan. Former McKinsey consultant with a decade of career coaching experience and four years building in tech." \
  --tag context:email \
  --tag context:social \
  --tag audience:general \
  --tag purpose:introduction \
  --tag tone:professional \
  --tag entity:vrijen \
  --notes "Brief intro for emails and social bios"
```

### Medium Bio
```bash
python3 N5/scripts/content_library.py add \
  --id vrijen_bio_medium \
  --type snippet \
  --title "Vrijen Bio (Medium)" \
  --content "Vrijen Attawar is the CEO and Co-Founder of Careerspan, an AI-powered career guidance platform. With a decade of experience as a career coach and four years as an entrepreneur in tech, Vrijen combines deep expertise in human potential development with modern technology. Prior to Careerspan, he was a consultant at McKinsey & Company." \
  --tag context:website \
  --tag context:presentation \
  --tag audience:general \
  --tag audience:professional \
  --tag purpose:introduction \
  --tag purpose:bio \
  --tag tone:professional \
  --tag entity:vrijen \
  --notes "Standard bio for websites and presentations"
```

## Company Descriptions

### Elevator Pitch
```bash
python3 N5/scripts/content_library.py add \
  --id careerspan_elevator_pitch \
  --type snippet \
  --title "Careerspan Elevator Pitch" \
  --content "Careerspan helps job seekers find roles where they'll actually thrive. We combine AI-powered alignment analysis with human coaching to match candidates with opportunities based on deep fit, not just keywords on a resume." \
  --tag context:email \
  --tag context:pitch \
  --tag context:meeting \
  --tag audience:investors \
  --tag audience:general \
  --tag purpose:pitch \
  --tag purpose:marketing \
  --tag tone:professional \
  --tag entity:careerspan \
  --notes "30-second elevator pitch"
```

### Value Proposition (Job Seekers)
```bash
python3 N5/scripts/content_library.py add \
  --id careerspan_value_prop_jobseekers \
  --type snippet \
  --title "Careerspan Value Prop (Job Seekers)" \
  --content "Stop wasting time on jobs that aren't right for you. Careerspan analyzes your unique strengths, values, and career trajectory to identify roles where you'll excel—not just get hired, but actually thrive. Get personalized coaching and alignment reports that help you stand out to the right employers." \
  --tag context:email \
  --tag context:marketing \
  --tag context:website \
  --tag audience:job_seekers \
  --tag audience:candidates \
  --tag purpose:marketing \
  --tag purpose:education \
  --tag tone:professional \
  --tag entity:careerspan \
  --notes "B2C value proposition for job seekers"
```

### Value Proposition (Employers)
```bash
python3 N5/scripts/content_library.py add \
  --id careerspan_value_prop_employers \
  --type snippet \
  --title "Careerspan Value Prop (Employers)" \
  --content "Hire for fit, not just credentials. Careerspan's alignment analysis goes beyond resumes to identify candidates who will thrive in your roles and culture. Reduce turnover, improve performance, and build teams where everyone is set up for success." \
  --tag context:email \
  --tag context:pitch \
  --tag context:marketing \
  --tag audience:employers \
  --tag audience:recruiters \
  --tag purpose:sales \
  --tag purpose:partnership \
  --tag tone:professional \
  --tag entity:careerspan \
  --notes "B2B value proposition for employers"
```

## Email Signatures

### Standard Signature
```bash
python3 N5/scripts/content_library.py add \
  --id vrijen_email_signature \
  --type snippet \
  --title "Vrijen Email Signature" \
  --content "Vrijen Attawar\nCEO & Co-Founder, Careerspan\nvrijen@mycareerspan.com\n[Calendly link]" \
  --tag context:email \
  --tag audience:general \
  --tag purpose:signature \
  --tag tone:professional \
  --tag entity:vrijen \
  --notes "Standard email signature - replace [Calendly link] with appropriate meeting link"
```

## Zo Partnership Copy

### Zo Intro Snippet
```bash
python3 N5/scripts/content_library.py add \
  --id zo_intro_snippet \
  --type snippet \
  --title "Zo Computer Intro (for founders)" \
  --content "I've been using Zo Computer (use code VATT50 for 50% off API costs) and it's been a game-changer for building without a technical co-founder. It's essentially AI-powered infrastructure that lets you automate workflows, build tools, and ship product without traditional engineering overhead." \
  --tag context:email \
  --tag context:chat \
  --tag context:meeting \
  --tag audience:founders \
  --tag audience:builders \
  --tag purpose:referral \
  --tag purpose:recommendation \
  --tag tone:professional \
  --tag entity:zo_partnership \
  --notes "Intro copy when recommending Zo to founders"
```

## Marketing Messaging

### Problem Statement (Job Search)
```bash
python3 N5/scripts/content_library.py add \
  --id problem_statement_job_search \
  --type snippet \
  --title "Problem Statement (Job Search Pain)" \
  --content "Most job seekers spend months applying to hundreds of roles, only to end up in positions where they're miserable or underperforming. The problem isn't lack of opportunity—it's lack of alignment. Traditional job search treats candidates like keyword-matching machines instead of complex humans with unique strengths and values." \
  --tag context:email \
  --tag context:pitch \
  --tag context:marketing \
  --tag context:website \
  --tag audience:job_seekers \
  --tag audience:investors \
  --tag purpose:marketing \
  --tag purpose:pitch \
  --tag tone:professional \
  --tag entity:careerspan \
  --notes "Problem framing for marketing and pitches"
```

## Common Responses

### Meeting Request Accept
```bash
python3 N5/scripts/content_library.py add \
  --id meeting_accept_template \
  --type snippet \
  --title "Meeting Request Accept Template" \
  --content "Looking forward to it! I've sent you a calendar invite. Let me know if you need anything ahead of our conversation." \
  --tag context:email \
  --tag audience:general \
  --tag purpose:scheduling \
  --tag tone:professional \
  --notes "Quick response when accepting meeting requests"
```

---

## Usage Tips

1. **Add bio variants first** - You'll use these constantly in emails
2. **Create audience-specific pitches** - Different messaging for investors, job seekers, employers
3. **Build template responses** - For common scenarios (meeting accepts, follow-ups, intro requests)
4. **Tag thoroughly** - Multiple tags enable precise retrieval
5. **Use notes field** - Add context on when to use each snippet

## Next Steps

After adding snippets, test the search:

```bash
# Find all founder-focused content
python3 N5/scripts/content_library.py search --tag audience:founders

# Find bio snippets
python3 N5/scripts/content_library.py search --query "bio" --type snippet

# Export investor materials
python3 N5/scripts/content_library.py export --tag audience:investors --format markdown
```
