# N5 OS Waitlist - Quick Reference

## Essential Info

**Live Site:** https://n5-waitlist-va.zocomputer.io  
**Project:** `file 'n5-waitlist/'`  
**Service:** n5-waitlist (svc_1kjHmuTDTn8)

---

## To Edit Content

1. **Edit the page:**
   ```bash
   # Open in editor
   file 'n5-waitlist/server.ts'
   ```

2. **Changes auto-reload** - Site updates automatically when you save

3. **View logs:**
   ```bash
   tail -f /dev/shm/n5-waitlist.log
   ```

---

## Key File Locations

- **Main page:** `file 'n5-waitlist/server.ts'` (line 10-onwards for HTML)
- **Logo:** `file 'n5-waitlist/public/n5-logo.jpg'`
- **LaunchList widget:** Line 577-581 in server.ts
- **Setup guide:** `file 'n5-waitlist/SETUP.md'`

---

## LaunchList Integration

**Form Key:** wB7wsV  
**Widget Line:** 577-581 in server.ts

### Custom CSS (Already added to LaunchList)
Brand colors applied via LaunchList dashboard → Custom Code → Head Code

---

## Service Management

```bash
# List services
zo services list

# View service details
zo services info n5-waitlist

# Restart (if needed)
pkill -f "bun run.*n5-waitlist" && cd /home/workspace/n5-waitlist && bun run dev
```

---

## Content Sections

1. **Hero** - Lines ~460-520
2. **Waitlist** - Lines ~570-590
3. **Capabilities Carousel** - Lines ~595-690
4. **About (Collapsible)** - Lines ~695-760
5. **FAQ** - Lines ~765-810
6. **Footer** - Lines ~820-840

---

## Brand Colors

```css
--rust: #8B3A1F;
--rust-dark: #6B2A0F;
--gold: #D4A574;
--gold-bright: #F5B941;
--cream: #FFF8F0;
```

---

## External Links

- **LinkedIn:** https://www.linkedin.com/in/vrijenattawar/
- **Zo Promo:** https://www.zo.computer/?promo=VATT50
- **LaunchList:** https://getlaunchlist.com

---

## Common Updates

### Change Headline
Search for: `<h1>N5 OS</h1>`

### Update Capabilities
Search for: `<div class="capability-card">`

### Modify FAQ
Search for: `<div class="faq-item">`

### Change CTAs
Search for: `class="btn btn-primary"` or `class="btn btn-outline"`

---

**Last Updated:** 2025-10-25
