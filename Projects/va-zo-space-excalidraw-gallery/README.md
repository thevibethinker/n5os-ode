---
created: 2026-02-06
last_edited: 2026-02-06
version: 1.0
provenance: con_A6c99gs3C9tU3S2O
---

# Excalidraw Gallery for va.zo.space

A public gallery of explorable Excalidraw canvases at [va.zo.space/sketches](https://va.zo.space/sketches).

## Live URLs

- **Gallery**: https://va.zo.space/sketches
- **View a canvas**: https://va.zo.space/sketches/view?id={id}
- **Direct viewer**: https://va.zo.space/excalidraw/viewer.html?id={id}

## How to Add a New Sketch

### 1. Create your canvas on excalidraw.com
- Go to [excalidraw.com](https://excalidraw.com)
- Create your drawing
- **Tip**: Use light-colored strokes (white, light grey) — the viewer inverts colors for dark mode

### 2. Export the canvas
- Click the hamburger menu (☰) → "Export"
- Choose "Save to file" → downloads a `.excalidraw` file (this is JSON)
- Rename it to a slug like `my-canvas.json`

### 3. Upload the scene file
Save the JSON to `/home/workspace/Projects/va-zo-space-excalidraw-gallery/scenes/` and then upload:

```bash
# Copy to workspace
cp ~/Downloads/my-canvas.excalidraw /home/workspace/Projects/va-zo-space-excalidraw-gallery/scenes/my-canvas.json
```

Then ask Zo to run:
```
update_space_asset(
  source_file="/home/workspace/Projects/va-zo-space-excalidraw-gallery/scenes/my-canvas.json",
  asset_path="/excalidraw/scenes/my-canvas.json"
)
```

### 4. Update the gallery index
Edit `gallery.json` to add your new item:

```json
{
  "id": "my-canvas",
  "title": "My Canvas Title",
  "subtitle": "A brief description",
  "scene_url": "/excalidraw/scenes/my-canvas.json",
  "tags": ["tag1", "tag2"],
  "updated": "2026-02-06"
}
```

Then upload the updated gallery:
```
update_space_asset(
  source_file="/home/workspace/Projects/va-zo-space-excalidraw-gallery/gallery.json",
  asset_path="/excalidraw/gallery.json"
)
```

## Architecture

```
Projects/va-zo-space-excalidraw-gallery/
├── README.md           # This file
├── viewer.html         # Excalidraw viewer (CDN-based)
├── viewer.css          # Viewer styles
├── gallery.json        # Gallery index
└── scenes/
    └── zo-concept.json # Scene files (Excalidraw JSON format)
```

**zo.space routes:**
- `/sketches` — Gallery listing page (React/Tailwind)
- `/sketches/view` — Individual canvas view with embedded iframe

**zo.space assets:**
- `/excalidraw/viewer.html` — The Excalidraw viewer
- `/excalidraw/viewer.css` — Viewer styles
- `/excalidraw/gallery.json` — Gallery metadata
- `/excalidraw/scenes/*.json` — Scene data files

## Dark Mode Implementation

The Excalidraw library doesn't properly respect `viewBackgroundColor` from CDN. We use a CSS filter workaround:

```css
.viewer-root.force-dark .excalidraw canvas {
  filter: invert(0.93) hue-rotate(180deg);
}
```

This inverts the canvas colors to achieve a dark background. **Implication**: When authoring, use light colors (white/light grey) — they'll appear as dark colors in the viewer.

To disable dark mode for a specific canvas (show original colors):
```
https://va.zo.space/excalidraw/viewer.html?id=my-canvas&forceDark=0
```

## Showcase Ideas for Zo

Some ways to use this gallery to showcase the Zo concept and your creativity:

1. **Zo Architecture Map** — Visual system diagram showing how Zo works (personas, rules, skills, workflows)
2. **Careerspan Pipeline** — Flowchart of how candidates flow through the system
3. **Personal Knowledge Graph** — Your N5 mental model visualized
4. **Project Roadmaps** — Visual timelines and dependency graphs
5. **Concept Explorations** — Sketchy, hand-drawn style explanations of ideas
6. **Meeting Whiteboard Archives** — Save whiteboard sessions from meetings

The hand-drawn Excalidraw aesthetic pairs nicely with the "vibe operator" / "vibethinker" brand.
