# DEPRECATED DIRECTORY

**Status:** Deprecated as of 2025-10-17

**Reason:** Internal meetings should be placed directly in `/N5/inbox/meeting_requests/` root directory, not in a subdirectory.

**Migration:** All pending internal meeting requests have been moved to the root directory.

**Do not use this directory going forward.** The scheduled task processor scans the root directory only.

---

## Historical Context

This directory was created as part of an early routing experiment to separate internal vs external meetings. It was discovered that this separation caused internal meetings to be skipped by the automated processor.

**Solution:** All pending requests (internal or external) are now placed in the root `/N5/inbox/meeting_requests/` directory. Classification is handled via the `classification` field in the JSON metadata, not via directory structure.
