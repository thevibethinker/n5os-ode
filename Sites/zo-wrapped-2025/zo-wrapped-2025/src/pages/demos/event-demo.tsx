import { useState } from "react";
import { IconCalendarEvent, IconCheck } from "@tabler/icons-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

/**
 * Event registration demo - working example with forms, API endpoints, and SQLite database.
 *
 * This demo shows:
 * - Form validation and submission
 * - API endpoints in server.ts (POST /api/_zo/demo/register, GET /api/_zo/demo/registrations)
 * - SQLite database storage (backend-lib/db.ts)
 *
 * The form submits to /api/_zo/demo/register which stores data in a SQLite database.
 * Ask Zo to help customize the fields, add email notifications, or display
 * the list of registrations from the database.
 */

export default function EventDemo() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company: "",
    notes: "",
  });
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const response = await fetch("/api/_zo/demo/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error("Registration failed");
      }

      setSubmitted(true);

      setTimeout(() => {
        setSubmitted(false);
        setFormData({ name: "", email: "", company: "", notes: "" });
      }, 3000);
    } catch (error) {
      console.error("Registration error:", error);
      alert("Registration failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (submitted) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-green-50 to-background dark:from-green-950/20">
        <div className="mx-auto max-w-2xl px-6 py-32 text-center">
          <div className="mb-6 inline-flex h-16 w-16 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/50">
            <IconCheck className="h-8 w-8 text-green-600 dark:text-green-400" />
          </div>
          <h1 className="mb-4 text-3xl font-semibold">
            Registration Confirmed!
          </h1>
          <p className="text-lg text-muted-foreground">
            Thank you for registering. We'll send you event details soon.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-background">
      <div className="mx-auto max-w-5xl px-6 py-16">
        <header className="mb-12 text-center">
          <Badge variant="outline" className="mb-4">
            <IconCalendarEvent className="mr-1 size-3" />
            Event Registration Demo
          </Badge>
          <h1 className="text-4xl font-semibold tracking-tight md:text-5xl">
            Tech Meetup 2025
          </h1>
          <p className="mt-3 text-lg text-muted-foreground">
            January 30, 2025 • 6:00 PM - 9:00 PM
          </p>
        </header>

        <div className="grid gap-8 md:grid-cols-2">
          <div>
            <Card>
              <CardHeader>
                <CardTitle>Register for Event</CardTitle>
                <CardDescription>
                  Fill out the form below to secure your spot
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">
                      Name <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) =>
                        setFormData({ ...formData, name: e.target.value })
                      }
                      placeholder="John Doe"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email">
                      Email <span className="text-red-500">*</span>
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) =>
                        setFormData({ ...formData, email: e.target.value })
                      }
                      placeholder="john@example.com"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="company">Company (Optional)</Label>
                    <Input
                      id="company"
                      value={formData.company}
                      onChange={(e) =>
                        setFormData({ ...formData, company: e.target.value })
                      }
                      placeholder="Acme Inc"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="notes">
                      Dietary Restrictions or Notes (Optional)
                    </Label>
                    <Textarea
                      id="notes"
                      value={formData.notes}
                      onChange={(e) =>
                        setFormData({ ...formData, notes: e.target.value })
                      }
                      placeholder="Any allergies or special requirements?"
                      rows={3}
                    />
                  </div>

                  <Button
                    type="submit"
                    disabled={submitting}
                    className="w-full"
                  >
                    {submitting ? "Registering..." : "Register"}
                  </Button>
                </form>

                <Card className="mt-6 border-primary/20 bg-primary/5">
                  <CardContent className="pt-4">
                    <p className="text-xs leading-relaxed text-muted-foreground">
                      This form submits to a SQLite database. Check{" "}
                      <code className="text-xs">backend-lib/db.ts</code> and{" "}
                      <code className="text-xs">server.ts</code> to see how it
                      works.
                    </p>
                  </CardContent>
                </Card>
              </CardContent>
            </Card>
          </div>

          <div>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Event Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div>
                  <p className="font-medium">Location</p>
                  <p className="text-muted-foreground">
                    Innovation Hub
                    <br />
                    123 Tech Street, San Francisco
                  </p>
                </div>
                <div>
                  <p className="font-medium">Agenda</p>
                  <ul className="mt-1 space-y-1 text-muted-foreground">
                    <li>6:00 PM - Registration & Networking</li>
                    <li>6:30 PM - Opening Remarks</li>
                    <li>7:00 PM - Tech Talks</li>
                    <li>8:30 PM - Q&A & Social</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </main>
  );
}
