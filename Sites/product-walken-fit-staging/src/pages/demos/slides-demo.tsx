import { useEffect, useState } from "react";
import {
  IconPresentation,
  IconArrowRight,
  IconArrowLeft,
  IconArrowDown,
} from "@tabler/icons-react";

/**
 * Presentation demo - interactive slide deck template.
 *
 * This is a simple CSS-based slide viewer with keyboard navigation.
 * When the user asks to customize this:
 * - Replace demo content with their slides
 * - Adjust colors and theme to match their brand
 * - Add animations and transitions
 * - Integrate Reveal.js for advanced features (markdown slides, speaker notes, PDF export)
 * - Load slides from markdown files or a CMS
 */

export default function SlidesDemo() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const totalSlides = 5;

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowRight" || e.key === " ") {
        setCurrentSlide((prev) => {
          const next = Math.min(prev + 1, totalSlides - 1);
          window.location.hash = `slide-${next}`;
          return next;
        });
      } else if (e.key === "ArrowLeft") {
        setCurrentSlide((prev) => {
          const next = Math.max(prev - 1, 0);
          window.location.hash = `slide-${next}`;
          return next;
        });
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [totalSlides]);

  return (
    <div className="reveal-wrapper min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Slide 0: Title */}
      <section
        id="slide-0"
        className="flex min-h-screen items-center justify-center p-8 text-center"
      >
        <div className="max-w-4xl">
          <div className="mb-8 inline-flex h-20 w-20 items-center justify-center rounded-full bg-blue-500/20">
            <IconPresentation className="h-10 w-10 text-blue-400" />
          </div>
          <h1 className="mb-6 text-6xl font-bold text-white md:text-7xl">
            Presentations on Zo
          </h1>
          <p className="mb-8 text-xl text-slate-300">
            Build interactive slide decks powered by your own server
          </p>
          <div className="flex items-center justify-center gap-4 text-sm text-slate-400">
            <IconArrowRight className="h-5 w-5" />
            <span>Use arrow keys or click to navigate</span>
          </div>
        </div>
      </section>

      {/* Slide 1: What You Can Build */}
      <section
        id="slide-1"
        className="flex min-h-screen items-center justify-center p-8"
      >
        <div className="max-w-5xl">
          <h2 className="mb-12 text-center text-5xl font-bold text-white">
            What You Can Build
          </h2>
          <div className="grid gap-6 md:grid-cols-3">
            <div className="rounded-lg bg-slate-800/50 p-6 backdrop-blur">
              <h3 className="mb-3 text-2xl font-semibold text-blue-400">
                Tech Talks
              </h3>
              <p className="text-slate-300">
                Present code, demos, and technical concepts with syntax
                highlighting
              </p>
            </div>
            <div className="rounded-lg bg-slate-800/50 p-6 backdrop-blur">
              <h3 className="mb-3 text-2xl font-semibold text-purple-400">
                Business Pitches
              </h3>
              <p className="text-slate-300">
                Professional presentations with charts, data, and media
              </p>
            </div>
            <div className="rounded-lg bg-slate-800/50 p-6 backdrop-blur">
              <h3 className="mb-3 text-2xl font-semibold text-green-400">
                Workshops
              </h3>
              <p className="text-slate-300">
                Interactive training materials with exercises and resources
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Slide 2: Code Example */}
      <section
        id="slide-2"
        className="flex min-h-screen items-center justify-center p-8"
      >
        <div className="max-w-4xl">
          <h2 className="mb-8 text-center text-5xl font-bold text-white">
            Show Code
          </h2>
          <div className="rounded-lg bg-slate-950 p-6 font-mono text-sm">
            <div className="mb-2 text-slate-500">// Example: Fetch data</div>
            <div className="text-blue-400">
              <span className="text-purple-400">async function</span>{" "}
              <span className="text-yellow-400">fetchData</span>
              <span className="text-slate-300">() {"{"}</span>
            </div>
            <div className="ml-4 text-slate-300">
              <span className="text-purple-400">const</span> response{" "}
              <span className="text-purple-400">=</span>{" "}
              <span className="text-purple-400">await</span>{" "}
              <span className="text-yellow-400">fetch</span>
              <span className="text-slate-400">(</span>
              <span className="text-green-400">'/api/data'</span>
              <span className="text-slate-400">)</span>;
            </div>
            <div className="ml-4 text-slate-300">
              <span className="text-purple-400">return</span>{" "}
              <span className="text-purple-400">await</span> response.
              <span className="text-yellow-400">json</span>
              <span className="text-slate-400">()</span>;
            </div>
            <div className="text-slate-300">{"}"}</div>
          </div>
          <p className="mt-6 text-center text-slate-400">
            Install Reveal.js for automatic syntax highlighting
          </p>
        </div>
      </section>

      {/* Slide 3: Features */}
      <section
        id="slide-3"
        className="flex min-h-screen items-center justify-center p-8"
      >
        <div className="max-w-4xl">
          <h2 className="mb-12 text-center text-5xl font-bold text-white">
            Reveal.js Features
          </h2>
          <div className="space-y-6 text-slate-300">
            <div className="flex items-start gap-4">
              <div className="mt-1 h-3 w-3 shrink-0 rounded-full bg-blue-500" />
              <div>
                <h3 className="mb-1 text-xl font-semibold text-white">
                  Keyboard Navigation
                </h3>
                <p>Arrow keys, space bar, and more for easy control</p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="mt-1 h-3 w-3 shrink-0 rounded-full bg-purple-500" />
              <div>
                <h3 className="mb-1 text-xl font-semibold text-white">
                  Markdown Support
                </h3>
                <p>Write slides in markdown for quick authoring</p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="mt-1 h-3 w-3 shrink-0 rounded-full bg-green-500" />
              <div>
                <h3 className="mb-1 text-xl font-semibold text-white">
                  Speaker Notes
                </h3>
                <p>Private notes visible only to the presenter</p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="mt-1 h-3 w-3 shrink-0 rounded-full bg-yellow-500" />
              <div>
                <h3 className="mb-1 text-xl font-semibold text-white">
                  PDF Export
                </h3>
                <p>Export your presentation to PDF for sharing</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Slide 4: Get Started */}
      <section
        id="slide-4"
        className="flex min-h-screen items-center justify-center p-8 text-center"
      >
        <div className="max-w-4xl">
          <h2 className="mb-8 text-5xl font-bold text-white">
            Ready to Build?
          </h2>
          <p className="mb-12 text-xl text-slate-300">
            Ask Zo to help update the content and theme to match what you want
          </p>
          <div className="rounded-lg bg-slate-800/50 p-8 backdrop-blur">
            <p className="mb-6 text-slate-300">
              This is a demo presentation template. Tell Zo what you'd like to
              present and it will help you customize the slides, colors, and
              content.
            </p>
            <div className="space-y-2 text-left text-sm text-slate-400">
              <div>✓ Keyboard navigation works (arrow keys)</div>
              <div>✓ Fully responsive design</div>
              <div>✓ Easy to customize and extend</div>
            </div>
          </div>
          <div className="mt-8 text-sm text-slate-400">
            This is a demo component - replace it with your own content
          </div>
        </div>
      </section>

      {/* Navigation hint */}
      <div className="fixed bottom-8 right-8 flex gap-2 rounded-lg bg-slate-800/80 p-3 text-xs text-slate-400 backdrop-blur">
        <IconArrowLeft className="h-4 w-4" />
        <IconArrowRight className="h-4 w-4" />
        <span>Navigate</span>
      </div>
    </div>
  );
}
