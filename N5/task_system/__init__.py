# N5 Task System
# Zo Task System MVP - Task registry and action conversation tracking

import sys
from pathlib import Path

# Ensure /home/workspace is in path for cross-module imports
_workspace_root = Path(__file__).parent.parent.parent
if str(_workspace_root) not in sys.path:
    sys.path.insert(0, str(_workspace_root))

# Temporarily disabled - action_tagger module is missing
# from .action_tagger import (
#     infer_action_conversation,
#     tag_conversation,
#     get_active_action_conversations,
#     get_task_for_conversation,
#     close_action_conversation,
#     get_conversation_details,
#     retag_conversation,
#     get_action_conversations_for_task,
# )

from .staging import (
    capture_staged_task,
    get_pending_staged_tasks,
    get_staged_task_by_id,
    generate_review_markdown,
    write_review_file,
    promote_staged_task,
    dismiss_staged_task,
    bulk_promote,
    bulk_dismiss,
    get_staged_tasks_by_source,
    cleanup_old_staged_tasks,
)

__all__ = [
    # Action tagger (temporarily disabled - module missing)
    # 'infer_action_conversation',
    # 'tag_conversation',
    # 'get_active_action_conversations',
    # 'get_task_for_conversation',
    # 'close_action_conversation',
    # 'get_conversation_details',
    # 'retag_conversation',
    # 'get_action_conversations_for_task',
    # Staging
    'capture_staged_task',
    'get_pending_staged_tasks',
    'get_staged_task_by_id',
    'generate_review_markdown',
    'write_review_file',
    'promote_staged_task',
    'dismiss_staged_task',
    'bulk_promote',
    'bulk_dismiss',
    'get_staged_tasks_by_source',
    'cleanup_old_staged_tasks',
]
