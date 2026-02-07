---
created: 2026-01-27
last_edited: 2026-01-27
version: 1
provenance: con_0IinoshR6wRMxjao
---
# Even Realities G2: Forum Intelligence & Use Case Research Dossier

## Executive Summary

This dossier aggregates intelligence from r/EvenRealities, GitHub, X/Twitter, and tech forums regarding the Even Realities G2 smart glasses and R1 ring. Sources include 40+ Reddit threads, community reverse engineering projects, and early adopter testimonials.

---

## Part 1: R1 Ring Accidental Touch Workarounds

### Identified Issues

| Issue | Frequency | Root Cause | Community Workaround |
|-------|-----------|-------------|----------------------|
| Accidental Conversate activation | Common | Ring has no wear detection; first menu item triggers easily | Users wish for menu reordering to put less disruptive items first |
| Ring disconnection after water exposure | Common | Bluetooth fails after washing hands/getting wet | Must place ring in charging pod to restart; cannot restart on ring itself |
| Ring randomly popping up HUD | Reported | Head tilt trigger too sensitive or angle settings off | Restart glasses to reset |
| Bluetooth disconnection with phone locked | Occasional | iOS app background limitation | Keep phone unlocked & app in foreground; iPhone users report this more than Android |

### Community-Requested Solutions

1. **5-press ring restart**: Long press on ring touch strip to force reboot without charging pod[^1]
2. **Menu reordering**: Allow users to move Conversate (currently first) to lower position to prevent accidental activation[^1]
3. **Ring wear detection**: Prevent activation when ring is not being worn (similar to glasses wear detection)[^2]
4. **Ring accidental use detection**: Smart sensing to distinguish intentional vs accidental touches[^2]

### Temporary Workarounds

- **Turn off Heads-Up Display entirely**: Some users disable HUD completely and rely on R1 ring exclusively[^2]
- **Use ring differently**: Adjust finger placement to avoid incidental touches while washing hands or typing
- **Keep phone screen on**: iOS users report this reduces disconnection frequency
- **Gentler swipes**: Practice deliberate tap-and-swipe motion rather than casual movements

---

## Part 2: HAO 2.0 Display Optimization Tips

### HAO 2.0 (Holistic Adaptive Optics) Capabilities

The G2 uses a dual-waveguide design creating a "floating spatial display" with 27.5° FOV and up to 1,200 nits brightness[^3].

### Brightness & Visibility Settings

| Setting | Recommendation | Notes |
|---------|---------------|-------|
| **Auto-brightness** | Enable but calibrate | Users report it can be "too bright or too dark" - may need manual adjustment[^1] |
| **Max brightness (1,200 nits)** | Use for outdoor navigation | Text readable even in bright daylight without shade clip[^1] |
| **Photo-fusion clip** | Use for daytime | Hides green line visibility, makes display look more natural[^4] |
| **Yellow clip** | Use for night driving | Reduces reflection and improves contrast in low light[^4] |

### Display Calibration Tips

1. **Adjust virtual distance**: Position glasses at correct angle to maximize peripheral vision and clarity[^3]
2. **Clean lenses regularly**: Dust affects waveguide light transmission and brightness uniformity[^3]
3. **Proper fit**: UltraFit adjustment by optician can significantly improve viewing experience[^3]
4. **Endless scrolling**: Users want ability to swipe down to cycle back to first widget (currently requested)[^1]

### Display Layering (Spatial Experience)

HAO 2.0 separates information into layers:
- **Foreground**: AI prompts, quick responses
- **Background**: Navigation details, notes
- **Tip**: Focus on foreground content when you need immediate action

---

## Part 3: 15+ Advanced Use Cases from Real Users

### Professional Use Cases

1. **Tech Sales & Discovery Calls**: Sales professionals use Conversate to get real-time suggestions during product calls on speaker phone. Works better when phone is unlocked and app is active[^6]

2. **Technical Presentations**: Software engineers use Conversate in meetings covering robotics, SLAM-based odometry, IMUs, Kalman Filters - AI cues were "quite accurate" and timely[^2]

3. **University Lecture Notation**: Students use live transcription in lectures to focus on professor rather than note-taking. Transcripts can be reviewed later for vocabulary study[^5]

4. **Live Meeting Captioning**: For hard-of-hearing users or anyone who needs real-time speech-to-text in meetings[^2]

5. **Bullshit Detection**: Users jokingly call Conversate a "real life bullshit detector" - turns it on during flat earth podcasts and other questionable content discussions[^1]

6. **Language Learning**: Chinese speakers use transcription to review difficult Mandarin vocabulary after conversations[^5]

7. **Real-Time Translation in Travel**: One user reported G1 translation worked "even better than Google Translate" during a trip to China. G2's translation is now free (no Pro model required) and comparable quality[^2][^7]

### Content Creation & Performance

8. **Teleprompting for Musicians/Performers**: Works well for singing/rapping along with lyrics - AI mode automatically scrolls at singing pace. Artists love not needing to manually swipe to next page[^2]

9. **Content Creation Notes**: Creators jot ideas mid-vlog or during streams using QuickNote without breaking flow[^4]

10. **Public Speaking**: Teleprompter helps maintain eye contact during presentations while script scrolls automatically. Used by David Fiorucci as a key productivity hack[^5]

### Daily Life & Wellness

11. **Health Tracking with R1**: Ring tracks heart rate, temperature, activity. Users wish for real-time health data when viewing dashboard (currently intermittent for battery)[^1]

12. **Discreet Notifications**: Get calendar, emails, and texts without "going down the phone rabbit hole" of unlocking phone and getting distracted[^5]

13. **Walking Navigation**: Navigate walking routes (not driving currently) with turn-by-turn directions. Limited by need for 5G connection and missing trails in some areas[^3]

14. **AI Query Assistant**: Quick definitions and facts via Even AI during conversations - e.g., "What is an axolotl" definitions on the fly[^3]

15. **Golf Caddie**: Requested use case - show yardages info via HUD. Wishlist item from golfers[^1]

16. **Lyrics Display**: Hard-of-hearing users want lyrics displayed during music playback (requested feature)[^1]

17. **Daily Dashboard for Task Management**: Users like Jason Rajasinghe use Dashboard to manage daily goals and tasks without pulling out phone[^5]

### Power User / Developer Hacks

18. **PC Integration via Custom Scripts**: One developer integrated Azure OpenAI responses to display on G2 via PC. GitHub repo shows full BLE protocol reverse engineering enabling custom teleprompter from Python[^8]

19. **Third-Party Apps via MentraOS**: Install MentraOS mobile app to access community-built apps for extended functionality beyond Even app[^5]

20. **BLE Protocol Reverse Engineering**: GitHub project `i-soxi/even-g2-protocol` (51 stars, 13 forks) documents full BLE packet structure enabling developers to call G2 services directly[^8]

21. **Custom Teleprompter from Terminal**: Python script can push multi-line text directly to glasses: `python teleprompter.py "Line one\nLine two"`[^8]

### Hardware Compatibility Hacks

22. **Over-Ear Headphones**: Compatible with Sennheiser HD800S, HD6XX, Audeze LCD-2C, Audio Technica MX50. Bluetooth dongles sit behind earcups comfortably[^2]

23. **AirPods + Glasses**: Users wear AirPods simultaneously with G2s without issue[^2]

---

## Part 4: Pain Points & Unofficial Fixes

### Critical Pain Points

| Pain Point | Frequency | Unofficial Fix |
|------------|-----------|------------------|
| **R1 won't reconnect after disconnection** | High | Place in charging pod (only solution) |
| **Navigation requires strong 5G** | High | Not workable in rural areas; no offline maps[^3] |
| **Conversate lag (up to 90 seconds)** | Medium | Use in meetings where slight delay acceptable; post-meeting recaps more accurate[^3] |
| **Health data stuck at 0** | Medium | Wait for "still gathering insights..." or contact support; some reports it doesn't work on iPhone at all[^3] |
| **No driving directions** | Confirmed | Walk/cycling only currently[^3] |
| **Temperature stuck in Celsius** | Minor | No in-app workaround yet; requested[^2] |

### Known Bugs

1. **Wear Detection Failure**: Glasses sometimes don't detect being worn, preventing display. Reshaping arms or repositioning bluetooth dongles can help[^2]

2. **HUD Pops Up Randomly**: After using Navigate, HUD may keep triggering on normal walks/driving until restarted[^3]

3. **R1 Firmware Mismatch**: Glasses update but ring doesn't finish - causes communication failure. Workaround: Update via charging pod[^1]

4. **App Crashes on iOS**: G2 requires app in foreground on iPhone, drains phone battery. Not fixable by users[^5]

---

## Part 5: Community Tools & Resources

### GitHub Projects

1. **[even-g2-protocol](https://github.com/i-soxi/even-g2-protocol)** - BLE reverse engineering documentation with working examples for custom teleprompter, calendar, and notifications[^8]

### Third-Party Apps

1. **MentraOS** - Community app platform for G2 glasses (mentioned in Reddit as way to access additional apps)[^5]

2. **DisplayPlus** - Mentioned as alternative for extended functionality[^5]

### Community Hubs

- **r/EvenRealities** - Primary discussion forum
- **Even Realities Discord** - Contains reverse engineering channel with G2 protocol discussions[^8]
- **CES 2026 Reviews** - Multiple reviewers tried G2 hands-on and shared tips

---

## Part 6: Feature Requests from Community

### High-Priority Requests

1. **Menu reordering** - Move Conversate from first position to prevent accidental activation
2. **Ring restart without charger** - 5-press restart gesture
3. **Wear detection for R1** - Match glasses wear detection
4. **Driving directions** - Current Navigate only supports walking/cycling
5. **Offline maps** - Critical for use outside major cities
6. **Temperature in Fahrenheit** - Currently stuck on Celsius
7. **Google Maps integration** - Native map integration requested by multiple users
8. **Health data sync to Apple Health/Google Fit** - Currently locked to Even app
9. **Battery level queries in Even AI** - "How's my battery?" queries

### Medium-Priority Requests

10. **Endless widget scrolling** - Cycle back to first widget
11. **Hide/show widgets option** - Customize dashboard widgets
12. **Time format toggle (12H/24H)** - G1 had this, G2 removed
13. **Map location labels** - Custom labels for saved addresses
14. **Real-time health tracking toggle** - Option for live data when viewing health widget
15. **Auto-save transcription opt-out** - Some users don't want auto-saved records
16. **Even AI reading health metrics** - Ask "How was my sleep last night?"
17. **Lyrics display during music playback**
18. **Golf caddie integration** - Yardages on HUD
19. **Hearing aid battery display** - Show Phonak aid program/battery

---

## Sources

[^1]: Reddit - "My biggest G2/ R1 problems" (https://www.reddit.com/r/EvenRealities/comments/1px4wnj/my_biggest_g2_r1_problems/)
[^2]: Reddit - "G2 / R1 - 48 Hour Thoughts" (https://www.reddit.com/r/EvenRealities/comments/1pwauwx/g2_r1_48_hour_thoughts/)
[^3]: Reddit - "Even Reality G2 Glasses, R1 Ring Review (1 Week)" (https://www.reddit.com/r/EvenRealities/comments/1q44pwm/even_reality_g2_glasses_r1_ring_review_1_week/)
[^4]: Reddit comments via sensitive-agent5256 and nickakio
[^5]: EvenRealities.com testimonials via web_research
[^6]: Reddit - "G2 for work/Sales Job" (https://www.reddit.com/r/EvenRealities/comments/1pm10a2/g2_for_worksales_job/)
[^7]: Reddit - "Most detailed review of G2 is out" translation discussion
[^8]: GitHub - i-soxi/even-g2-protocol (https://github.com/i-soxi/even-g2-protocol)
