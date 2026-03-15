# Personal Inbox

Universal landing zone for all transcript sources (Pocket, Fireflies, Fathom, manual).

Items land here as normalized folders with `manifest.json` (intake-v1 schema).
The pipeline classifies each item (meeting vs reflection), scans for Zo Take Heed
triggers, then routes to `Personal/Meetings/` or `Personal/Reflections/`.

Do not manually place files here without a manifest. Use the intake CLI:
```
python3 Skills/meeting-ingestion/scripts/meeting_cli.py intake <file>
```
