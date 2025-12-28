---
created: 2025-12-26
last_edited: 2025-12-26
version: 1.0
type: build_plan
status: draft
provenance: con_KFHX2cKVKuJcfyRb
---

# Plan: Workout Dashboard Arsenal Overhaul

**Objective:** Transform the generic SaaS-style health dashboard into a family-facing "Arsenal Trophy Room" that tracks 10K readiness via a Squad Status hierarchy and Arsenal-themed achievements.

**Trigger:** V's feedback on generic design, request for Arsenal branding, and desire for an accurate "Squad Status" progress narrative for family members.

**Key Design Principle:** Plans are FOR AI execution, not human review. V sets up the plan; Zo reads and executes it step-by-step without human intervention.

---

## Open Questions

- [ ] Does the `workouts` table in SQLite contain `pace` or `duration` for the 1-hour "Legend" check? (Will check in Phase 2)
- [ ] Are there specific Arsenal high-res assets available, or should we stick to CSS/Icon-based branding? (Default: CSS + Tabler Icons)

---

## Checklist

### Phase 1: Structural Gut & Branding
- ☐ Remove Sidebar and SidebarProvider from `Dashboard.tsx`
- ☐ Center layout and remove SaaS-style navigation elements
- ☐ Update `styles.css` with Arsenal palette (Red, White, Gold)
- ☐ Update `site-header.tsx` with Arsenal branding
- ☐ Test: Layout is centered and visually Arsenal-themed

### Phase 2: Logic & Hierarchy Integration
- ☐ Update `server.ts` to expose "Longest Run" and "Best 10K Time"
- ☐ Update `use-health-data.ts` to include `squadStatus` and `readinessPercent`
- ☐ Implement the Squad Hierarchy logic (Academy -> Reserves -> First Team -> Legend)
- ☐ Test: Longest run correctly maps to the intended Arsenal legend/status

### Phase 3: Visual Trophy Room
- ☐ Create/Update `SectionCards` with the new Squad Status and RHR "Medical" focus
- ☐ Implement "The Cannon" progress track visual
- ☐ Add "Achievement Room" section with Arsenal Legends
- ☐ Test: Progress bar accurately reflects 10K readiness; RHR visible for family doctors

---

## Phase 1: Structural Gut & Branding

### Affected Files
- `Sites/workout-legal/src/pages/Dashboard.tsx` - UPDATE - Remove sidebar/provider, center layout.
- `Sites/workout-legal/src/styles.css` - UPDATE - Inject Arsenal palette.
- `Sites/workout-legal/src/components/site-header.tsx` - UPDATE - Arsenal branding in header.

### Changes

**1.1 Remove Sidebar:**
Remove `SidebarProvider`, `AppSidebar`, and `SidebarInset`. Replace with a standard `max-w-7xl mx-auto` container.

**1.2 Arsenal Palette:**
Set primary color to Arsenal Red (`#EF0107`), secondary to White, and accents to Gold (`#DBA111`).

### Unit Tests
- Sidebar is gone.
- Page content is centered.
- Header shows "Arsenal" or Arsenal-themed logo/text.

---

## Phase 2: Logic & Hierarchy Integration

### Affected Files
- `Sites/workout-legal/server.ts` - UPDATE - Query longest run and best 10K time.
- `Sites/workout-legal/src/hooks/use-health-data.ts` - UPDATE - Expose status logic.

### Changes

**2.1 SQL Expansion:**
Modify the SQLite query to find the single longest run distance in the last 30 days and the fastest 10K if it exists.

**2.2 Status Mapping:**
- < 5km: **Academy** (Jack Wilshere)
- 5km - 9.9km: **Reserves** (Bukayo Saka)
- 10km (completed): **First Team** (Vieira/Henry)
- 10km < 1hr: **Legend** (Dennis Bergkamp)

### Unit Tests
- Hook returns correct `squadStatus` string based on distance.
- `readinessPercent` is `(distance / 10) * 100`.

---

## Phase 3: Visual Trophy Room

### Affected Files
- `Sites/workout-legal/src/components/section-cards.tsx` - UPDATE - Squad Status focus.
- `Sites/workout-legal/src/components/progress-cannon.tsx` - CREATE - SVG Cannon progress track.

### Changes

**3.1 Trophy Cards:**
The first card should be "Squad Status" with the Legend's name and image/icon. The second card should be "Resting Heart Rate" (Medical Focus).

**3.2 Cannon Track:**
A progress bar where the "thumb" is the Arsenal Cannon icon, moving across a red/white track.

---

## Success Criteria

1. Dashboard has NO sidebar and is centered.
2. Theme is unmistakably Arsenal (Red/White/Gold).
3. Progress is calculated as % of 10K distance.
4. "Squad Status" correctly displays Henry/Vieira/Bergkamp based on distance and time.
5. RHR is prominently displayed for "family doctors."

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Data missing for longest run | Default to "Transfer List" / 0% until first run synced. |
| 10K under 1hr hard to calculate | Use `total_seconds` / `distance` from DB if available. |

---

## Level Upper Review

### Counterintuitive Suggestions Received:
1. Styled like a Matchday Programme (Rejected by V in favor of Trophy Room).
2. "Efficiency Score" for doctors (Incorporate into RHR/Medical card).

### Incorporated:
- Accuracy-first progress (Finish = First Team, <1hr = Legend).
- Medical focus for RHR.

### Rejected (with rationale):
- Matchday Programme: V preferred the "Trophy Room" progress narrative.

