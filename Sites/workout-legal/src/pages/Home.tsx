import { useEffect } from "react";
import {
  IconCode,
  IconPalette,
  IconRocket,
  IconServer,
  IconSparkles,
} from "@tabler/icons-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const ideas = [
  {
    icon: IconPalette,
    title: "Personal Tools",
    description:
      "Build dashboards, trackers, or utilities tailored to you, using your local data",
  },
  {
    icon: IconCode,
    title: "APIs & Services",
    description: "Expose endpoints that work with your files and data",
  },
  {
    icon: IconServer,
    title: "Share Content",
    description: "Publish writing, galleries, or media from your computer",
  },
  {
    icon: IconSparkles,
    title: "Creative Projects",
    description: "Make generative art, games, or interactive experiences",
  },
];

export default function Home() {
  const isDev = import.meta.env.MODE !== "production";
  useEffect(() => {
    console.log(`Zo site in ${isDev ? "development" : "production"} mode.`);
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-b from-muted/40 to-background">
      <div className="mx-auto max-w-3xl px-6 py-16 md:py-24">
        <header className="mb-12 text-center">
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
            Ideas to explore
          </h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {ideas.map(({ icon: Icon, title, description }) => (
              <Card
                key={title}
                className="bg-card/60 transition-colors hover:bg-card"
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-2">
                    <Icon className="size-4 text-muted-foreground" />
                    <CardTitle className="text-base">{title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
