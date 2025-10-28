# Careerspan Ticketing System (Phases 1 → 4)

This folder contains a fully-functional ticketing pipeline turning raw meeting JSON into rich, context-aware tickets ready for content creation.

## Quick start
```bash
# generate a ticket from meeting data
echo '{"core_map":"Kick-off"}' > meeting.json
python ticketing_system/cli.py meeting.json ticket.json

# API
python ticketing_system/api.py &
# POST JSON to http://localhost:5000/generate_ticket

# Automation daemon (watches ticketing_system/meetings)
nohup python ticketing_system/automation.py &

# Stats
python ticketing_system/reporting.py
```

## Key files
| file | purpose |
|------|---------|
| `schema.json` | canonical ticket schema |
| `pipeline.py` | core generation logic |
| `cli.py`      | CLI wrapper |
| `api.py`      | Flask endpoint |
| `ticket_manager.py` | interactive management CLI |
| `automation.py` | directory watcher to auto-generate |
| `reporting.py` | simple aggregate reporting |
| `prompts.py` | LLM prompt templates |
| `tickets_store.json` | persistent store |
| `/home/workspace/knowledge_base.json` | stable knowledge base |
