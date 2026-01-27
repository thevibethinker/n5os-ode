---
created: 2026-01-24
last_edited: 2026-01-24
version: 1.0
provenance: con_wIR762ShVLHM0hZl
---

# Build Plan: vrijenattawar.com Spacing & Mobile Responsiveness

## Open Questions

None — requirements clear from conversation analysis.

## Summary

Two-pass refactor of PersonalLanding.tsx to fix:
1. **Pass 1 (Stream 1)**: Vertical spacing + name stacking for optical centering
2. **Pass 2 (Stream 2)**: Button grid + footer anchoring for mobile responsiveness

## Checklist

### Stream 1: Spacing & Name Stacking
- [ ] D1.1: Stack name (Vrijen / Attawar on separate lines)
- [ ] D1.1: Tighten badge→name gap (mb-10 → mb-6)
- [ ] D1.1: Tighten roles→buttons gap (mb-16 → mb-10)
- [ ] D1.1: Responsive logo sizing (w-20 sm:w-32)

### Stream 2: Button Grid & Footer
- [ ] D2.1: Convert buttons to CSS Grid (2-col mobile, 4-col desktop)
- [ ] D2.1: Anchor footer with flex mt-auto pattern
- [ ] D2.1: Verify all responsive breakpoints

## Affected Files

| File | Owner | Changes |
|------|-------|---------|
| `Sites/vrijenattawar-staging/src/pages/PersonalLanding.tsx` | D1.1, D2.1 | Sequential edits |

## Stream 1: Spacing & Name Stacking

**Drop D1.1** — Vertical rhythm + name centering fix

### Scope
- **Files**: `Sites/vrijenattawar-staging/src/pages/PersonalLanding.tsx`
- **Responsibilities**: 
  - Stack name on two lines (Vrijen above, Attawar below)
  - Adjust vertical spacing rhythm
  - Make logo responsive
- **Must NOT touch**: Button layout, footer structure, easter egg logic

### Changes

1. **Name stacking** — Replace single-line h1 with stacked layout:
   ```jsx
   <h1 className="mb-8 flex flex-col items-center text-5xl font-bold tracking-normal sm:text-6xl lg:text-7xl antialiased">
     <span>
       <span className="text-zinc-500">V</span>
       <span className="text-white">rijen</span>
     </span>
     <span className="text-zinc-500">Attawar</span>
   </h1>
   ```

2. **Responsive logo** — Change from fixed size:
   ```jsx
   // Before
   className="w-32 h-32 object-contain opacity-90"
   // After  
   className="w-20 h-20 sm:w-28 sm:h-28 lg:w-32 lg:h-32 object-contain opacity-90"
   ```

3. **Spacing adjustments**:
   - Badge: `mb-10` → `mb-6`
   - Name: `mb-8` → `mb-6`
   - Roles: `mb-16` → `mb-10`

### Unit Tests
- [ ] Name renders on two lines
- [ ] Logo scales at sm: and lg: breakpoints
- [ ] Vertical spacing visually balanced

---

## Stream 2: Button Grid & Footer Anchoring

**Drop D2.1** — Mobile grid + footer pinning

**Depends on**: D1.1 complete (sequential edit to same file)

### Scope
- **Files**: `Sites/vrijenattawar-staging/src/pages/PersonalLanding.tsx`
- **Responsibilities**:
  - Convert button layout to CSS Grid
  - Anchor footer to bottom
  - Ensure responsive behavior
- **Must NOT touch**: Name styling, logo, badge, easter egg logic

### Changes

1. **Button grid layout**:
   ```jsx
   <div className="grid grid-cols-2 gap-3 sm:flex sm:flex-wrap sm:justify-center sm:gap-4">
     {/* All 6 buttons in grid on mobile, flex-wrap on desktop */}
   </div>
   ```

2. **Footer anchoring** — Restructure section to use flex with mt-auto:
   ```jsx
   <section className="relative z-10 flex min-h-screen w-full flex-col items-center px-6 text-center">
     {/* Main content wrapper */}
     <div className="flex w-full flex-1 flex-col items-center justify-center py-16">
       {/* ... content ... */}
     </div>
     
     {/* Footer group - anchored to bottom */}
     <div className="mt-auto pb-6 sm:pb-10 text-center">
       {/* Cryptic hint */}
       <p className="mb-4 text-[10px] text-zinc-800 ...">...</p>
       {/* Built by */}
       <p className="text-sm text-zinc-600 ...">...</p>
     </div>
   </section>
   ```

### Unit Tests
- [ ] Buttons display as 2-column grid on mobile (<640px)
- [ ] Buttons display as flex-wrap on desktop (≥640px)
- [ ] Footer stays at bottom regardless of content height
- [ ] No overflow/scroll issues

---

## Success Criteria

1. Name appears optically centered (stacked layout)
2. Vertical spacing feels balanced — no "top-heavy" perception
3. Mobile view (<640px): 2-column button grid, smaller logo
4. Desktop view (≥768px): flex-wrap buttons, full-size logo
5. Footer anchored to bottom on all viewport heights
6. All existing easter eggs preserved (badge clicks, Konami code)

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Stream 2 edits conflict with Stream 1 | Sequential execution via `depends_on` |
| Responsive breakpoints untested | Manual preview after each stream |
| Easter egg logic accidentally broken | Explicit "must not touch" in scope |

## Alternatives Considered

1. **Single Drop for all changes** — Rejected: easier to review/rollback in two passes
2. **CSS-only fix (no stacking)** — Rejected: optical nudge is fragile across breakpoints
3. **Complete redesign** — Rejected: scope creep, current layout is fundamentally sound

## Trap Doors

None identified — all changes are easily reversible via git.
