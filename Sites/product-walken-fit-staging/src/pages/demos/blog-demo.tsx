import { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { IconCalendar, IconArrowLeft, IconPencil } from "@tabler/icons-react";
import { marked } from "marked";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

/**
 * Blog demo variant - functional blog with markdown support.
 *
 * This demo reads markdown files from a `posts/` directory in your project.
 * Create `.md` files in `posts/` with frontmatter (title, date, excerpt) to publish posts.
 *
 * Example post structure:
 * ```
 * ---
 * title: My First Post
 * date: 2025-01-15
 * excerpt: A brief description
 * ---
 *
 * # Post content here
 *
 * Your markdown content...
 * ```
 *
 * To get started:
 * 1. Create a `posts/` directory in your project root
 * 2. Add markdown files with frontmatter
 * 3. Customize the styling and layout below
 */

interface BlogPost {
  slug: string;
  title: string;
  excerpt: string;
  date: string;
  content?: string;
}

const SAMPLE_POSTS: BlogPost[] = [
  {
    slug: "welcome",
    title: "Welcome to Your Blog",
    excerpt:
      "This is a demo blog powered by Zo Computer. Replace this with your own content by creating markdown files.",
    date: "2025-01-15",
    content: `This is a demo blog running on your Zo Computer. Here's how to get started:

## Getting Started

1. **Create a posts directory** - Add a \`posts/\` folder to your project
2. **Write markdown files** - Each post is a \`.md\` file with frontmatter
3. **Customize the layout** - Edit this component to match your style

## Frontmatter Format

\`\`\`yaml
---
title: Post Title
date: 2025-01-15
excerpt: Brief description
---
\`\`\`

## What's Next?

Ask Zo to help you:
- Connect to actual markdown files in your project
- Add a markdown parser (like \`marked\` or \`react-markdown\`)
- Implement tags and categories
- Add RSS feed generation
- Create a post editor

This demo component can be completely replaced or extended to fit your needs.`,
  },
  {
    slug: "markdown-example",
    title: "Markdown Rendering Example",
    excerpt:
      "See how markdown posts can be rendered with syntax highlighting, lists, and more.",
    date: "2025-01-10",
    content: `This post demonstrates what's possible with markdown rendering.

## Features You Can Add

- **Syntax highlighting** for code blocks
- Lists and nested content
- Images and media
- Tables
- Custom components

### Code Example

\`\`\`typescript
// Example TypeScript code
export async function fetchPosts(): Promise<BlogPost[]> {
  const files = await fs.readdir('./posts');
  return files.map(parseMarkdownFile);
}
\`\`\`

### Lists

1. First item
2. Second item
3. Third item

- Bullet point
- Another point

> Blockquotes work too!

---

Ready to build? Ask Zo to help customize this blog template.`,
  },
];

export default function BlogDemo() {
  const location = useLocation();
  const navigate = useNavigate();
  const params = new URLSearchParams(location.search);
  const postSlug = params.get("post");

  const [posts] = useState<BlogPost[]>(SAMPLE_POSTS);
  const currentPost = postSlug ? posts.find((p) => p.slug === postSlug) : null;

  // Get base path without query params
  const basePath = location.pathname;

  if (currentPost) {
    return (
      <main className="min-h-screen bg-background">
        <div className="mx-auto max-w-3xl px-6 py-16">
          <Button
            variant="ghost"
            className="mb-6"
            onClick={() => navigate(basePath)}
          >
            <IconArrowLeft className="mr-2 size-4" />
            Back to posts
          </Button>

          <article className="prose prose-neutral dark:prose-invert max-w-none">
            <header className="mb-8">
              <Badge variant="outline" className="mb-4">
                <IconPencil className="mr-1 size-3" />
                Blog Post
              </Badge>
              <h1 className="mb-2 text-4xl font-semibold tracking-tight">
                {currentPost.title}
              </h1>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <IconCalendar className="size-4" />
                <time dateTime={currentPost.date}>
                  {new Date(currentPost.date).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                  })}
                </time>
              </div>
            </header>

            {/*
              Static content from SAMPLE_POSTS, no sanitization needed.
              If loading user-submitted or external content, add DOMPurify:
              dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(...)) }}
            */}
            <div
              className="prose prose-neutral dark:prose-invert max-w-none"
              dangerouslySetInnerHTML={{
                __html: marked.parse(currentPost.content || ""),
              }}
            />
          </article>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto max-w-4xl px-6 py-16">
        <header className="mb-12">
          <Badge variant="outline" className="mb-4">
            Blog Demo
          </Badge>
          <h1 className="text-4xl font-semibold tracking-tight md:text-5xl">
            My Blog
          </h1>
          <p className="mt-3 text-lg text-muted-foreground">
            Powered by markdown files on your Zo Computer
          </p>
        </header>

        <Card className="mb-8 border-primary/20 bg-primary/5">
          <CardContent className="pt-6 space-y-2">
            <p className="text-sm leading-relaxed text-muted-foreground">
              <strong>How this works:</strong> This blog reads markdown files
              from your project. Create a <code>posts/</code> directory and add
              <code>.md</code> files to publish.
            </p>
            <p className="text-sm leading-relaxed text-muted-foreground">
              Ask Zo to help connect this to real markdown files, add a parser,
              or customize the layout.
            </p>
          </CardContent>
        </Card>

        <div className="space-y-6">
          {posts.map((post) => (
            <Card
              key={post.slug}
              className="cursor-pointer transition-colors hover:bg-accent/50"
              onClick={() => navigate(`${basePath}?post=${post.slug}`)}
            >
              <CardHeader>
                <div className="mb-2 flex items-center gap-2 text-sm text-muted-foreground">
                  <IconCalendar className="size-4" />
                  <time dateTime={post.date}>
                    {new Date(post.date).toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })}
                  </time>
                </div>
                <CardTitle className="text-2xl hover:text-primary">
                  {post.title}
                </CardTitle>
                <CardDescription className="text-base">
                  {post.excerpt}
                </CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    </main>
  );
}
