# W5: UI Worker Handoff
**Worker ID:** W5-UI  
**Spawned From:** con_MuvXIR7jXZjZxlND (Build Orchestrator)  
**Dependencies:** W1 (Schema), W2 (Calculator) must complete first  
**Estimated Time:** 45 minutes

---

## Your Mission

Update the productivity dashboard UI (`index.tsx`) to display the **team status career progression** front and center, making it the primary focus of the interface.

You're building the **player's view** - what V sees when he checks his status each morning.

---

## Context: What Exists Now

### Current Dashboard
- **File:** `/home/workspace/Sites/productivity-dashboard/index.tsx`
- **Tech Stack:** Bun + Hono + JSX server-side rendering
- **Current Layout:**
  - Header: "Arsenal Productivity"
  - RPI stat card (main metric)
  - Grid of mini-stats (emails, XP, level, streak)
  - Mobile-responsive, Arsenal red/white theme

### Current Database Schema (After W1)
```sql
-- You'll query these tables:
team_status_history (date, status, days_in_status, previous_status, reason)
career_stats (metric, value, last_updated)
daily_stats (date, rpi, emails_sent, expected_emails, level, streak_days)
```

---

## Your Task Breakdown

### 1. Add New API Endpoints

**Endpoint: `/api/status`**
```typescript
// Returns current team status
{
  current_status: "first_team",
  days_in_status: 12,
  trajectory: "stable",  // "rising", "falling", "stable"
  last_changed: "2025-10-18",
  reason: "Consistent performance"
}
```

**Endpoint: `/api/career`**
```typescript
// Returns career statistics
{
  total_days_first_team: 45,
  total_days_squad: 12,
  total_promotions: 5,
  total_demotions: 2,
  highest_status: "first_team",
  current_probation: false
}
```

### 2. Redesign Dashboard Layout

**New Visual Hierarchy:**
```
┌─────────────────────────────────────┐
│  [TEAM STATUS BANNER] ← NEW!        │
│  🟢 First Team Starter              │
│  Day 12 in status | ↗️ Rising        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Today's Performance                │
│  RPI: 145% | 8/5 emails             │
└─────────────────────────────────────┘

┌──────────────┬──────────────────────┐
│ Career Stats │  Weekly Trend        │
│ (new section)│  (chart optional)    │
└──────────────┴──────────────────────┘
```

**Status Banner Requirements:**
- Full-width, prominent position (top of page)
- Dynamic background color based on status:
  - Transfer List: `#8B0000` (dark red)
  - Reserves: `#FF6B35` (orange-red)
  - Squad Member: `#FFD700` (gold/yellow)
  - First Team: `#00A86B` (Arsenal green)
  - Invincible: `#C0C0C0` (silver)
  - Legend: `#FFD700` with sparkle effect (gold)
- Show: Status name, days in status, trajectory icon
- On click/tap: Show modal with status change history

### 3. Status Display Components

**Status Badge Component:**
```typescript
function StatusBadge({ status, daysInStatus, trajectory }) {
  const statusConfig = {
    'transfer_list': { emoji: '🚫', label: 'Transfer List', color: '#8B0000' },
    'reserves': { emoji: '🟠', label: 'Reserves', color: '#FF6B35' },
    'squad_member': { emoji: '🟡', label: 'Squad Member', color: '#FFD700' },
    'first_team': { emoji: '🟢', label: 'First Team Starter', color: '#00A86B' },
    'invincible': { emoji: '⭐', label: 'Invincible Form', color: '#C0C0C0' },
    'legend': { emoji: '👑', label: 'Arsenal Legend', color: '#FFD700' }
  };
  
  const config = statusConfig[status];
  const trajectoryIcon = trajectory === 'rising' ? '↗️' : 
                         trajectory === 'falling' ? '↘️' : '→';
  
  return (
    <div class="status-banner" style={`background: ${config.color}`}>
      <h2>{config.emoji} {config.label}</h2>
      <p>Day {daysInStatus} in status | {trajectoryIcon} {trajectory}</p>
    </div>
  );
}
```

**Career Stats Panel:**
```typescript
function CareerStats({ stats }) {
  return (
    <div class="career-panel">
      <h3>Career Statistics</h3>
      <div class="stat-row">
        <span>Days as First Team:</span>
        <strong>{stats.total_days_first_team}</strong>
      </div>
      <div class="stat-row">
        <span>Total Promotions:</span>
        <strong>{stats.total_promotions}</strong>
      </div>
      <div class="stat-row">
        <span>Total Demotions:</span>
        <strong>{stats.total_demotions}</strong>
      </div>
      <div class="stat-row">
        <span>Highest Status:</span>
        <strong>{formatStatus(stats.highest_status)}</strong>
      </div>
    </div>
  );
}
```

### 4. Mobile Optimization

- Status banner must be readable on 375px width screens
- Touch-friendly tap targets (min 44px)
- Career stats should stack vertically on mobile
- Use system fonts for performance

### 5. CSS Updates

**Add these styles:**
```css
.status-banner {
  padding: 2rem;
  text-align: center;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  color: white;
  font-weight: bold;
}

.status-banner h2 {
  font-size: 1.8rem;
  margin: 0 0 0.5rem 0;
}

.status-banner p {
  font-size: 1.1rem;
  opacity: 0.9;
}

.career-panel {
  background: rgba(255,255,255,0.05);
  padding: 1.5rem;
  border-radius: 8px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.stat-row:last-child {
  border-bottom: none;
}
```

---

## Files You'll Modify

1. **`/home/workspace/Sites/productivity-dashboard/index.tsx`**
   - Add `/api/status` and `/api/career` endpoints
   - Update main page layout
   - Add StatusBadge and CareerStats components
   - Update CSS

---

## Technical Constraints

- **Database:** Use existing Bun SQLite connection (`/home/workspace/productivity_tracker.db`)
- **No external deps:** Work within existing Hono + Bun setup
- **Server-side rendering:** Keep it simple, no client-side JS needed
- **Performance:** Queries should be fast (<50ms)

---

## Success Criteria

- [ ] New API endpoints return correct data
- [ ] Status banner displays prominently with correct colors
- [ ] Trajectory indicator updates based on last 3 days
- [ ] Career stats panel shows accurate counts
- [ ] Mobile-responsive (tested at 375px width)
- [ ] Arsenal branding maintained (red/white theme)
- [ ] Page loads in <500ms

---

## Testing Checklist

**Unit Tests:**
- [ ] `/api/status` returns valid JSON
- [ ] `/api/career` calculates totals correctly
- [ ] Status colors map correctly

**Visual Tests:**
- [ ] View on desktop (1920px)
- [ ] View on mobile (375px)
- [ ] Check all 6 status colors render correctly
- [ ] Trajectory icons display properly

**Integration Tests:**
- [ ] After W3 runs `rpi_calculator.py`, dashboard updates
- [ ] Career stats increment correctly after status changes

---

## Return Deliverable Format

```markdown
# W5-UI Completion Report

Status: ✅ COMPLETE

## Changes Made

Files Modified:
- /home/workspace/Sites/productivity-dashboard/index.tsx (+200 lines)

New Endpoints:
- GET /api/status
- GET /api/career

## Testing Results

- [x] API endpoints tested
- [x] Mobile responsive verified
- [x] All status colors confirmed
- [x] Performance <500ms load time

Screenshots:
[Describe what the dashboard looks like now]

Notes:
[Any design decisions, challenges overcome]

Dashboard URL: https://productivity-dashboard-va.zocomputer.io
```

---

**Orchestrator:** con_MuvXIR7jXZjZxlND  
**Your Mission:** Make the status visible, beautiful, motivating. V checks this every morning.  
**Priority:** HIGH - This is what V sees.

Good luck! 🎨

---
**Created:** 2025-10-30 01:40 ET
