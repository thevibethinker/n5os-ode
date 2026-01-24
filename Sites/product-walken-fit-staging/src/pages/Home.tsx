import { useState, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import { quotes, getRandomQuoteByLevel, getRandomQuoteByLevelAvoidingImages, type KeanuQuote } from "@/data/quotes";
import { getChapterForQuoteId, getChapterIndexForQuoteId, getTranscendenceLevel } from "@/data/chapters";
import { cn } from "@/lib/utils";

const categoryLabels: Record<KeanuQuote['category'], string> = {
  sales: "Sales",
  marketing: "Marketing", 
  product: "Product",
  growth: "Growth",
  leadership: "Leadership",
  strategy: "Strategy"
};

const QUOTE_TRUNCATE_LENGTH = 240;
const RECENT_IMAGE_HISTORY_SIZE = 3;

function TruncatedQuote({ text, className }: { text: string; className?: string }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const needsTruncation = text.length > QUOTE_TRUNCATE_LENGTH;
  
  const displayText = needsTruncation && !isExpanded 
    ? text.slice(0, QUOTE_TRUNCATE_LENGTH).trim() + "..."
    : text;

  return (
    <div className={className}>
      <p className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-light leading-[1.4] sm:leading-[1.45] md:leading-[1.5] text-stone-100">
        "{displayText}"
      </p>
      {needsTruncation && (
        <button 
          onClick={() => setIsExpanded(!isExpanded)}
          className="mt-2 text-xs font-medium uppercase tracking-widest text-amber-500/60 hover:text-amber-400 transition-colors"
        >
          {isExpanded ? "Show less" : "Read more"}
        </button>
      )}
    </div>
  );
}

export default function Home() {
  const [searchParams] = useSearchParams();
  const isDebug = searchParams.get("debug") === "1";
  
  const [currentQuote, setCurrentQuote] = useState<KeanuQuote>(quotes[0]);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);
  
  // Progression state
  const [quotesSeenAtLevel, setQuotesSeenAtLevel] = useState(0);
  
  // Track recent images to avoid repetition
  const [recentImageNumbers, setRecentImageNumbers] = useState<number[]>([]);

  const chapter = getChapterForQuoteId(currentQuote.id);
  
  // Derive transcendence level from the actual quote
  const transcendenceLevel = getTranscendenceLevel(currentQuote.id);

  // Robust image loading - check if already loaded (cached)
  useEffect(() => {
    const img = imgRef.current;
    if (img && img.complete && img.naturalHeight > 0) {
      setImageLoaded(true);
    }
  }, [chapter.image]);

  const handleImageLoad = () => {
    setImageLoaded(true);
  };

  const handleImageError = () => {
    console.error('Failed to load image:', chapter.image);
    setImageLoaded(true); // Allow UI to continue
  };

  const getNewQuote = () => {
    setIsTransitioning(true);
    setImageLoaded(false);
    
    setTimeout(() => {
      let nextLevel = transcendenceLevel;
      let nextSeenCount = quotesSeenAtLevel + 1;

      // Advance transcendence level after every 3 quotes
      if (nextSeenCount >= 3) {
        if (nextLevel < 4) {
          nextLevel += 1;
          nextSeenCount = 0;
        } else {
          // Loop back to level 1 after completing level 4
          nextLevel = 1;
          nextSeenCount = 0;
        }
      }

      // Get a new quote, avoiding recently shown images
      const newQuote = getRandomQuoteByLevelAvoidingImages(nextLevel, recentImageNumbers);
      const newChapterIndex = getChapterIndexForQuoteId(newQuote.id);
      
      // Update recent images list
      setRecentImageNumbers(prev => {
        const updated = [newChapterIndex, ...prev.filter(n => n !== newChapterIndex)];
        return updated.slice(0, RECENT_IMAGE_HISTORY_SIZE);
      });
      
      setCurrentQuote(newQuote);
      setQuotesSeenAtLevel(nextSeenCount);
      setIsTransitioning(false);
    }, 400);
  };

  const copyLink = async () => {
    const url = `${window.location.origin}/q/${currentQuote.id}`;
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

  useEffect(() => {
    const initial = getRandomQuoteByLevel(1);
    setCurrentQuote(initial);
    // Initialize recent images with the first quote's chapter
    const initialChapter = getChapterIndexForQuoteId(initial.id);
    setRecentImageNumbers([initialChapter]);
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-stone-900 via-stone-800 to-stone-900 text-stone-100 relative overflow-hidden">
      {/* Zen background elements */}
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
            <div className="flex items-center gap-3">
              <span className="text-2xl">🧘</span>
              <div>
                <h1 className="text-xl font-light tracking-wide text-stone-200">
                  Keanu-to-Market
                </h1>
                <p className="text-xs text-stone-500 tracking-widest uppercase">
                  GTM Wisdom • Keanu Vibes
                </p>
              </div>
            </div>
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
                <div 
                  className="absolute inset-0 rounded-3xl blur-2xl scale-110"
                  style={{ background: 'linear-gradient(to top, var(--zen-gold), transparent)', opacity: 0.15 }}
                />
                
                {/* Loading placeholder */}
                <div className={cn(
                  "absolute inset-0 bg-stone-800/30 rounded-3xl flex items-center justify-center transition-opacity duration-500 z-10",
                  imageLoaded && !isTransitioning ? "opacity-0 pointer-events-none" : "opacity-100"
                )}>
                  <span className="text-4xl animate-pulse">🧘</span>
                </div>

                <img
                  ref={imgRef}
                  src={chapter.image}
                  alt="Keanu contemplating GTM wisdom"
                  onLoad={handleImageLoad}
                  onError={handleImageError}
                  className={cn(
                    "relative w-full h-full object-cover rounded-3xl shadow-2xl transition-all duration-700 ease-out",
                    "border border-stone-700/50",
                    isTransitioning ? "opacity-0 scale-95" : "opacity-100 scale-100"
                  )}
                  style={{
                    filter: 'saturate(0.82) sepia(0.12) contrast(1.05) brightness(0.98)'
                  }}
                />
                
                <div 
                  className="absolute inset-0 rounded-3xl pointer-events-none"
                  style={{
                    background: 'linear-gradient(to top, var(--zen-bg) 0%, transparent 40%, transparent 80%, var(--zen-mist) 100%)',
                    opacity: 0.4,
                    mixBlendMode: 'multiply'
                  }}
                />
                <div 
                  className="absolute inset-0 rounded-3xl pointer-events-none"
                  style={{
                    background: 'linear-gradient(135deg, transparent 30%, var(--zen-gold) 100%)',
                    opacity: 0.08
                  }}
                />
              </div>
              
              <p 
                className={cn(
                  "mt-4 text-center text-xs text-stone-500 italic font-light tracking-wide max-w-md mx-auto transition-opacity duration-300 leading-relaxed min-h-[2rem]",
                  isTransitioning ? "opacity-0" : "opacity-100"
                )}
              >
                {chapter.caption}
              </p>
            </div>

            {/* Quote */}
            <div className="order-2 md:order-2 space-y-6 md:space-y-8">
              <div className="flex flex-wrap items-center gap-3">
                <span className="px-3 py-1 text-xs font-medium tracking-wider uppercase bg-stone-800/80 text-stone-400 rounded-full border border-stone-700/50">
                  {categoryLabels[currentQuote.category]}
                </span>

                <div className="flex items-center gap-2 text-[10px] tracking-widest uppercase text-stone-600">
                  <span>Transcendence</span>
                  <div className="flex items-center gap-1">
                    {[1, 2, 3, 4].map((lvl) => (
                      <span 
                        key={lvl}
                        className={cn(
                          "w-1.5 h-1.5 rounded-full transition-all duration-500",
                          lvl <= transcendenceLevel ? "bg-amber-400/60 shadow-[0_0_8px_rgba(251,191,36,0.4)]" : "bg-stone-700/30"
                        )} 
                      />
                    ))}
                  </div>
                </div>
              </div>

              <div className={cn(
                "transition-all duration-300 min-h-[160px]",
                isTransitioning && "opacity-0 translate-y-4"
              )}>
                <TruncatedQuote text={currentQuote.keanuQuote} />
              </div>

              <div 
                className={cn(
                  "border-l-2 border-stone-700 pl-4 space-y-1 transition-all duration-300 delay-100",
                  isTransitioning && "opacity-0"
                )}
              >
                <p className="text-sm text-stone-500 italic">
                  Inspired by: "{currentQuote.originalQuote}"
                </p>
                <p className="text-xs text-stone-600">
                  — {currentQuote.authorUrl ? (
                    <a 
                      href={currentQuote.authorUrl} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="hover:text-amber-400/80 transition-colors underline decoration-stone-800 underline-offset-4"
                    >
                      {currentQuote.originalAuthor}
                    </a>
                  ) : currentQuote.originalAuthor}
                  {currentQuote.source && <span className="text-stone-700"> • {currentQuote.source}</span>}
                </p>
              </div>

              <div className="flex flex-col gap-4 mt-2">
                <div className="flex flex-wrap items-center gap-3">
                  <button
                    onClick={getNewQuote}
                    className={cn(
                      "group flex items-center gap-3 px-6 py-3",
                      "bg-stone-800/50 hover:bg-stone-700/50",
                      "border border-stone-700/50 hover:border-stone-600/50",
                      "rounded-full transition-all duration-300",
                      "text-stone-400 hover:text-stone-200 shadow-lg active:scale-95"
                    )}
                  >
                    <span className="text-sm tracking-wide">Another dose of wisdom</span>
                    <span className="group-hover:rotate-180 transition-transform duration-500">✨</span>
                  </button>

                  <button
                    onClick={copyLink}
                    className={cn(
                      "flex items-center gap-2 px-4 py-3",
                      "bg-stone-800/30 hover:bg-stone-700/40",
                      "border border-stone-700/30 hover:border-stone-600/40",
                      "rounded-full transition-all duration-300",
                      "text-stone-500 hover:text-stone-300 shadow-sm active:scale-95",
                      copySuccess && "border-amber-600/50 text-amber-400"
                    )}
                  >
                    <span className="text-sm">{copySuccess ? "Copied!" : "Copy link"}</span>
                    <span>{copySuccess ? "✓" : "🔗"}</span>
                  </button>
                </div>
                
                <p className="text-[10px] text-stone-700 tracking-widest uppercase italic">
                  Read each quote to move Keanu closer to product‑market fit
                </p>
              </div>
            </div>
          </div>
        </div>

        {isDebug && (
          <div className="fixed bottom-4 right-4 bg-stone-950/95 border border-stone-700 rounded-lg p-4 text-xs font-mono text-stone-400 max-w-xs shadow-xl z-50">
            <div className="text-stone-500 uppercase tracking-wider mb-2">Debug</div>
            <div className="space-y-1">
              <div><span className="text-stone-600">quoteId:</span> {currentQuote.id}</div>
              <div><span className="text-stone-600">transcendence:</span> {transcendenceLevel}/4</div>
              <div><span className="text-stone-600">quotesAtLvl:</span> {quotesSeenAtLevel}</div>
              <div><span className="text-stone-600">chapter:</span> {chapter.chapter}</div>
              <div><span className="text-stone-600">image:</span> {chapter.image}</div>
              <div><span className="text-stone-600">recentImgs:</span> [{recentImageNumbers.join(', ')}]</div>
              <div><span className="text-stone-600">permalink:</span> /q/{currentQuote.id}</div>
            </div>
          </div>
        )}

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
