# Draft: Batch Tasks Email to Aki (Dry-Run)

To: <PASTE_YOUR_AKI_EMAIL>
From: <choose sender: attawar.v@gmail.com or va@zo.computer>
Subject: [N5] Batch tasks | Tomorrow

Body:
- Task: Draft recap for Client X call
  When: Tomorrow 9:30am ET
  Duration: 20m
  Priority: Normal
  Project: Careerspan
  Tags: meeting, recap
  Notes: file 'Records/Company/Meetings/2025-10-22-Client-X.md'

- Task: Send warm intro Alice → Bob (draft email)
  When: Tomorrow 10:00am ET
  Duration: 15m
  Priority: High
  Project: Networking
  Tags: warm_intro
  Notes: include context; emails in file 'Records/Company/Intros/2025-10-23-Alice-Bob.md'

- Task: Update pipeline for Candidate Y
  When: Tomorrow 11:00am ET
  Duration: 20m
  Priority: Normal
  Project: Careerspan
  Tags: recruiting
  Notes: link to file 'Records/Company/Recruiting/Candidate-Y.md'

Notes:
- This format is designed for Aki’s NL parser. Multi-task ingestion is not documented; this is an experiment. Confirm tasks created = 3.
