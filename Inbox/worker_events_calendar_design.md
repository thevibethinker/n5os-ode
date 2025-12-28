---
created: 2025-12-27
last_edited: 2025-12-27
version: 1.0
provenance: con_WoVYvJ5iACxi1PaC
worker_type: design
---
# Worker Assignment: Events Calendar Design Improvement

## Parent Context
This worker was spawned from conversation `con_WoVYvJ5iACxi1PaC` which built the Event Allow List System and Events Calendar.

## Your Task
Improve the design of the Events Calendar site at `file 'Sites/events-calendar-staging'`.

## Current State
- Site is live at: https://events-calendar-va.zocomputer.io
- Basic dark mode UI with filter buttons
- Shows events from `N5/data/luma_candidates.json`
- Decision tracking (Going/Maybe/Not Going) persists to `N5/data/event_decisions.json`

## Design Requirements
1. **Calendar View**: Add a monthly calendar grid view (in addition to list view)
2. **30-Day Window**: Show full month ahead, not just a list
3. **Visual Polish**: 
   - Better typography
   - Event cards with cover images
   - Clear date grouping (Today, Tomorrow, This Week, Later)
4. **Conflict Detection**: Show when V already has calendar events on the same day/time
5. **Quick Actions**: One-click RSVP that opens the Luma page
6. **Mobile-First**: Responsive design that works well on phone

## Files to Modify
- `Sites/events-calendar-staging/public/index.html` - Main UI
- `Sites/events-calendar-staging/server.ts` - API endpoints

## Technical Notes
- Site runs on Bun/Hono
- After changes, the service auto-restarts (or run: `bun run server.ts`)
- Test locally at http://localhost:3047

## Success Criteria
- Calendar view shows 30 days
- Events grouped by date with clear visual hierarchy
- Decision buttons work and persist
- Looks polished on mobile

## When Complete
Report back to V with a summary of changes made.

