import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getQuoteById, type KeanuQuote } from "@/data/quotes";
import { getChapterForQuoteId } from "@/data/chapters";
import { cn } from "@/lib/utils";
import { useSearchParams } from "react-router-dom";

const categoryLabels: Record<KeanuQuote['category'], string> = {
  sales: "Sales",
  marketing: "Marketing", 
  product: "Product",
  growth: "Growth",
  leadership: "Leadership",
  strategy: "Strategy"
};

export default function QuotePage() {
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams();
  const isDebug = searchParams.get("debug") === "1";
  const [copySuccess, setCopySuccess] = useState(false);

  const quoteId = parseInt(id || "0", 10);
  const quote = getQuoteById(quoteId);

  if (!quote) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-stone-900 via-stone-800 to-stone-900 text-stone-100 flex flex-col items-center justify-center px-6">
        <div className="text-center space-y-6">
          <span className="text-6xl">🧘</span>
          <h1 className="text-2xl font-light text-stone-300">Quote not found</h1>
          <p className="text-stone-500 max-w-md">
            This wisdom has transcended beyond our reach. Perhaps another path awaits.
          </p>
          <Link 
            to="/"
            className={cn(
              "inline-flex items-center gap-2 px-6 py-3",
              "bg-stone-800/50 hover:bg-stone-700/50",
              "border border-stone-700/50 hover:border-stone-600/50",
              "rounded-full transition-all duration-300",
              "text-stone-400 hover:text-stone-200"
            )}
          >
            <span>Return to wisdom</span>
            <span>✨</span>
          </Link>
        </div>
      </main>
    );
  }

  const chapter = getChapterForQuoteId(quote.id);

  const copyLink = async () => {
    const url = window.location.href;
    try {
      await navigator.clipboard.writeText(url);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch {
      const input = document.createElement("input");
      input.value = url;
      document.body.appendChild(input);
      input.select();
      document.execCommand("copy");
      document.body.removeChild(input);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-stone-900 via-stone-800 to-stone-900 text-stone-100 relative overflow-hidden">
      {/* Zen background elements - using zen palette */}
      <div className="absolute inset-0 opacity-5">
        <div 
          className="absolute top-20 left-20 w-96 h-96 rounded-full blur-3xl"
          style={{ backgroundColor: 'var(--zen-gold)', opacity: 0.25 }}
        />
        <div 
          className="absolute bottom-20 right-20 w-80 h-80 rounded-full blur-3xl"
          style={{ backgroundColor: 'var(--zen-sage)', opacity: 0.2 }}
        />
        <div 
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full blur-3xl"
          style={{ backgroundColor: 'var(--zen-mist)', opacity: 0.1 }}
        />
      </div>

      {/* Subtle grid pattern */}
      <div 
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
          backgroundSize: '50px 50px'
        }}
      />

      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Header */}
        <header className="px-6 py-6 md:px-12">
          <div className="flex items-center justify-between max-w-7xl mx-auto">
            <Link to="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
              <span className="text-2xl">🧘</span>
              <div>
                <h1 className="text-xl font-light tracking-wide text-stone-200">
                  Keanu-to-Market
                </h1>
                <p className="text-xs text-stone-500 tracking-widest uppercase">
                  GTM Wisdom • Keanu Vibes
                </p>
              </div>
            </Link>
            <div className="text-right text-xs text-stone-500">
              <p>A gift for</p>
              <p className="text-stone-400 font-medium">Andy Mowat</p>
            </div>
          </div>
        </header>

        {/* Main content */}
        <div className="flex-1 flex items-center justify-center px-6 py-10 md:py-12">
          <div className="max-w-6xl w-full grid md:grid-cols-2 gap-8 md:gap-12 items-center">
            
            {/* Keanu Image + Caption */}
            <div className="relative order-1 md:order-1">
              <div className="relative aspect-[3/4] max-w-md mx-auto">
                {/* Glow effect behind image - zen gold */}
                <div 
                  className="absolute inset-0 rounded-3xl blur-2xl scale-110"
                  style={{ background: 'linear-gradient(to top, var(--zen-gold), transparent)', opacity: 0.15 }}
                />
                
                <img
                  src={chapter.image}
                  alt="Keanu contemplating GTM wisdom"
                  className={cn(
                    "relative w-full h-full object-cover rounded-3xl shadow-2xl",
                    "border border-stone-700/50"
                  )}
                  style={{
                    filter: 'saturate(0.82) sepia(0.12) contrast(1.05) brightness(0.98)'
                  }}
                />
                
                {/* Zen palette overlay - subtle warmth + cohesion */}
                <div 
                  className="absolute inset-0 rounded-3xl pointer-events-none"
                  style={{
                    background: 'linear-gradient(to top, var(--zen-bg) 0%, transparent 40%, transparent 80%, var(--zen-mist) 100%)',
                    opacity: 0.4,
                    mixBlendMode: 'multiply'
                  }}
                />
                {/* Secondary overlay for palette tint */}
                <div 
                  className="absolute inset-0 rounded-3xl pointer-events-none"
                  style={{
                    background: 'linear-gradient(135deg, transparent 30%, var(--zen-gold) 100%)',
                    opacity: 0.08
                  }}
                />
              </div>
              
              {/* Caption below image */}
              <p className="mt-4 text-center text-xs text-stone-500 italic font-light tracking-wide max-w-md mx-auto leading-relaxed">
                {chapter.caption}
              </p>
            </div>

            {/* Quote */}
            <div className="order-2 md:order-2 space-y-6 md:space-y-8">
              {/* Category badge */}
              <div className="flex flex-wrap items-center gap-3">
                <span className="px-3 py-1 text-xs font-medium tracking-wider uppercase bg-stone-800/80 text-stone-400 rounded-full border border-stone-700/50">
                  {categoryLabels[quote.category]}
                </span>

                <div className="flex items-center gap-2 text-[10px] tracking-widest uppercase text-stone-600">
                  <span>Transcendence</span>
                  <div className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400/60" />
                    <span className="w-1.5 h-1.5 rounded-full bg-stone-700/70" />
                    <span className="w-1.5 h-1.5 rounded-full bg-stone-700/50" />
                    <span className="w-1.5 h-1.5 rounded-full bg-stone-700/30" />
                  </div>
                </div>
              </div>

              {/* Keanu quote */}
              <blockquote>
                <p className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-light leading-[1.4] sm:leading-[1.45] md:leading-[1.5] text-stone-100">
                  "{quote.keanuQuote}"
                </p>
              </blockquote>

              {/* Original source */}
              <div className="border-l-2 border-stone-700 pl-4 space-y-1">
                <p className="text-sm text-stone-500 italic">
                  Inspired by: "{quote.originalQuote}"
                </p>
                <p className="text-xs text-stone-600">
                  — {quote.originalAuthor}
                  {quote.source && <span className="text-stone-700"> • {quote.source}</span>}
                </p>
              </div>

              {/* Action buttons */}
              <div className="flex flex-wrap items-center gap-3 mt-2">
                <Link
                  to="/"
                  className={cn(
                    "group flex items-center gap-3 px-6 py-3",
                    "bg-stone-800/50 hover:bg-stone-700/50",
                    "border border-stone-700/50 hover:border-stone-600/50",
                    "rounded-full transition-all duration-300",
                    "text-stone-400 hover:text-stone-200"
                  )}
                >
                  <span className="text-sm tracking-wide">More wisdom</span>
                  <span className="group-hover:rotate-180 transition-transform duration-500">✨</span>
                </Link>

                <button
                  onClick={copyLink}
                  className={cn(
                    "flex items-center gap-2 px-4 py-3",
                    "bg-stone-800/30 hover:bg-stone-700/40",
                    "border border-stone-700/30 hover:border-stone-600/40",
                    "rounded-full transition-all duration-300",
                    "text-stone-500 hover:text-stone-300",
                    copySuccess && "border-amber-600/50 text-amber-400"
                  )}
                >
                  <span className="text-sm">{copySuccess ? "Copied!" : "Copy link"}</span>
                  <span>{copySuccess ? "✓" : "🔗"}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Debug panel */}
        {isDebug && (
          <div className="fixed bottom-4 right-4 bg-stone-950/95 border border-stone-700 rounded-lg p-4 text-xs font-mono text-stone-400 max-w-xs shadow-xl">
            <div className="text-stone-500 uppercase tracking-wider mb-2">Debug</div>
            <div className="space-y-1">
              <div><span className="text-stone-600">quoteId:</span> {quote.id}</div>
              <div><span className="text-stone-600">chapterIndex:</span> {chapter.chapter}</div>
              <div><span className="text-stone-600">image:</span> {chapter.image}</div>
              <div><span className="text-stone-600">permalink:</span> /q/{quote.id}</div>
              <div><span className="text-stone-600">originalAuthor:</span> {quote.originalAuthor}</div>
              <div><span className="text-stone-600">verification:</span> {quote.verification}</div>
            </div>
          </div>
        )}

        {/* Footer */}
        <footer className="px-6 py-6 md:px-12">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-stone-600">
            <p>
              "Be excellent to each other" — not just movie wisdom, but GTM wisdom too.
            </p>
            <p className="text-stone-700">
              Made with 🖤 on Zo Computer
            </p>
          </div>
        </footer>
      </div>
    </main>
  );
}
