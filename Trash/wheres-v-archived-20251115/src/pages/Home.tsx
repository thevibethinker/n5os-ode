import React, { useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function Home() {
  const isDev = import.meta.env.MODE !== "production";
  useEffect(() => {
    console.log(`Zo site in ${isDev ? "development" : "production"} mode.`);
  }, []);

  return (
    <main className="flex min-h-screen items-center justify-center p-4 md:p-6">
      <div className="w-full max-w-2xl">
        <Card>
          <CardHeader>
            <CardTitle className="text-3xl">My Zo Site</CardTitle>
            <CardDescription>Welcome to your new Zo site</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p>You've just created a new site hosted from your Zo Computer.</p>
            <p>
              Sites can house one or more interactive pages and/or power an API.
            </p>
            <p>
              You can make any number of sites from your Zo computer and
              configure access so that they are either private to you or
              accessible to the public.
            </p>
            <p>
              Sites let you make personal tools, share content based on data on
              your computer, publish writing, make digital art, or even host a
              game. Use your imagination. Zo can help you get started or explore
              possibilities.
            </p>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
