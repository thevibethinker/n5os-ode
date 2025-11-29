# N5 Scripts & Tools

## Core Infrastructure

### N5 Command Dispatcher (`n5_dispatcher.py`)
**Entry point for `n5 <command>` CLI.**
- Prioritizes **Prompts** over scripts.
- Searches `Prompts/`, `N5/prompts/`, `N5/workflows/`.
- Fuzzy matches user commands to prompt filenames.
- Launches AI Workers via `n5_launch_worker.py`.

Usage: `n5 <command> [args]`

### N5 Context Loader (`n5_load_context.py`)
**Just-In-Time Context Injection.**
- Loads rule sets based on intent (`build`, `strategy`, `writer`).
- Driven by `N5/prefs/context_manifest.yaml`.

Usage: `python3 N5/scripts/n5_load_context.py <intent>`

### N5 Worker Launcher (`n5_launch_worker.py`)
**Spawns parallel worker threads.**
- Creates assignment files in `Records/Temporary`.
- Supports worker types (`build`, `research`, etc.).

Usage: `n5 launch-worker --parent <id> --type <type>`

## Legacy / Vestigial
- `n5_conversation_end_v2.py`: Vestigial wrapper (use `Close Conversation.prompt.md` via `n5 close` instead).

