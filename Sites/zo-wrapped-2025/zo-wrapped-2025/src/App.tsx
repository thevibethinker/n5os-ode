import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import BlankDemo from "./pages/demos/blank-demo";
import BlogDemo from "./pages/demos/blog-demo";
import EventDemo from "./pages/demos/event-demo";
import SlidesDemo from "./pages/demos/slides-demo";
import DataDemo from "./pages/demos/data-demo";
import MarketingDemo from "./pages/demos/marketing-demo";
import { ThemeProvider } from "@/components/theme-provider";

/**
 * Main SPA application component. Backend router is defined in `../server.ts`.
 *
 * Variant routing: The root route shows a demo component based on the
 * VITE_ZO_SITE_DEMO_VARIANT environment variable set in zosite.json.
 * Individual demos are also accessible at their own routes for development.
 */

const DEMO_COMPONENTS = {
  blank: BlankDemo,
  blog: BlogDemo,
  event: EventDemo,
  slides: SlidesDemo,
  data: DataDemo,
  marketing: MarketingDemo,
} as const;

type Variant = keyof typeof DEMO_COMPONENTS;

export default function App() {
  const variant =
    (import.meta.env.VITE_ZO_SITE_DEMO_VARIANT as Variant) || "blank";
  const DemoComponent = DEMO_COMPONENTS[variant] || BlankDemo;

  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<DemoComponent />} />
          <Route path="/demos/blank" element={<BlankDemo />} />
          <Route path="/demos/blog" element={<BlogDemo />} />
          <Route path="/demos/event" element={<EventDemo />} />
          <Route path="/demos/slides" element={<SlidesDemo />} />
          <Route path="/demos/data" element={<DataDemo />} />
          <Route path="/demos/marketing" element={<MarketingDemo />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
