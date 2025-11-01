import React, { useEffect } from "react";

export default function Home() {
  const isDev = import.meta.env.MODE !== "production";
  useEffect(() => {
    console.log(`Zo site in ${isDev ? "development" : "production"} mode.`);
  }, []);

  return (
    <main className="wrap">
      <section className="card">
        <h1>My Zo Site</h1>
        <p>You've just created a new site hosted from your Zo Computer.</p>
        <p>
          Sites can house one or more interactive pages and/or power an API.
        </p>
        <p>
          You can make any number of sites from your Zo computer and configure
          access so that they are either private to you or accessible to the
          public.
        </p>
        <p>
          Sites let you make personal tools, share content based on data on your
          computer, publish writing, make digital art, or even host a game. Use
          your imagination. Zo can help you get started or explore
          possibilities.
        </p>
      </section>
    </main>
  );
}
