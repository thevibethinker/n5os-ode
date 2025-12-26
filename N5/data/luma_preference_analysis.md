---
created: 2025-12-11
last_edited: 2025-12-11
version: 1.0
---

# Luma Event Preference Analysis

**Based on:** Subscribed calendars, upcoming "Going" events, and event descriptions.  
**Profile:** 86 events attended since May 2023

---

## 1. Subscribed Calendars (Direct Interest Signal)

| Calendar | Focus Area | Signal Strength |
|----------|------------|-----------------|
| **Andrew's Yeung's Tech Events** | Founder breakfasts, dinners, networking | ⭐⭐⭐ High |
| **NYC Founders Club** | Founder dinners | ⭐⭐⭐ High |
| **Marvin VC Events** | VC firesides, founder content | ⭐⭐⭐ High |
| **Beta University Events** | AI Founders, early-stage | ⭐⭐⭐ High |
| **Bond AI - New York** | AI/ML community, engineer meetups | ⭐⭐ Medium |
| **The Fourth Effect** | VC/Advisory boards | ⭐⭐ Medium |
| **Intercom** | AI Support, product | ⭐⭐ Medium |
| **Reading Rhythms NYC** | Reading/social | ⭐ Low (lifestyle) |

---

## 2. Event Type Preferences

### Strong Preferences (Attend These)
- **Intimate founder gatherings** (30-50 people, curated)
- **Breakfast/dinner formats** (vs. large mixers)
- **Pre-seed to Series A focused** events
- **Fireside chats** with interesting speakers
- **AI/Tech founder** community events
- **VC-adjacent** (meeting investors, but in founder context)

### Moderate Interest
- **Outdoor/extreme sports** with founders (12 Scrappy Founders does hikes, dirt-biking)
- **Philanthropy/giving back** topics
- **Reading/intellectual** social events

### Low/No Interest (Exclude)
- Generic networking happy hours
- Large conferences (100+ people)
- Pure social/party events without founder angle
- Yoga, meditation, fitness (per your earlier guidance)
- Concerts, art shows

---

## 3. Organizer Patterns

### Trusted Organizers (High Attendance Likely)
| Organizer | Org/Calendar | Why |
|-----------|--------------|-----|
| **Andrew Yeung** | Andrew's Mixers, fibe | "Gatsby of Silicon Alley" - curated, high-quality founder events |
| **Drew Parten** | Rho (co-hosts with Andrew) | Business banking for founders |
| **Ulrik Soderstrom** | Marvin VC | Founder-focused VC events |
| **Denis Belyavsky** | 12 Scrappy Founders | Outdoor + AI founder combo |

### Calendar/Org Reputation
- **Beta Fund** - Early-stage AI focus
- **NYC Founders Club** - Intimate dinners
- **Next Wave NYC** - Pre-seed/seed community

---

## 4. Format Preferences

| Format | Interest Level |
|--------|---------------|
| Breakfast (9-11am) | ⭐⭐⭐ High |
| Dinner (6-9pm) | ⭐⭐⭐ High |
| Fireside Chat | ⭐⭐⭐ High |
| Roundtable | ⭐⭐ Medium |
| Happy Hour | ⭐ Low (unless curated) |
| Conference | ⭐ Low |

---

## 5. Location Preferences

- **Primary:** NYC (Manhattan)
- **Secondary:** SF/Bay Area (for special events)
- **Virtual:** Yes, for firesides/talks

---

## 6. Scoring Adjustments Recommended

Based on this analysis, update `N5/config/luma_scoring.json`:

```json
{
  "category_keywords": {
    "high_priority": {
      "keywords": ["founder", "startup", "AI", "pre-seed", "seed", "series A", 
                   "breakfast", "dinner", "fireside", "curated", "intimate",
                   "roundtable", "VC", "investor"],
      "weight": 3.0
    },
    "medium_priority": {
      "keywords": ["tech", "networking", "meetup", "community", "hike", 
                   "outdoor", "pickleball", "reading"],
      "weight": 2.0
    },
    "exclude": {
      "keywords": ["concert", "yoga", "meditation", "art show", "gallery",
                   "music festival", "fitness"],
      "weight": -5.0
    }
  },
  "organizer_reputation": {
    "priority_organizers": [
      "andrew yeung", "drew parten", "ulrik soderstrom", 
      "denis belyavsky", "tushar agarwal"
    ],
    "priority_calendars": [
      "Andrew's Yeung's Tech Events", "NYC Founders Club",
      "Marvin VC Events", "12 (scrappy) founders", "Beta University Events"
    ]
  },
  "format_preferences": {
    "breakfast": 2.0,
    "dinner": 2.0,
    "fireside": 1.5,
    "roundtable": 1.0,
    "happy_hour": -0.5
  },
  "size_preferences": {
    "intimate_max": 50,
    "intimate_bonus": 1.5,
    "large_min": 100,
    "large_penalty": -1.0
  }
}
```

---

## 7. Key Insight

**You prefer quality over quantity.**

Your event pattern shows:
- Curated, invitation-only gatherings
- Repeat organizers you trust (Andrew Yeung appears multiple times)
- Founder-to-founder connection focus
- Morning or evening (not midday)
- Small groups (30-50) where real conversations happen

**Recommendation:** Weight organizer reputation heavily. If Andrew Yeung or similar trusted organizers host an event, it should score high regardless of other factors.

