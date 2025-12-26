import {
  IconRocket,
  IconCode,
  IconDatabase,
  IconCloud,
  IconCheck,
  IconBrandGithub,
} from "@tabler/icons-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

/**
 * Marketing/Landing page demo - professional landing page template.
 *
 * This demo shows how to build a polished marketing site with:
 * - Hero section with CTA
 * - Features grid
 * - Pricing/plans section
 * - Testimonials
 * - Footer with links
 *
 * Fully responsive and theme-aware. Customize colors, copy, and layout
 * to match your product or service.
 */

const features = [
  {
    icon: IconCode,
    title: "Developer-Friendly",
    description:
      "Built with modern web technologies. Full TypeScript support and hot reload.",
  },
  {
    icon: IconDatabase,
    title: "Data Persistence",
    description:
      "SQLite databases included. Store and query data without external services.",
  },
  {
    icon: IconCloud,
    title: "Self-Hosted",
    description:
      "Run on your own infrastructure. Full control over your data and deployment.",
  },
  {
    icon: IconRocket,
    title: "Fast Deployment",
    description:
      "Go from idea to production in minutes. No complex setup or configuration.",
  },
];

const plans = [
  {
    name: "Starter",
    price: "$0",
    period: "forever",
    features: [
      "Up to 3 sites",
      "1GB storage",
      "Community support",
      "Basic templates",
    ],
  },
  {
    name: "Pro",
    price: "$19",
    period: "per month",
    features: [
      "Unlimited sites",
      "50GB storage",
      "Priority support",
      "Advanced templates",
      "Custom domains",
      "SSL certificates",
    ],
    popular: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "contact us",
    features: [
      "Everything in Pro",
      "Dedicated support",
      "SLA guarantees",
      "Team collaboration",
      "Advanced security",
    ],
  },
];

export default function MarketingDemo() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-background to-background" />
        <div className="relative mx-auto max-w-7xl px-6 py-24 md:py-32">
          <div className="mx-auto max-w-3xl text-center">
            <Badge variant="outline" className="mb-6">
              <IconRocket className="mr-1 size-3" />
              Now in Beta
            </Badge>
            <h1 className="mb-6 text-5xl font-bold tracking-tight md:text-6xl lg:text-7xl">
              Build web apps on{" "}
              <span className="bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                your computer
              </span>
            </h1>
            <p className="mb-8 text-xl text-muted-foreground md:text-2xl">
              Create, host, and publish websites and services without managing
              servers. Everything runs on your Zo Computer.
            </p>
            <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Button size="lg" className="w-full sm:w-auto">
                Get Started Free
              </Button>
              <Button size="lg" variant="outline" className="w-full sm:w-auto">
                <IconBrandGithub className="mr-2 size-5" />
                View on GitHub
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="mx-auto max-w-7xl px-6 py-24">
        <div className="mb-16 text-center">
          <h2 className="mb-4 text-3xl font-bold tracking-tight md:text-4xl">
            Everything you need to build
          </h2>
          <p className="text-lg text-muted-foreground">
            Powerful features that make development simple and fast
          </p>
        </div>
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => (
            <Card key={feature.title} className="border-muted">
              <CardHeader>
                <div className="mb-2 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                  <feature.icon className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-xl">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Pricing Section */}
      <section className="bg-muted/50 py-24">
        <div className="mx-auto max-w-7xl px-6">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-3xl font-bold tracking-tight md:text-4xl">
              Simple, transparent pricing
            </h2>
            <p className="text-lg text-muted-foreground">
              Choose the plan that's right for you
            </p>
          </div>
          <div className="grid gap-8 md:grid-cols-3">
            {plans.map((plan) => (
              <Card
                key={plan.name}
                className={
                  plan.popular ? "border-primary shadow-lg" : "border-muted"
                }
              >
                {plan.popular && (
                  <div className="bg-primary px-4 py-2 text-center text-sm font-medium text-primary-foreground">
                    Most Popular
                  </div>
                )}
                <CardHeader className="text-center">
                  <CardTitle className="text-2xl">{plan.name}</CardTitle>
                  <div className="mt-4">
                    <span className="text-4xl font-bold">{plan.price}</span>
                    <span className="text-muted-foreground">
                      {" "}
                      / {plan.period}
                    </span>
                  </div>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-2">
                        <IconCheck className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
                        <span className="text-sm">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <Button
                    className="mt-6 w-full"
                    variant={plan.popular ? "default" : "outline"}
                  >
                    {plan.name === "Enterprise"
                      ? "Contact Sales"
                      : "Get Started"}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="mx-auto max-w-7xl px-6 py-24">
        <Card className="border-primary/20 bg-gradient-to-br from-primary/10 via-primary/5 to-background">
          <CardContent className="p-12 text-center">
            <h2 className="mb-4 text-3xl font-bold tracking-tight md:text-4xl">
              Ready to get started?
            </h2>
            <p className="mb-8 text-lg text-muted-foreground">
              Join thousands of developers building on Zo Computer
            </p>
            <Button size="lg">Create Your First Site</Button>
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t bg-muted/30">
        <div className="mx-auto max-w-7xl px-6 py-12">
          <div className="grid gap-8 md:grid-cols-4">
            <div>
              <h3 className="mb-4 font-semibold">Product</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>Features</li>
                <li>Pricing</li>
                <li>Documentation</li>
                <li>Changelog</li>
              </ul>
            </div>
            <div>
              <h3 className="mb-4 font-semibold">Company</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>About</li>
                <li>Blog</li>
                <li>Careers</li>
                <li>Contact</li>
              </ul>
            </div>
            <div>
              <h3 className="mb-4 font-semibold">Resources</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>Community</li>
                <li>Help Center</li>
                <li>Status</li>
                <li>API Reference</li>
              </ul>
            </div>
            <div>
              <h3 className="mb-4 font-semibold">Legal</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li>Privacy</li>
                <li>Terms</li>
                <li>Security</li>
                <li>Compliance</li>
              </ul>
            </div>
          </div>
          <div className="mt-12 border-t pt-8 text-center text-sm text-muted-foreground">
            <p>© 2025 Zo Computer. This is a demo marketing page template.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
