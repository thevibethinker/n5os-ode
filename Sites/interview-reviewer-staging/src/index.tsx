import { Hono } from "hono";
import { html } from "hono/html";
import { randomUUID } from "crypto";

import {
  createSession,
  updateSessionStripe,
  updateSessionReport,
  getSession,
} from "./lib/db";
import { analyzeInterview } from "./lib/openai";
import { checkRateLimit, recordRequest, resetCircuitBreaker, getStatus } from "./lib/ratelimit";
import { storeTranscript, getTranscript, deleteTranscript } from "./lib/session-store";
import { verifyPaymentViaZo } from "./lib/zo-stripe";

const app = new Hono();

const getBaseUrl = () => process.env.BASE_URL || "http://localhost:3000";
const getPaymentLinkUrl = () => process.env.PAYMENT_LINK_URL || "";

// ============ Shared Layout ============
const Layout = ({ title, children }: { title: string; children: any }) => html`
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>${title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
      body { font-family: system-ui, -apple-system, sans-serif; }
    </style>
  </head>
  <body class="bg-gray-50 min-h-screen">
    ${children}
  </body>
</html>
`;

// ============ Landing Page ============
app.get("/", (c) => {
  const paymentLinkUrl = getPaymentLinkUrl();
  
  return c.html(
    <Layout title="Am I Hired? - Interview Feedback">
      {/* Header */}
      <header class="bg-white border-b">
        <div class="max-w-3xl mx-auto px-4 py-4">
          <h1 class="text-xl font-bold text-gray-900">Am I Hired?</h1>
        </div>
      </header>

      <main class="max-w-3xl mx-auto px-4 py-8">
        {/* Hero Section */}
        <section class="text-center mb-12">
          <h2 class="text-3xl font-bold text-gray-900 mb-4">
            Get Expert Feedback on Your Interview
          </h2>
          <p class="text-lg text-gray-600 max-w-xl mx-auto">
            Paste your interview transcript and get actionable feedback from an AI trained on 10+ years of career coaching expertise. $5, one-time.
          </p>
        </section>

        {/* How It Works */}
        <section class="mb-12">
          <h3 class="text-lg font-semibold text-gray-900 mb-4">How It Works</h3>
          <div class="grid md:grid-cols-3 gap-4">
            <div class="bg-white p-4 rounded-lg border">
              <div class="text-2xl mb-2">1</div>
              <div class="font-medium">Paste your transcript</div>
              <div class="text-sm text-gray-500">From Zoom, Teams, Otter, or any recording tool</div>
            </div>
            <div class="bg-white p-4 rounded-lg border">
              <div class="text-2xl mb-2">2</div>
              <div class="font-medium">Pay $5</div>
              <div class="text-sm text-gray-500">Secure checkout via Stripe</div>
            </div>
            <div class="bg-white p-4 rounded-lg border">
              <div class="text-2xl mb-2">3</div>
              <div class="font-medium">Get your feedback</div>
              <div class="text-sm text-gray-500">Detailed analysis in seconds</div>
            </div>
          </div>
        </section>

        {/* Input Form */}
        <section class="bg-white p-6 rounded-lg border mb-8">
          <form action="/submit" method="POST">
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Company Name
              </label>
              <input
                type="text"
                name="company"
                required
                placeholder="e.g., Acme Corp"
                class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Job Description
              </label>
              <textarea
                name="jobDescription"
                required
                rows={4}
                placeholder="Paste the job description or key requirements here..."
                class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              ></textarea>
              <p class="text-xs text-gray-500 mt-1">
                We use this to compare your answers against what the role requires.
              </p>
            </div>
            
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                How do you feel it went?
              </label>
              <textarea
                name="selfAssessment"
                required
                rows={3}
                placeholder="What's your gut feeling? Any specific moments you're worried about? What do you think went well?"
                class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
              ></textarea>
              <p class="text-xs text-gray-500 mt-1">
                We'll compare your perception against the actual transcript to calibrate your self-assessment.
              </p>
            </div>

            <div class="mb-6">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Interview Transcript
              </label>
              <textarea
                name="transcript"
                required
                rows={10}
                placeholder="Paste your interview transcript here..."
                class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              ></textarea>
              <p class="text-xs text-gray-500 mt-1">
                Your transcript is never saved to disk and is deleted immediately after analysis.
              </p>
            </div>
            
            <div class="mb-6">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Promo Code <span class="text-gray-400 font-normal">(optional)</span>
              </label>
              <input
                type="text"
                name="promoCode"
                placeholder="e.g., THANKS-7K2X"
                class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              type="submit"
              class="w-full bg-blue-600 text-white py-3 px-4 rounded-md font-medium hover:bg-blue-700 transition"
            >
              Continue to Payment ($5)
            </button>
          </form>
        </section>

        {/* Privacy Notice */}
        <section class="text-center text-sm text-gray-500">
          <p>
            <strong>Privacy first:</strong> Your transcript is stored in memory only, never written to disk,
            and deleted immediately after generating your feedback.
          </p>
          <p class="mt-2">
            <a href="https://github.com/careerspan/am-i-hired" class="underline" target="_blank">
              View source code
            </a>
            {" "}to verify our privacy claims.
          </p>
        </section>
      </main>

      {/* Footer */}
      <footer class="border-t mt-12 py-6">
        <div class="max-w-3xl mx-auto px-4 text-center text-sm text-gray-500">
          Built by <a href="https://careerspan.io" class="underline">Careerspan</a>
        </div>
      </footer>
    </Layout>
  );
});

// ============ Form Submission → Payment ============
app.post("/submit", async (c) => {
  const body = await c.req.parseBody();
  const transcript = body.transcript as string;
  const company = body.company as string;
  const jobDescription = (body.jobDescription as string)?.trim() || "";
  const selfAssessment = (body.selfAssessment as string)?.trim() || "";
  const promoCode = (body.promoCode as string)?.trim() || undefined;

  if (!transcript || !company || !jobDescription || !selfAssessment) {
    return c.html(
      <Layout title="Error - Am I Hired?">
        <div class="max-w-xl mx-auto px-4 py-16 text-center">
          <h1 class="text-2xl font-bold text-red-600 mb-4">Missing Information</h1>
          <p class="text-gray-600 mb-6">Please fill in all required fields (company, job description, self-assessment, and transcript).</p>
          <a href="/" class="text-blue-600 underline">Go back</a>
        </div>
      </Layout>
    );
  }

  // Rate limit check
  if (!checkRateLimit()) {
    return c.html(
      <Layout title="Rate Limited - Am I Hired?">
        <div class="max-w-xl mx-auto px-4 py-16 text-center">
          <h1 class="text-2xl font-bold text-orange-600 mb-4">Too Many Requests</h1>
          <p class="text-gray-600 mb-6">Please try again in a few minutes.</p>
          <a href="/" class="text-blue-600 underline">Go back</a>
        </div>
      </Layout>
    );
  }

  // Create session
  const sessionId = randomUUID();
  createSession(sessionId, company, selfAssessment);
  
  // Store transcript in memory only (never touches disk)
  storeTranscript(sessionId, transcript, company, jobDescription, selfAssessment);

  const paymentLinkUrl = getPaymentLinkUrl();
  
  if (!paymentLinkUrl) {
    return c.html(
      <Layout title="Setup Required - Am I Hired?">
        <div class="max-w-xl mx-auto px-4 py-16 text-center">
          <h1 class="text-2xl font-bold text-orange-600 mb-4">Payment Not Configured</h1>
          <p class="text-gray-600 mb-6">Payment link is not set up yet.</p>
          <a href="/" class="text-blue-600 underline">Go back</a>
        </div>
      </Layout>
    );
  }

  // Build payment URL with session tracking
  const successUrl = `${getBaseUrl()}/success?session_id=${sessionId}`;
  const paymentUrl = `${paymentLinkUrl}?client_reference_id=${sessionId}`;

  return c.html(
    <Layout title="Confirm Payment - Am I Hired?">
      <header class="bg-white border-b">
        <div class="max-w-3xl mx-auto px-4 py-4">
          <h1 class="text-xl font-bold text-gray-900">Am I Hired?</h1>
        </div>
      </header>

      <main class="max-w-xl mx-auto px-4 py-16 text-center">
        <div class="bg-white p-8 rounded-lg border">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">Ready for Payment</h2>
          
          <div class="text-left bg-gray-50 p-4 rounded mb-6">
            <div class="text-sm text-gray-500">Company</div>
            <div class="font-medium">{company}</div>
            <div class="text-sm text-gray-500 mt-2">Job description</div>
            <div class="font-medium">✓ Provided ({jobDescription.length.toLocaleString()} chars)</div>
            <div class="text-sm text-gray-500 mt-2">Self-assessment</div>
            <div class="font-medium text-sm text-gray-700 italic">"{selfAssessment.slice(0, 100)}{selfAssessment.length > 100 ? '...' : ''}"</div>
            <div class="text-sm text-gray-500 mt-2">Transcript length</div>
            <div class="font-medium">{transcript.length.toLocaleString()} characters</div>
            {promoCode && (
              <>
                <div class="text-sm text-gray-500 mt-2">Promo code</div>
                <div class="font-medium">{promoCode}</div>
              </>
            )}
          </div>

          <a
            href={paymentUrl}
            class="block w-full bg-blue-600 text-white py-3 px-4 rounded-md font-medium hover:bg-blue-700 transition text-center"
          >
            Pay $5 with Stripe
          </a>
          
          <p class="text-xs text-gray-500 mt-4">
            Session: {sessionId.slice(0, 8)}... 
            <br />After payment, you'll be redirected back here for your results.
          </p>
        </div>
      </main>

      <script dangerouslySetInnerHTML={{ __html: `
        localStorage.setItem('amihired_session', '${sessionId}');
      `}} />
    </Layout>
  );
});

// ============ Success / Results Page ============
app.get("/success", async (c) => {
  const sessionId = c.req.query("session_id");
  const checkoutSessionId = c.req.query("checkout_session_id");

  if (!sessionId) {
    return c.html(
      <Layout title="Error - Am I Hired?">
        <div class="max-w-xl mx-auto px-4 py-16 text-center">
          <h1 class="text-2xl font-bold text-red-600 mb-4">Missing Session</h1>
          <p class="text-gray-600 mb-6">No session ID provided.</p>
          <a href="/" class="text-blue-600 underline">Start over</a>
        </div>
      </Layout>
    );
  }

  // Get stored transcript
  const transcriptData = getTranscript(sessionId);
  if (!transcriptData) {
    return c.html(
      <Layout title="Session Expired - Am I Hired?">
        <div class="max-w-xl mx-auto px-4 py-16 text-center">
          <h1 class="text-2xl font-bold text-orange-600 mb-4">Session Expired</h1>
          <p class="text-gray-600 mb-6">Your session has expired. Please submit your transcript again.</p>
          <a href="/" class="text-blue-600 underline">Start over</a>
        </div>
      </Layout>
    );
  }

  // Verify payment via Zo's API
  const paymentVerified = await verifyPaymentViaZo(sessionId);
  
  if (!paymentVerified) {
    return c.html(
      <Layout title="Payment Pending - Am I Hired?">
        <div class="max-w-xl mx-auto px-4 py-16 text-center">
          <h1 class="text-2xl font-bold text-orange-600 mb-4">Payment Not Found</h1>
          <p class="text-gray-600 mb-6">
            We couldn't verify your payment yet. This may take a moment.
          </p>
          <button 
            onclick="location.reload()" 
            class="bg-blue-600 text-white py-2 px-4 rounded-md font-medium hover:bg-blue-700"
          >
            Check Again
          </button>
        </div>
      </Layout>
    );
  }

  // Record the request for rate limiting
  recordRequest();

  // Run the analysis
  const analysis = await analyzeInterview(
    transcriptData.transcript,
    transcriptData.company,
    transcriptData.selfAssessment,
    transcriptData.jobDescription
  );

  // Delete transcript immediately after analysis
  deleteTranscript(sessionId);

  // Update session with results
  if (analysis.success) {
    updateSessionReport(sessionId, analysis.report);
  }

  if (!analysis.success) {
    return c.html(
      <Layout title="Analysis Error - Am I Hired?">
        <div class="max-w-xl mx-auto px-4 py-16 text-center">
          <h1 class="text-2xl font-bold text-red-600 mb-4">Analysis Failed</h1>
          <p class="text-gray-600 mb-6">{analysis.error}</p>
          <p class="text-sm text-gray-500">
            Your payment was processed. Please contact support for a refund.
          </p>
        </div>
      </Layout>
    );
  }

  // Parse the analysis sections
  const report = analysis.report;
  const hadJobDescription = !!transcriptData.jobDescription;

  return c.html(
    <Layout title="Your Feedback - Am I Hired?">
      <header class="bg-white border-b">
        <div class="max-w-3xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 class="text-xl font-bold text-gray-900">Am I Hired?</h1>
          <span class="text-sm text-green-600 font-medium">✓ Analysis Complete</span>
        </div>
      </header>

      <main class="max-w-3xl mx-auto px-4 py-8">
        <div class="mb-6">
          <h2 class="text-2xl font-bold text-gray-900">Your Interview Feedback</h2>
          <p class="text-gray-500">Interview at {transcriptData.company}</p>
          <div class="mt-2">
            {hadJobDescription ? (
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                ✓ Analyzed against job requirements
              </span>
            ) : (
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                ℹ️ Generic analysis (no job description provided)
              </span>
            )}
          </div>
        </div>

        <div class="bg-white rounded-lg border divide-y">
          <div class="p-6 prose max-w-none" dangerouslySetInnerHTML={{ __html: formatReport(report) }} />
        </div>

        <div class="mt-8 text-center">
          <a href="/" class="text-blue-600 underline">Analyze another interview</a>
        </div>
      </main>

      <footer class="border-t mt-12 py-6">
        <div class="max-w-3xl mx-auto px-4 text-center text-sm text-gray-500">
          Built by <a href="https://careerspan.io" class="underline">Careerspan</a>
        </div>
      </footer>
    </Layout>
  );
});

// ============ Mock Results Page (for preview) ============
app.get("/demo", (c) => {
  const mockReport = `## Overall Assessment

Your interview at TechCorp showed strong technical foundations but revealed opportunities to better articulate your impact. You demonstrated solid problem-solving skills, though some answers could have been more structured.

**Verdict: Likely advancing to next round (70% confidence)**

## What Went Well

- **Technical depth**: Your explanation of the system design question showed genuine understanding, not just memorized patterns
- **Authenticity**: When you admitted you hadn't used GraphQL in production, it came across as honest rather than defensive
- **Enthusiasm**: Your energy when discussing the team's product was genuine and noticeable

## Areas to Improve

### 1. Quantify Your Impact
When asked about your previous project, you said "I improved the system significantly." Instead, try: "I reduced API response time from 800ms to 120ms, which increased user retention by 15%."

### 2. Structure Behavioral Answers
Your answer to "Tell me about a conflict" jumped around. Use the STAR format:
- **Situation**: Brief context (1 sentence)
- **Task**: Your specific responsibility
- **Action**: What YOU did (not the team)
- **Result**: Measurable outcome

### 3. Ask Better Questions
"What's the team culture like?" is generic. Try: "I noticed you recently shipped [specific feature]. How did the team approach the technical tradeoffs?"

## Specific Moments to Revisit

| Timestamp | What Happened | Suggested Alternative |
|-----------|---------------|----------------------|
| ~5 min | Interviewer asked about failure, you pivoted to success | Own the failure first, then the learning |
| ~18 min | Long pause after system design question | Buy time with "Let me think through the constraints..." |
| ~25 min | Said "we" repeatedly | Use "I" to clarify your specific contribution |

## Next Steps

1. **Before next round**: Prepare 3 stories with specific metrics
2. **Practice**: Record yourself answering "Tell me about yourself" - aim for 90 seconds
3. **Research**: Look up your interviewers on LinkedIn and find common ground`;

  return c.html(
    <Layout title="Demo Feedback - Am I Hired?">
      <header class="bg-white border-b">
        <div class="max-w-3xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 class="text-xl font-bold text-gray-900">Am I Hired?</h1>
          <span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">Demo</span>
        </div>
      </header>

      <main class="max-w-3xl mx-auto px-4 py-8">
        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <p class="text-sm text-yellow-800">
            <strong>This is a demo page</strong> showing what your feedback will look like. 
            The content below is sample output, not a real analysis.
          </p>
        </div>

        <div class="mb-6">
          <h2 class="text-2xl font-bold text-gray-900">Your Interview Feedback</h2>
          <p class="text-gray-500">Interview at TechCorp (Demo)</p>
        </div>

        <div class="bg-white rounded-lg border">
          <div class="p-6 prose max-w-none" dangerouslySetInnerHTML={{ __html: formatReport(mockReport) }} />
        </div>

        <div class="mt-8 text-center">
          <a href="/" class="bg-blue-600 text-white py-2 px-6 rounded-md font-medium hover:bg-blue-700 transition inline-block">
            Try it with your transcript
          </a>
        </div>
      </main>

      <footer class="border-t mt-12 py-6">
        <div class="max-w-3xl mx-auto px-4 text-center text-sm text-gray-500">
          Built by <a href="https://careerspan.io" class="underline">Careerspan</a>
        </div>
      </footer>
    </Layout>
  );
});

// ============ Helper: Format Markdown-ish Report to HTML ============
function formatReport(report: string): string {
  return report
    // Headers
    .replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold mt-6 mb-2">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="text-xl font-bold mt-8 mb-3 pb-2 border-b">$1</h2>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Lists
    .replace(/^- (.+)$/gm, '<li class="ml-4">$1</li>')
    // Tables (basic)
    .replace(/\|(.+)\|/g, (match) => {
      const cells = match.split('|').filter(c => c.trim());
      if (cells.some(c => c.includes('---'))) return '';
      const isHeader = cells[0]?.includes('Timestamp') || cells[0]?.includes('What');
      const tag = isHeader ? 'th' : 'td';
      const className = isHeader ? 'text-left p-2 bg-gray-50 font-medium' : 'p-2 border-t';
      return `<tr>${cells.map(c => `<${tag} class="${className}">${c.trim()}</${tag}>`).join('')}</tr>`;
    })
    // Wrap tables
    .replace(/(<tr>.*<\/tr>\s*)+/g, '<table class="w-full text-sm my-4 border rounded">$&</table>')
    // Paragraphs
    .replace(/\n\n/g, '</p><p class="my-3">')
    // Wrap in paragraph
    .replace(/^/, '<p class="my-3">')
    .replace(/$/, '</p>')
    // Clean up list items
    .replace(/<p class="my-3">(<li)/g, '<ul class="my-3">$1')
    .replace(/(<\/li>)<\/p>/g, '$1</ul>');
}

// ============ Privacy Policy ============
app.get("/privacy", (c) => {
  return c.html(
    <Layout title="Privacy Policy - Am I Hired?">
      <header class="bg-white border-b">
        <div class="max-w-3xl mx-auto px-4 py-4">
          <a href="/" class="text-xl font-bold text-gray-900">Am I Hired?</a>
        </div>
      </header>

      <main class="max-w-3xl mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold mb-6">Privacy Policy</h1>
        
        <div class="prose max-w-none">
          <p class="text-gray-600 mb-4"><strong>Last updated:</strong> January 2026</p>
          
          <h2 class="text-xl font-semibold mt-8 mb-4">What We Collect</h2>
          <p class="mb-4">When you use Am I Hired?, we collect:</p>
          <ul class="list-disc ml-6 mb-4 space-y-2">
            <li><strong>Company name</strong> — The company you interviewed with</li>
            <li><strong>Sentiment</strong> — How you felt the interview went</li>
            <li><strong>Session metadata</strong> — Anonymous session ID and timestamp</li>
            <li><strong>Report summary</strong> — Key points from your feedback (no transcript)</li>
          </ul>

          <h2 class="text-xl font-semibold mt-8 mb-4">What We DON'T Collect</h2>
          <p class="mb-4 text-green-700 font-medium">Your interview transcript is NEVER stored.</p>
          <ul class="list-disc ml-6 mb-4 space-y-2">
            <li>Transcripts exist only in server memory during processing</li>
            <li>Transcripts are deleted immediately after analysis completes</li>
            <li>Transcripts are never written to disk or any database</li>
            <li>We do not store your email, name, or any personal identifiers</li>
          </ul>

          <h2 class="text-xl font-semibold mt-8 mb-4">Third-Party Services</h2>
          <ul class="list-disc ml-6 mb-4 space-y-2">
            <li><strong>Stripe</strong> — Payment processing. Stripe may collect payment information under their privacy policy.</li>
            <li><strong>OpenAI</strong> — AI analysis. Your transcript is sent to OpenAI's API for processing. OpenAI's data retention policies apply.</li>
          </ul>

          <h2 class="text-xl font-semibold mt-8 mb-4">Open Source</h2>
          <p class="mb-4">
            This application is open source. You can verify our privacy claims by reviewing the code at{" "}
            <a href="https://github.com/careerspan/am-i-hired" class="text-blue-600 underline">github.com/careerspan/am-i-hired</a>.
          </p>

          <h2 class="text-xl font-semibold mt-8 mb-4">Contact</h2>
          <p class="mb-4">
            Questions? Contact us at <a href="mailto:privacy@careerspan.io" class="text-blue-600 underline">privacy@careerspan.io</a>
          </p>
        </div>
      </main>

      <footer class="border-t mt-12 py-6">
        <div class="max-w-3xl mx-auto px-4 text-center text-sm text-gray-500">
          <a href="/" class="underline">Home</a> · <a href="/terms" class="underline">Terms</a>
        </div>
      </footer>
    </Layout>
  );
});

// ============ Terms of Service ============
app.get("/terms", (c) => {
  return c.html(
    <Layout title="Terms of Service - Am I Hired?">
      <header class="bg-white border-b">
        <div class="max-w-3xl mx-auto px-4 py-4">
          <a href="/" class="text-xl font-bold text-gray-900">Am I Hired?</a>
        </div>
      </header>

      <main class="max-w-3xl mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold mb-6">Terms of Service</h1>
        
        <div class="prose max-w-none">
          <p class="text-gray-600 mb-4"><strong>Last updated:</strong> January 2026</p>
          
          <h2 class="text-xl font-semibold mt-8 mb-4">Service Description</h2>
          <p class="mb-4">
            Am I Hired? provides AI-powered feedback on interview transcripts. This is an educational tool 
            designed to help you improve your interview skills. It is not a guarantee of employment outcomes.
          </p>

          <h2 class="text-xl font-semibold mt-8 mb-4">Payment</h2>
          <ul class="list-disc ml-6 mb-4 space-y-2">
            <li>Payment is $5 USD per analysis, charged via Stripe</li>
            <li>Payment is due before analysis is provided</li>
            <li>Refunds may be provided at our discretion if analysis fails</li>
          </ul>

          <h2 class="text-xl font-semibold mt-8 mb-4">Your Responsibilities</h2>
          <ul class="list-disc ml-6 mb-4 space-y-2">
            <li>You must have the right to share any transcript you submit</li>
            <li>Remove personally identifiable information (PII) from transcripts before submission</li>
            <li>Do not submit transcripts containing confidential business information</li>
            <li>Do not abuse the service or attempt to circumvent rate limits</li>
          </ul>

          <h2 class="text-xl font-semibold mt-8 mb-4">Disclaimer</h2>
          <p class="mb-4">
            THE SERVICE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND. The feedback provided is 
            AI-generated and should not be considered professional career advice. We are not responsible 
            for employment decisions or outcomes based on our feedback.
          </p>

          <h2 class="text-xl font-semibold mt-8 mb-4">Limitation of Liability</h2>
          <p class="mb-4">
            Careerspan's total liability for any claims arising from your use of the service is limited 
            to the amount you paid for the service ($5).
          </p>

          <h2 class="text-xl font-semibold mt-8 mb-4">Contact</h2>
          <p class="mb-4">
            Questions? Contact us at <a href="mailto:legal@careerspan.io" class="text-blue-600 underline">legal@careerspan.io</a>
          </p>
        </div>
      </main>

      <footer class="border-t mt-12 py-6">
        <div class="max-w-3xl mx-auto px-4 text-center text-sm text-gray-500">
          <a href="/" class="underline">Home</a> · <a href="/privacy" class="underline">Privacy</a>
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

// ============ Start Server ============
const PORT = parseInt(process.env.PORT || "3000", 10);

export default {
  port: PORT,
  fetch: app.fetch,
};

console.log(`🚀 Am I Hired? running on http://localhost:${PORT}`);






