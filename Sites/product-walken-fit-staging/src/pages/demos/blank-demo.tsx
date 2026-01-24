import { useEffect } from "react";
import { Link } from "react-router-dom";
import {
  IconRocket,
  IconArticle,
  IconCalendarEvent,
  IconPresentation,
  IconChartBar,
  IconWorld,
} from "@tabler/icons-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

/**
 * Blank demo variant - minimal starting point with welcome message and links to demo templates.
 *
 * This is a demo component that can be replaced or customized to build your site.
 * Delete this file and create your own pages to get started.
 */

const demos = [
  {
    icon: IconArticle,
    title: "Blog",
    description: "Article listing with markdown rendering and post pages",
    path: "/demos/blog",
  },
  {
    icon: IconCalendarEvent,
    title: "Event Registration",
    description: "Form submission with SQLite storage and API endpoints",
    path: "/demos/event",
  },
  {
    icon: IconPresentation,
    title: "Slides",
    description: "Presentation-style content with keyboard navigation",
    path: "/demos/slides",
  },
  {
    icon: IconChartBar,
    title: "Data Dashboard",
    description: "Charts, tables, and data visualization examples",
    path: "/demos/data",
  },
  {
    icon: IconWorld,
    title: "Marketing Page",
    description: "Landing page with hero, features, and pricing sections",
    path: "/demos/marketing",
  },
];

export default function BlankDemo() {
  const isDev = import.meta.env.MODE !== "production";
  useEffect(() => {
    console.log(`Zo site in ${isDev ? "development" : "production"} mode.`);
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-b from-muted/40 to-background">
      <div className="mx-auto max-w-3xl px-6 py-16 md:py-24">
        <header className="mb-12 text-center">
          <img
            src="/images/pegasus.png"
            alt="Zo"
            className="mx-auto mb-6 size-16 rounded-xl opacity-80"
          />
          <Badge variant="outline" className="mb-4">
            <IconRocket className="size-3" />
            Running on your Zo Computer
          </Badge>
          <h1 className="text-4xl font-semibold tracking-tight md:text-5xl">
            Your new Zo site
          </h1>
          <p className="mt-3 text-lg text-muted-foreground">
            You&apos;ve just created a new site running on your Zo Computer
          </p>
        </header>

        <Card className="mb-8 bg-gradient-to-t from-primary/5 to-card shadow-xs">
          <CardHeader>
            <CardTitle>Welcome</CardTitle>
            <CardDescription>
              This is your starting point — edit it, replace it, or build on it
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm leading-relaxed text-muted-foreground">
            <p>
              Sites can host interactive pages, serve an API, or both. You can
              make as many sites as you like and control who has access.
            </p>
            <p>
              Zo can help you get started — ask to customize this page, add
              features, create local databases, or explore what's possible.
            </p>
          </CardContent>
        </Card>

        <section>
          <h2 className="mb-4 text-sm font-medium text-muted-foreground">
            Demo Templates
          </h2>
          <p className="mb-4 text-sm text-muted-foreground">
            Explore working examples to see what's possible and learn patterns
            for building your own site.
          </p>
          <div className="grid gap-3 sm:grid-cols-2">
            {demos.map(({ icon: Icon, title, description, path }) => (
              <Link key={title} to={path}>
                <Card className="h-full bg-card/60 transition-colors hover:bg-card">
                  <CardHeader className="pb-2">
                    <div className="flex items-center gap-2">
                      <Icon className="size-4 text-muted-foreground" />
                      <CardTitle className="text-base">{title}</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      {description}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
