---
created: 2026-02-12
last_edited: 2026-02-12
version: 1.0
provenance: con_0Ql8WKEVvqDsDWEp
---

# zo.space Best Practices: Building Web Things Right

## Decision Rule
- Simple pages → Use page routes with React/Tailwind
- APIs/webhooks → Use API routes with Hono
- Images/files → Upload as assets first, then reference

## The 3-Step Setup

**Pages:** Create page route, export React component, use Tailwind for styling.

**APIs:** Create API route, export function taking Context, return Response.

**Assets:** Upload files via asset tools, reference with /path/to/file.jpg in code.

**Public vs Private:** Default pages to private unless explicitly public-facing.

## A Tiny Example

**Simple page:**
```tsx
export default function About() {
  return <div className="p-8">Hello world</div>;
}
```

**API endpoint:**
```ts  
export default (c) => c.json({message: "Hello"});
```

## If It Breaks
- Build errors? Check console in zo.space panel for syntax issues
- Assets not loading? Verify asset path matches upload path exactly