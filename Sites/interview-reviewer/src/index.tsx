import { Hono } from "hono";
import { html } from "hono/html";

import {
  createSession,
  updateSessionStripe,
  updateSessionReport,
  getSession,
} from "./lib/db";
import { checkRateLimit, recordRequest, resetCircuitBreaker, getStatus } from "./lib/ratelimit";
import { storeTranscript, getTranscript, deleteTranscript } from "./lib/session-store";
import { verifyPaymentViaZo } from "./lib/zo-stripe";
import { runPipeline, generateSessionId } from "./lib/pipeline";
import type { AnalysisReport, AnswerFeedback, PieChartData } from "./lib/types/pipeline";
import { validatePromoCode, redeemPromoCode } from "./lib/promo";
import { createPromoCode, listActivePromoCodes } from "./lib/promo";

const app = new Hono();

// Serve static files from public directory
app.get("/public/*", async (c) => {
  const path = c.req.path.replace("/public/", "");
  const filePath = `${import.meta.dir}/../public/${path}`;
  const file = Bun.file(filePath);
  
  if (await file.exists()) {
    return new Response(file, {
      headers: {
        "Content-Type": file.type,
        "Cache-Control": "public, max-age=31536000",
      },
    });
  }
  return c.notFound();
});

const getBaseUrl = () => process.env.BASE_URL || "http://localhost:3000";
const getPaymentLinkUrl = () => process.env.PAYMENT_LINK_URL || "";
const isMaintenanceMode = () => process.env.MAINTENANCE_MODE === "true";

// Email rate limiter to avoid spam filters
const emailRateLimiter = {
  sent: [] as number[],
  HOURLY_LIMIT: 20,
  DAILY_LIMIT: 100,
  MIN_DELAY_MS: 2000,
  lastSent: 0,
  
  canSend(): boolean {
    const now = Date.now();
    const oneHourAgo = now - 60 * 60 * 1000;
    const oneDayAgo = now - 24 * 60 * 60 * 1000;
    
    // Clean old entries
    this.sent = this.sent.filter(t => t > oneDayAgo);
    
    const hourlyCount = this.sent.filter(t => t > oneHourAgo).length;
    const dailyCount = this.sent.length;
    
    if (hourlyCount >= this.HOURLY_LIMIT) {
      console.log(`[Email Rate Limit] Hourly limit reached (${hourlyCount}/${this.HOURLY_LIMIT})`);
      return false;
    }
    if (dailyCount >= this.DAILY_LIMIT) {
      console.log(`[Email Rate Limit] Daily limit reached (${dailyCount}/${this.DAILY_LIMIT})`);
      return false;
    }
    
    return true;
  },
  
  async waitForDelay(): Promise<void> {
    const now = Date.now();
    const timeSinceLast = now - this.lastSent;
    if (timeSinceLast < this.MIN_DELAY_MS) {
      await new Promise(r => setTimeout(r, this.MIN_DELAY_MS - timeSinceLast));
    }
  },
  
  record(): void {
    this.sent.push(Date.now());
    this.lastSent = Date.now();
  },
  
  getStatus(): { hourly: number; daily: number; canSend: boolean } {
    const now = Date.now();
    const oneHourAgo = now - 60 * 60 * 1000;
    this.sent = this.sent.filter(t => t > now - 24 * 60 * 60 * 1000);
    return {
      hourly: this.sent.filter(t => t > oneHourAgo).length,
      daily: this.sent.length,
      canSend: this.canSend()
    };
  }
};

// Email notification helper (uses Zo API)
async function sendAnalysisEmail(
  email: string, 
  name: string, 
  sessionId: string, 
  verdict: string,
  summary: string
): Promise<boolean> {
  try {
    // Check rate limits
    if (!emailRateLimiter.canSend()) {
      console.log(`[Email] Rate limited, skipping email to ${email}`);
      return false;
    }
    
    // Wait for minimum delay between sends
    await emailRateLimiter.waitForDelay();
    
    const reportUrl = `${getBaseUrl()}/analyze/${sessionId}/results`;
    
    const response = await fetch("https://api.zo.computer/email/send", {
      method: "POST",
      headers: {
        "Authorization": process.env.ZO_CLIENT_IDENTITY_TOKEN || "",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        to: email,
        subject: `Your Interview Analysis is Ready - ${verdict}`,
        markdown_body: `Hi ${name},\n\nYour interview analysis is complete!\n\n## Verdict: ${verdict}\n\n${summary}\n\n---\n\n**[View Your Full Report](${reportUrl})**\n\nThis link will remain active for 90 days.\n\n---\n\nQuestions or feedback? Reply to this email.\n\nBest,\nCareerspan Interview Reviewer`
      })
    });
    
    console.log(`[Email] Sent to ${email}, status: ${response.status}`);
    emailRateLimiter.record();
    return response.ok;
  } catch (e) {
    console.error("[Email] Failed to send:", e);
    return false;
  }
}

// ============ Design System - Modern with distinctive fonts + warm palette ============
const designTokens = {
  fonts: {
    heading: "'Plus Jakarta Sans', 'sans-serif'",
    body: "'Inter', 'sans-serif'",
  },
  colors: {
    // Careerspan Navy Blue palette
    primary: {
      50: '#f0f4f8',
      100: '#d9e2ec',
      200: '#bcccdc',
      300: '#9fb3c8',
      400: '#829ab1',
      500: '#627d98',
      600: '#0a2540',  // Main Careerspan navy
      700: '#081d32',
      800: '#061525',
      900: '#030c15',
    },
    // Warm gold accent for CTAs
    accent: {
      50: '#fffbeb',
      100: '#fef3c7',
      200: '#fde68a',
      300: '#fcd34d',
      400: '#fbbf24',
      500: '#f59e0b',
      600: '#d97706',
      700: '#b45309',
      800: '#92400e',
      900: '#78350f',
    },
    stone: {
      50: '#fafaf9',
      100: '#f5f5f4',
      200: '#e7e5e3',
      300: '#d6d3d1',
      400: '#a8a29e',
      500: '#78716c',
      600: '#57534e',
      700: '#44403c',
      800: '#292524',
      900: '#1c1917',
    },
  },
};

// ============ Shared Layout with Modern Design ============
const Layout = ({ title, children }: { title: string; children: any }) => html`
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>${title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Distinctive Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    
    <script>
      tailwind.config = {
        theme: {
          extend: {
            fontFamily: {
              sans: ['Plus Jakarta Sans', 'sans-serif'],
              mono: ['JetBrains Mono', 'monospace'],
            },
            colors: {
              primary: {
                50: '#f0f4f8',
                100: '#d9e2ec',
                200: '#bcccdc',
                300: '#9fb3c8',
                400: '#829ab1',
                500: '#627d98',
                600: '#0a2540',
                700: '#081d32',
                800: '#061525',
                900: '#030c15',
              },
              accent: {
                400: '#fbbf24',
                500: '#f59e0b',
                600: '#d97706',
              },
              stone: {
                50: '#fafaf9',
                100: '#f5f5f4',
                200: '#e7e5e4',
                300: '#d6d3d1',
                400: '#a8a29e',
                500: '#78716c',
                600: '#57534e',
                700: '#44403c',
                800: '#292524',
                900: '#1c1917',
              }
            },
            animation: {
              'fade-in': 'fadeIn 0.5s ease-out',
              'slide-up': 'slideUp 0.6s ease-out',
              'slide-up-delay-1': 'slideUp 0.6s ease-out 0.1s both',
              'slide-up-delay-2': 'slideUp 0.6s ease-out 0.2s both',
              'slide-up-delay-3': 'slideUp 0.6s ease-out 0.3s both',
            },
            keyframes: {
              fadeIn: {
                '0%': { opacity: '0' },
                '100%': { opacity: '1' },
              },
              slideUp: {
                '0%': { opacity: '0', transform: 'translateY(20px)' },
                '100%': { opacity: '1', transform: 'translateY(0)' },
              },
            },
          },
        },
      }
    </script>
    
    <style>
      body { 
        font-family: 'Plus Jakarta Sans', sans-serif;
        -webkit-font-smoothing: antialiased;
      }
      
      /* Warm gradient background */
      .hero-bg {
        background: linear-gradient(135deg, #fef7f4 0%, #fdeee6 50%, #f5f5f4 100%);
      }
      
      /* Subtle pattern overlay */
      .pattern-overlay {
        background-image: radial-gradient(circle at 1px 1px, rgba(232, 93, 4, 0.03) 1px, transparent 0);
        background-size: 24px 24px;
      }
      
      /* Card hover effects */
      .card-hover {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
      }
      .card-hover:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
      }
      
      /* Focus ring styling */
      .focus-ring:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(232, 93, 4, 0.2);
        border-color: #e85d04;
      }
      
      /* Staggered animation for list items */
      .stagger-item {
        animation: slideUp 0.5s ease-out both;
      }
      .stagger-item:nth-child(1) { animation-delay: 0.1s; }
      .stagger-item:nth-child(2) { animation-delay: 0.2s; }
      .stagger-item:nth-child(3) { animation-delay: 0.3s; }
      .stagger-item:nth-child(4) { animation-delay: 0.4s; }
      .stagger-item:nth-child(5) { animation-delay: 0.5s; }
      
      /* Button shine effect */
      .btn-shine {
        position: relative;
        overflow: hidden;
      }
      .btn-shine::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
      }
      .btn-shine:hover::before {
        left: 100%;
      }
    </style>
  </head>
  <body class="bg-stone-50 min-h-screen">
    ${children}
  </body>
</html>
`;

// ============ Landing Page ============
app.get("/", (c) => {
  const paymentLinkUrl = getPaymentLinkUrl();
  const maintenanceMode = isMaintenanceMode();
  
  return c.html(
    <Layout title="Did I Get It? — Expert Interview Feedback">
      {/* Header */}
      <header class="bg-white/80 backdrop-blur-sm border-b border-stone-200 sticky top-0 z-50">
        <div class="max-w-4xl mx-auto px-6 py-4 flex justify-between items-center">
          <div class="flex items-center gap-2">
            <img src="/public/careerspan-logo.png" alt="Careerspan" class="w-8 h-8 rounded-lg object-cover" />
            <span class="text-lg font-bold text-stone-900">Did I Get It?</span>
          </div>
          <a href="/privacy" class="text-sm text-stone-500 hover:text-stone-700 transition">Privacy</a>
        </div>
      </header>

      {/* Launch Special Banner */}
      <div class="bg-gradient-to-r from-primary-600 to-primary-700 text-white py-2 px-4 text-center text-sm font-medium">
        🚀 <strong>January Launch Special:</strong> Get your analysis for 50% off — limited time only!
      </div>

      <main class="hero-bg pattern-overlay min-h-[calc(100vh-73px)]">
        <div class="max-w-4xl mx-auto px-6 py-12">
          
          {/* Hero Section */}
          <section class="text-center mb-16 animate-fade-in">
            <div class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary-100 text-primary-700 text-sm font-medium mb-6">
              <span class="w-2 h-2 rounded-full bg-primary-500 animate-pulse"></span>
              Powered by 10+ years of career coaching
            </div>
            
            <h1 class="text-4xl md:text-5xl font-extrabold text-stone-900 mb-6 leading-tight">
              Get Expert Feedback on<br />
              <span class="bg-gradient-to-r from-primary-500 to-primary-700 bg-clip-text text-transparent">
                Your Interview Performance
              </span>
            </h1>
            
            <p class="text-lg text-stone-600 max-w-2xl mx-auto leading-relaxed">
              Paste your interview transcript and get actionable feedback from an AI trained on 
              <strong class="text-stone-800">10+ years of career coaching expertise</strong>. 
              <span class="line-through text-stone-400">$20</span> <strong class="text-primary-600">$10</strong> per analysis.
            </p>
          </section>

          {/* Founders Section - moved above How It Works */}
          <section class="mb-12 animate-slide-up">
            <div class="grid md:grid-cols-2 gap-4">
              <div class="flex items-center gap-4 px-6 py-4 rounded-2xl bg-white/60 border border-stone-200">
                <img 
                  src="/public/vrijen-photo.jpg" 
                  alt="Vrijen Attawar" 
                  class="w-12 h-12 rounded-full border-2 border-white shadow-sm"
                />
                <div class="text-left flex-1">
                  <div class="flex items-center gap-2">
                    <span class="font-semibold text-stone-900">Vrijen Attawar</span>
                    <a href="https://www.linkedin.com/in/vrijenattawar/" target="_blank" class="text-stone-400 hover:text-[#0077b5] transition" title="LinkedIn">
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                    </a>
                    <a href="https://x.com/vibethinker" target="_blank" class="text-stone-400 hover:text-stone-900 transition" title="X/Twitter">
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                    </a>
                  </div>
                  <p class="text-xs text-stone-500">Cornell MBA • Ex-McKinsey</p>
                </div>
              </div>
              <div class="flex items-center gap-4 px-6 py-4 rounded-2xl bg-white/60 border border-stone-200">
                <img 
                  src="/public/logan-currie.jpeg" 
                  alt="Logan Currie" 
                  class="w-12 h-12 rounded-full border-2 border-white shadow-sm object-cover"
                />
                <div class="text-left flex-1">
                  <div class="flex items-center gap-2">
                    <span class="font-semibold text-stone-900">Logan Currie</span>
                    <a href="https://www.linkedin.com/in/logan-currie-5744577/" target="_blank" class="text-stone-400 hover:text-[#0077b5] transition" title="LinkedIn">
                      <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                    </a>
                  </div>
                  <p class="text-xs text-stone-500">Ex-Harvard Project on Workforce</p>
                </div>
              </div>
            </div>
          </section>

          {/* How It Works */}
          <section class="mb-12 animate-slide-up">
            <h2 class="text-sm font-semibold text-stone-500 uppercase tracking-wider text-center mb-6">How It Works</h2>
            <div class="grid md:grid-cols-3 gap-4">
              <div class="card-hover bg-white rounded-2xl p-6 border border-stone-200 shadow-sm stagger-item">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center text-primary-600 font-bold text-lg mb-4">1</div>
                <div class="font-semibold text-stone-900 mb-1">Paste your transcript</div>
                <div class="text-sm text-stone-500">From Zoom, Teams, Otter, Fathom, or any recording tool</div>
              </div>
              <div class="card-hover bg-white rounded-2xl p-6 border border-stone-200 shadow-sm stagger-item">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-accent-500/20 to-accent-500/30 flex items-center justify-center text-accent-600 font-bold text-lg mb-4">2</div>
                <div class="font-semibold text-stone-900 mb-1"><span class="line-through text-stone-400 font-normal">$20</span> Pay $10</div>
                <div class="text-sm text-stone-500">Secure checkout via Stripe</div>
              </div>
              <div class="card-hover bg-white rounded-2xl p-6 border border-stone-200 shadow-sm stagger-item">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-stone-100 to-stone-200 flex items-center justify-center text-stone-600 font-bold text-lg mb-4">3</div>
                <div class="font-semibold text-stone-900 mb-1">Get your feedback</div>
                <div class="text-sm text-stone-500 mb-3">Detailed analysis in under 5 minutes</div>
                <a href="/preview-results" class="inline-flex items-center gap-1.5 text-sm text-primary-600 hover:text-primary-700 font-medium transition group">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                  See a sample report
                  <svg class="w-3 h-3 group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
                </a>
              </div>
            </div>
          </section>

          {/* Input Form */}
          <section class="bg-white rounded-3xl p-8 border border-stone-200 shadow-lg animate-slide-up-delay-1">
            <form action="/submit" method="post">
              
              {/* Personal Info Section */}
              <div class="grid md:grid-cols-2 gap-6 mb-8">
                <div>
                  <label class="block text-sm font-semibold text-stone-700 mb-2">
                    Your Name
                  </label>
                  <input
                    type="text"
                    name="customerName"
                    required
                    placeholder="Jane Smith"
                    class="focus-ring w-full px-4 py-3 border border-stone-300 rounded-xl bg-stone-50 transition"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-semibold text-stone-700 mb-2">
                    Your Email
                  </label>
                  <input
                    type="email"
                    name="customerEmail"
                    required
                    placeholder="you@example.com"
                    class="focus-ring w-full px-4 py-3 border border-stone-300 rounded-xl bg-stone-50 transition"
                  />
                  <p class="text-xs text-stone-400 mt-1.5">
                    We'll email you a link to your report when it's ready.
                  </p>
                </div>
              </div>
              
              {/* Interview Context */}
              <div class="space-y-6 mb-8">
                <div>
                  <label class="block text-sm font-semibold text-stone-700 mb-2">
                    Company Name
                  </label>
                  <input
                    type="text"
                    name="company"
                    required
                    placeholder="e.g., Acme Corp"
                    class="focus-ring w-full px-4 py-3 border border-stone-300 rounded-xl bg-stone-50 transition"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-semibold text-stone-700 mb-2">
                    Job Description
                  </label>
                  <textarea
                    name="jobDescription"
                    required
                    rows={4}
                    placeholder="Paste the job description or key requirements here..."
                    class="focus-ring w-full px-4 py-3 border border-stone-300 rounded-xl bg-stone-50 transition text-sm"
                  ></textarea>
                  <p class="text-xs text-stone-400 mt-1.5">
                    We compare your answers against what the role requires.
                  </p>
                </div>
                
                <div>
                  <label class="block text-sm font-semibold text-stone-700 mb-2">
                    How do you feel it went?
                  </label>
                  <textarea
                    name="selfAssessment"
                    required
                    rows={3}
                    placeholder="What's your gut feeling? Any specific moments you're worried about? What do you think went well?"
                    class="focus-ring w-full px-4 py-3 border border-stone-300 rounded-xl bg-stone-50 transition text-sm"
                  ></textarea>
                  <p class="text-xs text-stone-400 mt-1.5">
                    We'll calibrate your self-assessment against the actual transcript.
                  </p>
                </div>
              </div>

              {/* Transcript */}
              <div class="mb-6">
                <label class="block text-sm font-semibold text-stone-700 mb-2">
                  Interview Transcript
                </label>
                <textarea
                  name="transcript"
                  required
                  rows={10}
                  placeholder="Paste your interview transcript here..."
                  class="focus-ring w-full px-4 py-3 border border-stone-300 rounded-xl bg-stone-50 transition font-mono text-sm"
                ></textarea>
                <div class="flex items-center gap-2 mt-2">
                  <svg class="w-4 h-4 text-accent-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  <p class="text-xs text-accent-600 font-medium">
                    Your transcript is never saved and is deleted immediately after analysis.
                  </p>
                </div>
              </div>
              
              {/* Promo Code */}
              <div class="mb-8">
                <label class="block text-sm font-semibold text-stone-700 mb-2">
                  Promo Code <span class="text-stone-400 font-normal">(optional)</span>
                </label>
                <input
                  type="text"
                  name="promoCode"
                  placeholder="e.g., THANKS-7K2X"
                  class="focus-ring w-full md:w-1/2 px-4 py-3 border border-stone-300 rounded-xl bg-stone-50 transition"
                />
              </div>

              {/* Submit Button */}
              {maintenanceMode ? (
                <button
                  type="button"
                  disabled
                  class="w-full bg-stone-300 text-stone-500 py-4 px-6 rounded-xl font-semibold text-lg cursor-not-allowed"
                >
                  Temporarily Offline — Check back soon
                </button>
              ) : (
                <button
                  type="submit"
                  class="btn-shine w-full bg-gradient-to-r from-primary-500 to-primary-600 text-white py-4 px-6 rounded-xl font-semibold text-lg hover:from-primary-600 hover:to-primary-700 transition shadow-lg shadow-primary-500/25"
                >
                  Continue to Payment — $10
                </button>
              )}
              
              <p class="text-center text-xs text-stone-400 mt-4">
                By continuing, you agree to our{" "}
                <a href="/terms" class="underline hover:text-stone-600">Terms</a> and{" "}
                <a href="/privacy" class="underline hover:text-stone-600">Privacy Policy</a>.
              </p>
            </form>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer class="bg-white border-t border-stone-200 py-8">
        <div class="max-w-4xl mx-auto px-6">
          <div class="flex flex-col md:flex-row justify-between items-center gap-4">
            <div class="flex items-center gap-2">
              <img src="/public/careerspan-logo.png" alt="Careerspan" class="w-6 h-6 rounded-md object-cover" />
              <span class="text-sm text-stone-700">Did I Get It?</span>
              <span class="text-stone-300">•</span>
              <span class="text-sm text-stone-500">by <a href="https://careerspan.io" target="_blank" class="hover:text-stone-700">Careerspan</a></span>
            </div>
            <div class="flex items-center gap-6 text-sm text-stone-500">
              <a href="/privacy" class="hover:text-stone-700 transition">Privacy</a>
              <a href="/terms" class="hover:text-stone-700 transition">Terms</a>
              <a href="mailto:feedback@mycareerspan.com" class="hover:text-stone-700 transition">Contact</a>
            </div>
          </div>
        </div>
      </footer>
    </Layout>
  );
});

// ============ Form Submission → Payment ============
app.post("/submit", async (c) => {
  const body = await c.req.parseBody();
  
  const customerName = (body.customerName as string || "").trim();
  const customerEmail = (body.customerEmail as string || "").trim();
  const company = (body.company as string || "").trim();
  const jobDescription = (body.jobDescription as string || "").trim();
  const selfAssessment = (body.selfAssessment as string || "").trim();
  const transcript = (body.transcript as string || "").trim();
  const promoCode = (body.promoCode as string || "").trim();

  // Basic validation
  if (!customerName || !customerEmail || !company || !jobDescription || !selfAssessment || !transcript) {
    return c.html(
      <Layout title="Error - Did I Get It?">
        <main class="max-w-3xl mx-auto px-6 py-16 text-center">
          <div class="w-16 h-16 mx-auto mb-6 rounded-full bg-red-100 flex items-center justify-center">
            <svg class="w-8 h-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-stone-900 mb-4">Missing Information</h1>
          <p class="text-stone-600 mb-8">Please fill in all required fields.</p>
          <a href="/" class="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to form
          </a>
        </main>
      </Layout>
    );
  }

  // Generate session ID
  const sessionId = generateSessionId();

  // Store session in DB (with name/email for remarketing)
  createSession(sessionId, company, selfAssessment, customerName, customerEmail);

  // Store transcript in memory only (with name/email)
  storeTranscript(sessionId, transcript, company, jobDescription, selfAssessment, customerName, customerEmail);

  // Check for promo code
  if (promoCode) {
    const promoValidation = validatePromoCode(promoCode);
    if (promoValidation.valid) {
      // Redeem promo code
      redeemPromoCode(promoCode);
      
      // Skip payment, go directly to analysis
      return c.redirect(`/analyze/${sessionId}`);
    } else {
      // Invalid promo code - show error
      return c.html(
        <Layout title="Invalid Promo Code - Did I Get It?">
          <main class="max-w-3xl mx-auto px-6 py-16 text-center">
            <div class="w-16 h-16 mx-auto mb-6 rounded-full bg-amber-100 flex items-center justify-center">
              <svg class="w-8 h-8 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h1 class="text-2xl font-bold text-stone-900 mb-4">Invalid Promo Code</h1>
            <p class="text-stone-600 mb-2">{promoValidation.reason}</p>
            <p class="text-sm text-stone-500 mb-8">You can continue without a promo code, or go back and try again.</p>
            <div class="flex justify-center gap-4">
              <a href="/" class="px-4 py-2 text-stone-600 hover:text-stone-800 font-medium">
                ← Back to form
              </a>
              <a href={`${getPaymentLinkUrl()}?client_reference_id=${sessionId}`} 
                 class="px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition">
                Continue to Payment
              </a>
            </div>
          </main>
        </Layout>
      );
    }
  }

  // Redirect to Stripe payment
  const paymentUrl = `${getPaymentLinkUrl()}?client_reference_id=${sessionId}`;
  return c.redirect(paymentUrl);
});

// ============ Stripe Webhook / Success ============
app.get("/success", async (c) => {
  const sessionId = c.req.query("session_id");
  
  if (!sessionId) {
    return c.redirect("/");
  }
  
  // Look up our session by Stripe session ID or client_reference_id
  // For payment links, we need to verify via Zo
  const verification = await verifyPaymentViaZo(sessionId);
  
  if (!verification.paid || !verification.order) {
    return c.html(
      <Layout title="Payment Verification - Did I Get It?">
        <main class="max-w-3xl mx-auto px-6 py-16 text-center">
          <div class="w-16 h-16 mx-auto mb-6 rounded-full bg-amber-100 flex items-center justify-center">
            <svg class="w-8 h-8 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-stone-900 mb-4">Verifying Payment...</h1>
          <p class="text-stone-600 mb-8">
            We couldn't verify your payment immediately. If you completed payment, 
            please wait a moment and refresh, or contact support.
          </p>
          <a href="mailto:feedback@mycareerspan.com" class="text-primary-600 hover:text-primary-700 font-medium">
            Contact Support
          </a>
        </main>
      </Layout>
    );
  }
  
  // Extract client_reference_id from the URL params (passed through payment link)
  const ourSessionId = c.req.query("client_reference_id") || sessionId;
  
  // Update session with Stripe ID
  updateSessionStripe(ourSessionId, sessionId);
  
  // Redirect to analysis
  return c.redirect(`/analyze/${ourSessionId}`);
});

// ============ Analysis Page ============
// In-memory store for analysis status
const analysisStatus = new Map<string, { status: 'pending' | 'processing' | 'complete' | 'error', report?: AnalysisReport, error?: string, startedAt: number }>();

// Status endpoint for polling
app.get("/analyze/:sessionId/status", (c) => {
  const sessionId = c.req.param("sessionId");
  const status = analysisStatus.get(sessionId);
  
  if (!status) {
    return c.json({ status: 'not_found' });
  }
  
  return c.json({ 
    status: status.status,
    elapsed: Date.now() - status.startedAt,
    hasReport: !!status.report
  });
});

// Results endpoint (after analysis complete)
app.get("/analyze/:sessionId/results", (c) => {
  const sessionId = c.req.param("sessionId");
  
  // First check in-memory status (for fresh completions)
  const status = analysisStatus.get(sessionId);
  if (status?.status === 'complete' && status.report) {
    const report = status.report;
    analysisStatus.delete(sessionId);
    return c.html(<ResultsPage report={report} />);
  }
  
  // Fall back to database (for returning visitors)
  const session = getSession(sessionId);
  if (session?.report_json) {
    try {
      const report = JSON.parse(session.report_json);
      return c.html(<ResultsPage report={report} />);
    } catch (e) {
      console.error('[Results] Failed to parse stored report:', e);
    }
  }
  
  // No report found - redirect to analyze page
  return c.redirect(`/analyze/${sessionId}`);
});

// Loading page component
function LoadingPage({ sessionId }: { sessionId: string }) {
  return (
    <Layout title="Analyzing Your Interview - Did I Get it?">
      <main class="max-w-2xl mx-auto px-6 py-16 text-center">
        <div class="mb-8">
          <div class="w-20 h-20 mx-auto mb-6 rounded-full bg-primary-100 flex items-center justify-center">
            <svg class="w-10 h-10 text-primary-600 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-stone-900 mb-2">Analyzing Your Interview</h1>
          <p class="text-stone-600">Our AI is reviewing your transcript. This usually takes 2-4 minutes.</p>
        </div>
        
        <div class="bg-white rounded-2xl border border-stone-200 p-6 mb-8">
          <div class="mb-4">
            <div class="h-3 bg-stone-200 rounded-full overflow-hidden">
              <div id="progress-bar" class="h-full bg-primary-600 rounded-full transition-all duration-1000" style="width: 0%"></div>
            </div>
          </div>
          <p id="status-text" class="text-sm text-stone-500">Starting analysis...</p>
        </div>
        
        <div class="text-left bg-stone-50 rounded-xl p-6">
          <h3 class="font-semibold text-stone-900 mb-3">What we're analyzing:</h3>
          <ul class="space-y-2 text-stone-600">
            <li class="flex items-center gap-2">
              <span id="step1" class="w-5 h-5 rounded-full bg-stone-200 flex items-center justify-center text-xs">1</span>
              Extracting questions and answers
            </li>
            <li class="flex items-center gap-2">
              <span id="step2" class="w-5 h-5 rounded-full bg-stone-200 flex items-center justify-center text-xs">2</span>
              Analyzing question difficulty and intent
            </li>
            <li class="flex items-center gap-2">
              <span id="step3" class="w-5 h-5 rounded-full bg-stone-200 flex items-center justify-center text-xs">3</span>
              Evaluating your responses
            </li>
            <li class="flex items-center gap-2">
              <span id="step4" class="w-5 h-5 rounded-full bg-stone-200 flex items-center justify-center text-xs">4</span>
              Identifying gaps and calibration
            </li>
            <li class="flex items-center gap-2">
              <span id="step5" class="w-5 h-5 rounded-full bg-stone-200 flex items-center justify-center text-xs">5</span>
              Generating your personalized report
            </li>
          </ul>
        </div>
        
        <p class="mt-6 text-xs text-stone-400">Session: {sessionId}</p>
      </main>
      
      <script dangerouslySetInnerHTML={{ __html: `
        const sessionId = '${sessionId}';
        const maxTime = 240000; // 4 minutes max
        const startTime = Date.now();
        const statusTexts = [
          'Starting analysis...',
          'Extracting Q&A pairs from transcript...',
          'Analyzing interview questions...',
          'Evaluating your responses...',
          'Checking for gaps and calibration...',
          'Generating your personalized report...',
          'Finalizing analysis...'
        ];
        
        function updateProgress() {
          const elapsed = Date.now() - startTime;
          const progress = Math.min(95, (elapsed / maxTime) * 100);
          document.getElementById('progress-bar').style.width = progress + '%';
          
          // Update status text based on progress
          const textIndex = Math.min(Math.floor(progress / 15), statusTexts.length - 1);
          document.getElementById('status-text').textContent = statusTexts[textIndex];
          
          // Update step indicators
          const stepNum = Math.floor(progress / 18) + 1;
          for (let i = 1; i <= 5; i++) {
            const step = document.getElementById('step' + i);
            if (i < stepNum) {
              step.className = 'w-5 h-5 rounded-full bg-green-500 text-white flex items-center justify-center text-xs';
              step.innerHTML = '✓';
            } else if (i === stepNum) {
              step.className = 'w-5 h-5 rounded-full bg-primary-600 text-white flex items-center justify-center text-xs animate-pulse';
            }
          }
        }
        
        async function checkStatus() {
          try {
            const res = await fetch('/analyze/' + sessionId + '/status');
            const data = await res.json();
            
            if (data.status === 'complete') {
              document.getElementById('progress-bar').style.width = '100%';
              document.getElementById('status-text').textContent = 'Analysis complete! Loading results...';
              setTimeout(() => {
                window.location.href = '/analyze/' + sessionId + '/results';
              }, 500);
              return;
            } else if (data.status === 'error') {
              document.getElementById('status-text').textContent = 'Error occurred. Refreshing...';
              setTimeout(() => window.location.reload(), 2000);
              return;
            }
          } catch (e) {
            console.error('Status check failed:', e);
          }
          
          updateProgress();
          setTimeout(checkStatus, 2000);
        }
        
        checkStatus();
        setInterval(updateProgress, 1000);
      `}} />
    </Layout>
  );
}

app.get("/analyze/:sessionId", async (c) => {
  const sessionId = c.req.param("sessionId");
  
  // Check if analysis is already complete
  const existingStatus = analysisStatus.get(sessionId);
  if (existingStatus?.status === 'complete' && existingStatus.report) {
    return c.redirect(`/analyze/${sessionId}/results`);
  }
  
  // Check if analysis is already in progress
  if (existingStatus?.status === 'processing') {
    return c.html(<LoadingPage sessionId={sessionId} />);
  }
  
  // Get transcript from memory
  const transcriptData = getTranscript(sessionId);
  if (!transcriptData) {
    return c.html(
      <Layout title="Session Expired - Did I Get It?">
        <main class="max-w-3xl mx-auto px-6 py-16 text-center">
          <div class="w-16 h-16 mx-auto mb-6 rounded-full bg-red-100 flex items-center justify-center">
            <svg class="w-8 h-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-stone-900 mb-4">Session Expired</h1>
          <p class="text-stone-600 mb-8">
            Your session has expired. Transcripts are automatically deleted after 30 minutes for privacy. 
            Please start a new analysis.
          </p>
          <a href="/" class="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition">
            Start New Analysis
          </a>
        </main>
      </Layout>
    );
  }
  
  // Check rate limits
  const rateLimitOk = checkRateLimit();
  if (!rateLimitOk) {
    return c.html(
      <Layout title="Service Busy - Did I Get It?">
        <main class="max-w-3xl mx-auto px-6 py-16 text-center">
          <div class="w-16 h-16 mx-auto mb-6 rounded-full bg-amber-100 flex items-center justify-center">
            <svg class="w-8 h-8 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <h1 class="text-2xl font-bold text-stone-900 mb-4">Service Temporarily Busy</h1>
          <p class="text-stone-600 mb-8">
            We're experiencing high demand. Please wait a moment and try again.
          </p>
          <button onclick="window.location.reload()" class="px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition">
            Try Again
          </button>
        </main>
      </Layout>
    );
  }
  
  // Record the request
  recordRequest();
  
  // Mark analysis as processing
  analysisStatus.set(sessionId, { status: 'processing', startedAt: Date.now() });
  
  // Start pipeline in background (don't await)
  console.log(`[Analysis] Starting background pipeline for session ${sessionId}`);
  runPipeline({
    transcript: transcriptData.transcript,
    company: transcriptData.company,
    jobDescription: transcriptData.jobDescription,
    selfAssessment: transcriptData.selfAssessment,
    sessionId,
  }).then(result => {
    // Note: transcript cleanup is handled by the 30-min expiry job in session-store.ts
    // Do NOT delete here - user may refresh or need to re-access
    
    if (!result.success || !result.report) {
      console.error(`[Analysis] Pipeline failed for ${sessionId}:`, result.error);
      analysisStatus.set(sessionId, { 
        status: 'error', 
        error: result.error || 'Unknown error',
        startedAt: analysisStatus.get(sessionId)?.startedAt || Date.now()
      });
      return;
    }
    
    // Store report summary in DB
    updateSessionReport(sessionId, result.report.executiveSummary, JSON.stringify(result.report));
    
    // Send email notification
    const session = getSession(sessionId);
    if (session?.customer_email) {
      sendAnalysisEmail(
        session.customer_email,
        session.customer_name || "there",
        sessionId,
        result.report.verdict,
        result.report.executiveSummary
      ).catch(e => console.error("[Email] Background send failed:", e));
    }
    
    // Mark as complete with report
    console.log(`[Analysis] Pipeline complete for ${sessionId}`);
    analysisStatus.set(sessionId, { 
      status: 'complete', 
      report: result.report,
      startedAt: analysisStatus.get(sessionId)?.startedAt || Date.now()
    });
  }).catch(err => {
    console.error(`[Analysis] Pipeline crashed for ${sessionId}:`, err);
    analysisStatus.set(sessionId, { 
      status: 'error', 
      error: err.message || 'Pipeline crashed',
      startedAt: analysisStatus.get(sessionId)?.startedAt || Date.now()
    });
  });
  
  // Return loading page immediately
  return c.html(<LoadingPage sessionId={sessionId} />);
});

// ============ Results Page Component ============
function ResultsPage({ report }: { report: AnalysisReport }) {
  return (
    <Layout title={`Interview Feedback - ${report.sessionId}`}>
      {/* Header */}
      <header class="bg-white/80 backdrop-blur-sm border-b border-stone-200 sticky top-0 z-50">
        <div class="max-w-4xl mx-auto px-6 py-4 flex justify-between items-center">
          <div class="flex items-center gap-2">
            <img src="/public/careerspan-logo.png" alt="Careerspan" class="w-8 h-8 rounded-lg object-cover" />
            <span class="text-lg font-bold text-stone-900">Did I Get It?</span>
          </div>
          <div class="text-sm text-stone-500">
            Session: <code class="bg-stone-100 px-2 py-0.5 rounded font-mono text-xs">{report.sessionId}</code>
          </div>
        </div>
      </header>

      <main class="max-w-4xl mx-auto px-6 py-8">
        {/* Save Link Notice */}
        <div class="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-6 flex items-start gap-3 animate-fade-in">
          <svg class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
          </svg>
          <div>
            <p class="font-medium text-blue-900">Bookmark this page!</p>
            <p class="text-sm text-blue-700">This link is the only way to access your report. We've also emailed you a copy.</p>
          </div>
        </div>

        {/* Executive Summary */}
        <div class="bg-gradient-to-br from-white to-stone-50 rounded-2xl border border-stone-200 p-8 mb-8 shadow-sm animate-fade-in">
          <div class="flex items-start justify-between mb-6">
            <h1 class="text-2xl font-bold text-stone-900">Your Interview Feedback</h1>
            <VerdictBadge verdict={report.verdict} />
          </div>
          <p class="text-stone-700 leading-relaxed text-lg">{report.executiveSummary}</p>
        </div>

        {/* Two Column Layout */}
        <div class="grid md:grid-cols-2 gap-6 mb-8">
          {/* Question Breakdown */}
          <div class="bg-white rounded-2xl border border-stone-200 p-6 shadow-sm stagger-item">
            <h3 class="font-semibold text-stone-900 mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.04A12.02 12.02 0 003 9c0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Question Types
            </h3>
            <QuestionBreakdownChart data={report.questionBreakdown} />
          </div>

          {/* JD Coverage */}
          <div class="bg-white rounded-2xl border border-stone-200 p-6 shadow-sm stagger-item">
            <h3 class="font-semibold text-stone-900 mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-accent-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Job Requirements Coverage
            </h3>
            <JDCoverageMap coverage={report.jdCoverage} />
          </div>
        </div>

        {/* Calibration Insight */}
        <CalibrationCard calibration={report.calibrationInsight} />

        {/* Top Answer Feedback */}
        <div class="bg-white rounded-2xl border border-stone-200 mb-8 shadow-sm overflow-hidden">
          <div class="p-6 border-b border-stone-100 bg-stone-50">
            <h3 class="font-semibold text-stone-900 mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m-6 9l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Answer-by-Answer Feedback
            </h3>
          </div>
          <div class="divide-y divide-stone-100">
            {report.topAnswerFeedback.map((feedback: AnswerFeedback, idx: number) => (
              <AnswerFeedbackCard key={idx} feedback={feedback} index={idx + 1} />
            ))}
          </div>
        </div>

        {/* Top Improvements */}
        <div class="bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl border border-amber-200 p-6 mb-8">
          <h3 class="font-semibold text-amber-900 mb-4 flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Your Top Priorities
          </h3>
          <ol class="space-y-3">
            {report.topImprovements.map((improvement: string, idx: number) => (
              <li key={idx} class="flex gap-3 text-amber-900">
                <span class="flex-shrink-0 w-6 h-6 rounded-full bg-amber-200 text-amber-800 text-sm font-bold flex items-center justify-center">{idx + 1}</span>
                <span>{improvement}</span>
              </li>
            ))}
          </ol>
        </div>

        {/* Technical Questions Note */}
        {report.technicalQuestionsNote && (
          <div class="bg-stone-100 rounded-xl border border-stone-200 p-4 mb-8 text-sm text-stone-600">
            <strong>Note on Technical Questions:</strong> {report.technicalQuestionsNote}
          </div>
        )}

        {/* Final Verdict */}
        <FinalVerdict verdict={report.verdict} />

        {/* Feedback CTA */}
        <div class="mt-8 text-center bg-gradient-to-br from-primary-50 to-orange-50 rounded-2xl p-8 border border-primary-100">
          <p class="text-stone-700 mb-3 font-medium">Was this feedback helpful?</p>
          <p class="text-sm text-stone-500 mb-6">
            We'd love to hear how it went! Email us at{" "}
            <a href={`mailto:feedback@mycareerspan.com?subject=Interview Reviewer Feedback - ${report.sessionId}`} class="text-primary-600 underline hover:text-primary-700">
              feedback@mycareerspan.com
            </a>
          </p>
          <a href="/" class="inline-flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a2 2 0 002 2h2a2 2 0 002-2m0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            Analyze another interview
          </a>
        </div>
      </main>

      {/* Footer */}
      <footer class="bg-white border-t border-stone-200 py-8 mt-12">
        <div class="max-w-4xl mx-auto px-6 text-center text-sm text-stone-500">
          Built by{" "}
          <a href="https://www.linkedin.com/in/vrijenattawar/" target="_blank" class="hover:text-stone-700">Vrijen Attawar</a>{" "}
          at{" "}
          <a href="https://careerspan.io" target="_blank" class="hover:text-stone-700">
            Careerspan
          </a>
        </div>
      </footer>
    </Layout>
  );
}

// ============ Report Components ============

function VerdictBadge({ verdict }: { verdict: AnalysisReport["verdict"] }) {
  const colors: Record<string, string> = {
    strong: "bg-emerald-100 text-emerald-800 border-emerald-200",
    moderate: "bg-amber-100 text-amber-800 border-amber-200",
    uncertain: "bg-orange-100 text-orange-800 border-orange-200",
    unlikely: "bg-red-100 text-red-800 border-red-200",
  };
  
  return (
    <div class={`rounded-xl border px-4 py-3 text-center ${colors[verdict.hireLikelihood] || colors.uncertain}`}>
      <div class="text-2xl font-bold">{verdict.overallGrade}</div>
      <div class="text-xs uppercase tracking-wide font-medium">{verdict.hireLikelihood}</div>
      <div class="text-xs mt-0.5 opacity-75">{verdict.hireLikelihoodPercent}</div>
    </div>
  );
}

function QuestionBreakdownChart({ data }: { data: PieChartData[] }) {
  const colors: Record<string, { bg: string; text: string }> = {
    behavioral: { bg: "bg-blue-500", text: "text-blue-700" },
    technical: { bg: "bg-purple-500", text: "text-purple-700" },
    situational: { bg: "bg-teal-500", text: "text-teal-700" },
    cultural: { bg: "bg-amber-500", text: "text-amber-700" },
    competency: { bg: "bg-rose-500", text: "text-rose-700" },
    logistical: { bg: "bg-stone-400", text: "text-stone-600" },
  };
  
  const total = data.reduce((sum: number, s: PieChartData) => sum + s.count, 0);
  
  return (
    <div class="space-y-3">
      {data.map((item: PieChartData, idx: number) => {
        const pct = item.percentage || (total > 0 ? Math.round((item.count / total) * 100) : 0);
        const colorSet = colors[item.type] || { bg: "bg-stone-400", text: "text-stone-600" };
        return (
          <div key={idx}>
            <div class="flex justify-between text-sm mb-1">
              <span class={`font-medium ${colorSet.text}`}>{item.type}</span>
              <span class="text-stone-500">{item.count} ({pct}%)</span>
            </div>
            <div class="h-2 bg-stone-100 rounded-full overflow-hidden">
              <div class={`h-full ${colorSet.bg} rounded-full transition-all`} style={`width: ${pct}%`}></div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function JDCoverageMap({ coverage }: { coverage: AnalysisReport["jdCoverage"] }) {
  const allItems = [
    ...coverage.demonstrated.map(r => ({ requirement: r, status: "demonstrated" as const })),
    ...coverage.partiallyCovered.map(r => ({ requirement: r, status: "partially_covered" as const })),
    ...coverage.notAddressed.map(r => ({ requirement: r, status: "not_addressed" as const })),
  ];
  
  const statusStyles = {
    demonstrated: { icon: "✓", bg: "bg-emerald-100", text: "text-emerald-700" },
    partially_covered: { icon: "◐", bg: "bg-amber-100", text: "text-amber-700" },
    not_addressed: { icon: "○", bg: "bg-stone-100", text: "text-stone-500" },
  };
  
  return (
    <div class="space-y-2">
      {allItems.map((item, idx: number) => {
        const style = statusStyles[item.status];
        return (
          <div key={idx} class={`flex items-center gap-2 px-3 py-2 rounded-lg ${style.bg}`}>
            <span class={`text-sm font-medium ${style.text}`}>{style.icon}</span>
            <span class={`text-sm ${style.text}`}>{item.requirement}</span>
          </div>
        );
      })}
    </div>
  );
}

function CalibrationCard({ calibration }: { calibration: AnalysisReport["calibrationInsight"] }) {
  const labels = {
    realistic: { label: "Well Calibrated", bg: "bg-emerald-50", border: "border-emerald-200" },
    optimistic: { label: "Overconfident", bg: "bg-amber-50", border: "border-amber-200" },
    pessimistic: { label: "Underconfident", bg: "bg-blue-50", border: "border-blue-200" },
  };
  
  const style = labels[calibration.delta];
  
  return (
    <div class={`rounded-2xl border p-6 mb-8 ${style.bg} ${style.border}`}>
      <div class="flex items-center gap-2 mb-3">
        <svg class="w-5 h-5 text-stone-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <span class="text-xs font-semibold text-stone-700 uppercase tracking-wide">Self-Assessment Calibration</span>
        <span class="ml-auto px-2 py-0.5 rounded-full text-xs font-medium bg-white border">{calibration.deltaEmoji} {style.label}</span>
      </div>
      <div class="space-y-2 text-stone-700">
        <p><strong>You said:</strong> {calibration.userSaid}</p>
        <p><strong>Analysis found:</strong> {calibration.analysisFound}</p>
      </div>
    </div>
  );
}

function AnswerFeedbackCard({ feedback, index }: { feedback: AnswerFeedback; index: number }) {
  const gradeColors: Record<string, string> = {
    A: "bg-emerald-100 text-emerald-700 border-emerald-200",
    B: "bg-blue-100 text-blue-700 border-blue-200",
    C: "bg-amber-100 text-amber-700 border-amber-200",
    D: "bg-orange-100 text-orange-700 border-orange-200",
    F: "bg-red-100 text-red-700 border-red-200",
    "N/A": "bg-stone-100 text-stone-600 border-stone-200",
  };
  
  const gradeClass = gradeColors[feedback.grade] || "bg-stone-100 text-stone-600 border-stone-200";
  
  return (
    <div class="p-6 hover:bg-stone-50/50 transition-colors">
      {/* Question Header with Grade */}
      <div class="flex items-start gap-5 mb-4">
        <div class={`flex-shrink-0 w-14 h-14 rounded-2xl border-2 ${gradeClass} flex flex-col items-center justify-center`}>
          <span class="font-bold text-2xl leading-none">{feedback.grade}</span>
          <span class="text-[10px] uppercase tracking-wider opacity-75">grade</span>
        </div>
        <div class="flex-1 min-w-0 pt-1">
          <h4 class="font-semibold text-lg text-stone-900 leading-snug">{feedback.questionSummary}</h4>
        </div>
      </div>
      
      {/* Good / Missing - Two Column Layout */}
      {(feedback.whatWasGood.length > 0 || feedback.whatWasMissing.length > 0) && (
        <div class="grid md:grid-cols-2 gap-4 mb-4 ml-[76px]">
          {feedback.whatWasGood.length > 0 && (
            <div class="bg-emerald-50 rounded-xl p-4 border border-emerald-100">
              <div class="flex items-center gap-2 mb-2">
                <svg class="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                <span class="text-xs font-semibold text-emerald-700 uppercase tracking-wide">What was good</span>
              </div>
              <ul class="space-y-1">
                {feedback.whatWasGood.map((item: string, i: number) => (
                  <li key={i} class="text-sm text-emerald-800 flex items-start gap-2">
                    <span class="text-emerald-400 mt-1">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {feedback.whatWasMissing.length > 0 && (
            <div class="bg-amber-50 rounded-xl p-4 border border-amber-100">
              <div class="flex items-center gap-2 mb-2">
                <svg class="w-4 h-4 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <span class="text-xs font-semibold text-amber-700 uppercase tracking-wide">What was missing</span>
              </div>
              <ul class="space-y-1">
                {feedback.whatWasMissing.map((item: string, i: number) => (
                  <li key={i} class="text-sm text-amber-800 flex items-start gap-2">
                    <span class="text-amber-400 mt-1">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      
      {/* How to Improve - Prominent CTA */}
      {feedback.howToImprove && (
        <div class="ml-[76px] bg-gradient-to-r from-primary-50 to-orange-50 rounded-xl p-4 border border-primary-100">
          <div class="flex items-start gap-3">
            <div class="w-8 h-8 rounded-lg bg-primary-100 flex items-center justify-center flex-shrink-0">
              <span class="text-lg">💡</span>
            </div>
            <div>
              <span class="text-xs font-semibold text-primary-700 uppercase tracking-wide block mb-1">How to improve</span>
              <p class="text-sm text-stone-700 leading-relaxed">{feedback.howToImprove}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function FinalVerdict({ verdict }: { verdict: AnalysisReport["verdict"] }) {
  return (
    <div class="bg-gradient-to-br from-stone-900 to-stone-800 rounded-2xl p-8 text-white">
      <div class="flex flex-col md:flex-row md:items-center gap-6">
        <div class="flex-1">
          <h3 class="text-lg font-semibold mb-2 text-stone-200">Final Assessment</h3>
          <p class="text-xl font-medium">{verdict.gradeDescription}</p>
          <div class="mt-2 text-stone-400 text-sm">
            <span class="text-emerald-400">Strength: </span>{verdict.keyStrength}
          </div>
          <div class="text-stone-400 text-sm">
            <span class="text-amber-400">Risk: </span>{verdict.keyRisk}
          </div>
        </div>
        <div class="text-center md:text-right">
          <div class="text-4xl font-bold text-primary-400">{verdict.overallGrade}</div>
          <div class="text-sm text-stone-400 mt-1">{verdict.hireLikelihoodPercent} likelihood</div>
        </div>
      </div>
    </div>
  );
}

// ============ Privacy Policy ============
app.get("/privacy", (c) => {
  return c.html(
    <Layout title="Privacy Policy - Did I Get It?">
      <header class="bg-white/80 backdrop-blur-sm border-b border-stone-200">
        <div class="max-w-3xl mx-auto px-6 py-4">
          <a href="/" class="flex items-center gap-2">
            <img src="/public/careerspan-logo.png" alt="Careerspan" class="w-8 h-8 rounded-lg object-cover" />
            <span class="text-lg font-bold text-stone-900">Did I Get It?</span>
          </a>
        </div>
      </header>

      <main class="max-w-3xl mx-auto px-6 py-12">
        <h1 class="text-3xl font-bold mb-8 text-stone-900">Privacy Policy</h1>
        
        <div class="prose max-w-none">
          <p class="text-stone-500 mb-8"><strong>Last updated:</strong> January 2026</p>
          
          <section class="mb-8">
            <h2 class="text-xl font-semibold mb-4 text-stone-900">What We Collect</h2>
            <ul class="space-y-2 text-stone-600">
              <li><strong>Name and email</strong> — For support and optional follow-up</li>
              <li><strong>Company name</strong> — The company you interviewed with</li>
              <li><strong>Self-assessment</strong> — How you felt the interview went</li>
              <li><strong>Session metadata</strong> — Anonymous session ID and timestamp</li>
              <li><strong>Report summary</strong> — Key points from your feedback (no transcript)</li>
            </ul>
          </section>

          <section class="mb-8 bg-emerald-50 rounded-xl p-6 border border-emerald-200">
            <h2 class="text-xl font-semibold mb-4 text-emerald-900">What We DON'T Store</h2>
            <p class="text-emerald-800 font-medium mb-4">Your interview transcript is NEVER stored.</p>
            <ul class="space-y-2 text-emerald-700">
              <li>• Transcripts exist only in server memory during processing</li>
              <li>• Transcripts are deleted immediately after analysis completes</li>
              <li>• Transcripts are never written to disk or any database</li>
            </ul>
          </section>

          <section class="mb-8">
            <h2 class="text-xl font-semibold mb-4 text-stone-900">Third-Party Services</h2>
            <ul class="space-y-2 text-stone-600">
              <li><strong>Stripe</strong> — Payment processing under their privacy policy</li>
              <li><strong>OpenAI</strong> — AI analysis under their data retention policies</li>
            </ul>
          </section>

          <section class="mb-8">
            <h2 class="text-xl font-semibold mb-4 text-stone-900">Contact</h2>
            <p class="text-stone-600">
              Questions? Contact us at{" "}
              <a href="mailto:feedback@mycareerspan.com" class="text-primary-600 hover:text-primary-700">feedback@mycareerspan.com</a>
            </p>
          </section>
        </div>
      </main>

      <footer class="border-t border-stone-200 py-6 mt-12">
        <div class="max-w-3xl mx-auto px-6 text-center text-sm text-stone-500">
          <a href="/" class="hover:text-stone-700">Home</a> · <a href="/terms" class="hover:text-stone-700">Terms</a>
        </div>
      </footer>
    </Layout>
  );
});

// ============ Terms of Service ============
app.get("/terms", (c) => {
  return c.html(
    <Layout title="Terms of Service - Did I Get It?">
      <header class="bg-white/80 backdrop-blur-sm border-b border-stone-200">
        <div class="max-w-3xl mx-auto px-6 py-4">
          <a href="/" class="flex items-center gap-2">
            <img src="/public/careerspan-logo.png" alt="Careerspan" class="w-8 h-8 rounded-lg object-cover" />
            <span class="text-lg font-bold text-stone-900">Did I Get It?</span>
          </a>
        </div>
      </header>

      <main class="max-w-3xl mx-auto px-6 py-12">
        <h1 class="text-3xl font-bold mb-8 text-stone-900">Terms of Service</h1>
        
        <div class="prose max-w-none">
          <p class="text-stone-500 mb-8"><strong>Last updated:</strong> January 2026</p>
          
          <section class="mb-8">
            <h2 class="text-xl font-semibold mb-4 text-stone-900">Service Description</h2>
            <p class="text-stone-600">
              Interview Reviewer provides AI-powered feedback on interview transcripts. This is an educational tool 
              designed to help you improve your interview skills. It is not a guarantee of employment outcomes.
            </p>
          </section>

          <section class="mb-8">
            <h2 class="text-xl font-semibold mb-4 text-stone-900">Payment</h2>
            <ul class="space-y-2 text-stone-600">
              <li>• Payment is $10 USD per analysis, charged via Stripe (regularly $20)</li>
              <li>• Payment is due before analysis is provided</li>
              <li>• Refunds may be provided at our discretion if analysis fails</li>
            </ul>
          </section>

          <section class="mb-8">
            <h2 class="text-xl font-semibold mb-4 text-stone-900">Your Responsibilities</h2>
            <ul class="space-y-2 text-stone-600">
              <li>• You must have the right to share any transcript you submit</li>
              <li>• Remove personally identifiable information (PII) from transcripts before submission</li>
              <li>• Do not submit transcripts containing confidential business information</li>
            </ul>
          </section>

          <section class="mb-8">
            <h2 class="text-xl font-semibold mb-4 text-stone-900">Contact</h2>
            <p class="text-stone-600">
              Questions? Contact us at{" "}
              <a href="mailto:feedback@mycareerspan.com" class="text-primary-600 hover:text-primary-700">feedback@mycareerspan.com</a>
            </p>
          </section>
        </div>
      </main>

      <footer class="border-t border-stone-200 py-6 mt-12">
        <div class="max-w-3xl mx-auto px-6 text-center text-sm text-stone-500">
          <a href="/" class="hover:text-stone-700">Home</a> · <a href="/privacy" class="hover:text-stone-700">Privacy</a>
        </div>
      </footer>
    </Layout>
  );
});

// ============ Health & Admin Endpoints ============
app.get("/health", (c) => {
  return c.json({
    status: "ok",
    openai: !!process.env.OPENAI_API_KEY,
    paymentLink: !!process.env.PAYMENT_LINK_URL,
    rateLimit: getStatus(),
  });
});

app.post("/admin/reset-circuit", (c) => {
  const adminKey = c.req.header("X-Admin-Key");
  if (!adminKey || adminKey !== process.env.ADMIN_KEY) {
    return c.json({ error: "Unauthorized" }, 401);
  }
  resetCircuitBreaker();
  return c.json({ status: "Circuit breaker reset", rateLimit: getStatus() });
});

// ============ Promo Code Admin Endpoints ============
app.post("/admin/promo/create", async (c) => {
  const adminKey = c.req.header("X-Admin-Key");
  if (!adminKey || adminKey !== process.env.ADMIN_KEY) {
    return c.json({ error: "Unauthorized" }, 401);
  }
  
  const body = await c.req.json().catch(() => ({}));
  const promo = createPromoCode({
    prefix: body.prefix || "THANKS",
    usesTotal: body.uses || 5,
    expiresInDays: body.expiresInDays || 90,
    createdBy: body.createdBy || "admin",
    note: body.note,
  });
  
  return c.json({ success: true, promo });
});

app.get("/admin/promo/list", (c) => {
  const adminKey = c.req.header("X-Admin-Key");
  if (!adminKey || adminKey !== process.env.ADMIN_KEY) {
    return c.json({ error: "Unauthorized" }, 401);
  }
  
  const promos = listActivePromoCodes();
  return c.json({ promos });
});

// ============ Preview Results Page (for testing layout) ============
app.get("/preview-results", (c) => {
  const mockReport: AnalysisReport = {
    sessionId: "preview-demo-123",
    executiveSummary: "You demonstrated strong communication skills and genuine enthusiasm for the role. Your STAR-format answers were well-structured, particularly when discussing your project management experience. However, you missed opportunities to quantify your impact and could have asked more strategic questions about the team's challenges.",
    questionBreakdown: [
      { type: "behavioral", count: 5, percentage: 42 },
      { type: "technical", count: 3, percentage: 25 },
      { type: "situational", count: 2, percentage: 17 },
      { type: "cultural", count: 2, percentage: 16 },
    ],
    jdCoverage: {
      demonstrated: ["Project management", "Cross-functional collaboration", "Stakeholder communication"],
      partiallyCovered: ["Data analysis", "Budget oversight"],
      notAddressed: ["Vendor management", "Risk mitigation frameworks"],
    },
    calibrationInsight: {
      delta: "optimistic",
      deltaEmoji: "📈",
      userSaid: "I think it went really well, I nailed most of the questions.",
      analysisFound: "While your answers were solid, you missed key opportunities to demonstrate depth in technical areas and left some requirements unaddressed.",
    },
    topAnswerFeedback: [
      {
        questionSummary: "Tell me about a time you led a cross-functional project",
        grade: "A",
        whatWasGood: ["Clear STAR structure", "Specific metrics mentioned (15% efficiency gain)", "Showed leadership without being boastful"],
        whatWasMissing: ["Could have mentioned stakeholder management challenges"],
        howToImprove: "Next time, briefly mention how you handled any pushback or competing priorities from different teams.",
      },
      {
        questionSummary: "How do you prioritize when everything is urgent?",
        grade: "B",
        whatWasGood: ["Mentioned using a prioritization framework", "Gave a concrete example"],
        whatWasMissing: ["Didn't explain how you communicate priorities to stakeholders", "No mention of saying 'no' or pushing back"],
        howToImprove: "Add a sentence about how you communicate trade-offs to leadership and manage expectations when deprioritizing.",
      },
      {
        questionSummary: "What's your experience with data analysis tools?",
        grade: "C",
        whatWasGood: ["Mentioned Excel and basic SQL"],
        whatWasMissing: ["No specific examples of insights derived", "Didn't mention visualization tools", "Vague on proficiency level"],
        howToImprove: "Prepare 2-3 specific examples where your data analysis led to a business decision. Mention specific tools and your comfort level with each.",
      },
      {
        questionSummary: "Why are you interested in this role?",
        grade: "B",
        whatWasGood: ["Showed genuine enthusiasm", "Connected your background to the role"],
        whatWasMissing: ["Could have been more specific about the company's mission", "Didn't mention recent company news or initiatives"],
        howToImprove: "Research 1-2 recent company announcements and weave them into your answer to show you've done your homework.",
      },
    ],
    topImprovements: [
      "Quantify your impact with specific numbers in every answer (revenue, time saved, team size, etc.)",
      "Prepare examples that address the 'vendor management' and 'risk mitigation' requirements from the JD",
      "Ask 2-3 strategic questions about team challenges to demonstrate senior-level thinking",
    ],
    technicalQuestionsNote: "The technical questions were relatively surface-level. For a senior role, expect deeper follow-ups on your SQL and data analysis experience in the next round.",
    verdict: {
      overallGrade: "B+",
      hireLikelihood: "moderate",
      hireLikelihoodPercent: "60-70%",
      gradeDescription: "Solid interview with room for improvement. You're likely advancing to the next round, but need to shore up technical depth and JD coverage.",
      keyStrength: "Strong communication and structured thinking",
      keyRisk: "Gaps in technical depth and some JD requirements unaddressed",
    },
  };

  return c.html(<ResultsPage report={mockReport} />);
});

// ============ Start Server ============
const PORT = parseInt(process.env.PORT || "3000", 10);

export default {
  port: PORT,
  fetch: app.fetch,
  idleTimeout: 120, // 2 minutes for long-running analysis
};

console.log(`🚀 Did I Get It? running on http://localhost:${PORT}`);











