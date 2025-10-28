import { Hono } from 'hono';

const app = new Hono();

app.get('/', (c) => {
  return c.html(`<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>N5 OS Launch Waitlist</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  
  <!-- LaunchList Widget Script - ADD YOUR SCRIPT HERE -->
  <script src="https://getlaunchlist.com/js/widget.js" defer></script>
  
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      line-height: 1.6;
      color: #1a1a1a;
      background: #f5f5f5;
    }
    
    :root {
      --n5-rust: #7a2f1f;
      --n5-rust-light: #8b3a26;
      --n5-rust-dark: #5a1f11;
      --n5-gold: #d4a574;
      --n5-gold-bright: #e8b87e;
      --n5-cream: #f5ebe0;
      --n5-dark: #2a1810;
    }
    
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 24px;
    }
    
    .hero {
      background: linear-gradient(135deg, var(--n5-rust) 0%, var(--n5-rust-dark) 100%);
      color: white;
      padding: 80px 0 120px;
      position: relative;
      overflow: hidden;
    }
    
    .hero::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: 
        radial-gradient(circle at 20% 50%, rgba(212, 165, 116, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(212, 165, 116, 0.15) 0%, transparent 50%);
      pointer-events: none;
    }
    
    .hero-content {
      position: relative;
      z-index: 1;
      text-align: center;
    }
    
    .logo {
      width: 180px;
      height: 180px;
      margin: 0 auto 32px;
      border-radius: 20px;
      overflow: hidden;
      box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    .logo img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    h1 {
      font-size: 3.5rem;
      font-weight: 800;
      margin-bottom: 24px;
      line-height: 1.1;
      color: var(--n5-gold-bright);
    }
    
    .subtitle {
      font-size: 1.5rem;
      font-weight: 300;
      margin-bottom: 16px;
      color: var(--n5-cream);
    }
    
    .hero-description {
      font-size: 1.15rem;
      max-width: 800px;
      margin: 0 auto 48px;
      line-height: 1.8;
      color: rgba(255, 255, 255, 0.9);
    }
    
    .cta-section {
      background: white;
      padding: 80px 0;
      margin-top: -60px;
      position: relative;
      z-index: 2;
    }
    
    .waitlist-card {
      max-width: 600px;
      margin: 0 auto;
      background: white;
      padding: 48px;
      border-radius: 20px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.12);
      border: 2px solid var(--n5-gold);
    }
    
    .waitlist-card h2 {
      font-size: 2rem;
      font-weight: 700;
      margin-bottom: 16px;
      color: var(--n5-rust);
      text-align: center;
    }
    
    .waitlist-card p {
      text-align: center;
      margin-bottom: 32px;
      color: #666;
      font-size: 1.1rem;
    }
    
    /* LaunchList Widget Container */
    .launchlist-widget {
      margin-bottom: 24px;
    }
    
    .widget-placeholder {
      background: var(--n5-cream);
      border: 2px dashed var(--n5-gold);
      border-radius: 12px;
      padding: 48px 24px;
      text-align: center;
      color: var(--n5-rust);
    }
    
    .widget-placeholder h3 {
      margin-bottom: 12px;
      font-size: 1.2rem;
    }
    
    .widget-placeholder code {
      background: white;
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 0.9rem;
      color: var(--n5-rust-dark);
    }
    
    .alternative-cta {
      text-align: center;
      padding-top: 24px;
      border-top: 1px solid #e0e0e0;
      margin-top: 24px;
    }
    
    .alternative-cta p {
      margin-bottom: 16px;
      font-size: 1rem;
    }
    
    .btn {
      display: inline-block;
      padding: 16px 32px;
      border-radius: 8px;
      text-decoration: none;
      font-weight: 600;
      font-size: 1rem;
      transition: all 0.2s ease;
      border: none;
      cursor: pointer;
    }
    
    .btn-primary {
      background: var(--n5-rust);
      color: white;
    }
    
    .btn-primary:hover {
      background: var(--n5-rust-dark);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(122, 47, 31, 0.3);
    }
    
    .btn-secondary {
      background: var(--n5-gold);
      color: var(--n5-dark);
    }
    
    .btn-secondary:hover {
      background: var(--n5-gold-bright);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(212, 165, 116, 0.4);
    }
    
    .btn-outline {
      background: transparent;
      color: var(--n5-rust);
      border: 2px solid var(--n5-rust);
    }
    
    .btn-outline:hover {
      background: var(--n5-rust);
      color: white;
    }
    
    .social-proof {
      background: var(--n5-cream);
      padding: 80px 0;
    }
    
    .testimonial {
      max-width: 900px;
      margin: 0 auto;
      background: white;
      padding: 48px;
      border-radius: 20px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.08);
      border-left: 4px solid var(--n5-gold);
    }
    
    .testimonial-text {
      font-size: 1.3rem;
      font-style: italic;
      color: var(--n5-dark);
      margin-bottom: 24px;
      line-height: 1.7;
    }
    
    .testimonial-author {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    
    .author-info {
      flex: 1;
    }
    
    .author-name {
      font-weight: 700;
      color: var(--n5-rust);
      font-size: 1.1rem;
    }
    
    .author-title {
      color: #666;
      font-size: 0.95rem;
    }
    
    .section {
      padding: 80px 0;
    }
    
    .section-title {
      font-size: 2.5rem;
      font-weight: 700;
      text-align: center;
      margin-bottom: 24px;
      color: var(--n5-rust);
    }
    
    .section-subtitle {
      text-align: center;
      font-size: 1.2rem;
      color: #666;
      max-width: 800px;
      margin: 0 auto 64px;
    }
    
    .capabilities-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 32px;
      margin-bottom: 48px;
    }
    
    .capability-card {
      background: white;
      padding: 32px;
      border-radius: 16px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.06);
      border: 1px solid #e0e0e0;
      transition: all 0.2s ease;
    }
    
    .capability-card:hover {
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(122, 47, 31, 0.12);
      border-color: var(--n5-gold);
    }
    
    .capability-number {
      display: inline-block;
      width: 40px;
      height: 40px;
      background: var(--n5-rust);
      color: var(--n5-gold-bright);
      border-radius: 50%;
      text-align: center;
      line-height: 40px;
      font-weight: 700;
      margin-bottom: 16px;
    }
    
    .capability-card h3 {
      font-size: 1.3rem;
      margin-bottom: 12px;
      color: var(--n5-rust-dark);
    }
    
    .capability-card p {
      color: #555;
      line-height: 1.7;
    }
    
    .faq-section {
      background: var(--n5-cream);
    }
    
    .faq-list {
      max-width: 800px;
      margin: 0 auto;
    }
    
    .faq-item {
      background: white;
      padding: 32px;
      border-radius: 12px;
      margin-bottom: 16px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    
    .faq-question {
      font-size: 1.2rem;
      font-weight: 600;
      color: var(--n5-rust);
      margin-bottom: 12px;
    }
    
    .faq-answer {
      color: #555;
      line-height: 1.7;
    }
    
    .faq-answer ul {
      margin-left: 24px;
      margin-top: 12px;
    }
    
    .faq-answer li {
      margin-bottom: 8px;
    }
    
    .footer {
      background: var(--n5-dark);
      color: var(--n5-cream);
      padding: 64px 0 32px;
      text-align: center;
    }
    
    .footer-ctas {
      display: flex;
      justify-content: center;
      gap: 16px;
      flex-wrap: wrap;
      margin-bottom: 32px;
    }
    
    .footer-links {
      margin-bottom: 32px;
    }
    
    .footer-links a {
      color: var(--n5-gold);
      text-decoration: none;
      margin: 0 16px;
      transition: color 0.2s;
    }
    
    .footer-links a:hover {
      color: var(--n5-gold-bright);
    }
    
    .footer-note {
      color: rgba(245, 235, 224, 0.6);
      font-size: 0.9rem;
    }
    
    @media (max-width: 768px) {
      h1 {
        font-size: 2.5rem;
      }
      
      .subtitle {
        font-size: 1.2rem;
      }
      
      .hero {
        padding: 60px 0 80px;
      }
      
      .waitlist-card {
        padding: 32px 24px;
      }
      
      .capabilities-grid {
        grid-template-columns: 1fr;
      }
      
      .section {
        padding: 60px 0;
      }
      
      .footer-ctas {
        flex-direction: column;
      }
    }
  </style>
</head>
<body>
  <!-- Hero Section -->
  <section class="hero">
    <div class="container">
      <div class="hero-content">
        <div class="logo">
          <img src="/n5-logo.jpg" alt="N5 OS Logo">
        </div>
        <h1>N5 OS</h1>
        <p class="subtitle">Your AI Operating System for Founder Work</p>
        <p class="hero-description">
          Stop juggling disconnected tools. N5 OS is a complete operating system that turns scattered conversations, 
          meetings, contacts, and ideas into an intelligent, interconnected workspace that actually works the way you think.
        </p>
      </div>
    </div>
  </section>

  <!-- Waitlist CTA Section -->
  <section class="cta-section">
    <div class="container">
      <div class="waitlist-card">
        <h2>Join the Waitlist</h2>
        <p>Be among the first to get access when N5 OS launches. No spam, just updates on launch progress.</p>
        
        <!-- LaunchList Widget - REPLACE data-key-id WITH YOUR FORM KEY -->
        <div class="launchlist-widget" data-key-id="YOUR_FORM_KEY_HERE" data-height="180px">
          <!-- Placeholder - This will be replaced by LaunchList widget -->
          <div class="widget-placeholder">
            <h3>📋 LaunchList Widget Goes Here</h3>
            <p>Replace <code>YOUR_FORM_KEY_HERE</code> in the code with your actual LaunchList form key.</p>
          </div>
        </div>
        
        <div class="alternative-cta">
          <p><strong>Can't wait?</strong> Build your own system on Zo today.</p>
          <a href="https://www.zo.computer/?promo=VATT50" class="btn btn-secondary" target="_blank" rel="noopener">
            Start Building on Zo (50% off)
          </a>
        </div>
      </div>
    </div>
  </section>

  <!-- Social Proof / Testimonial -->
  <section class="social-proof">
    <div class="container">
      <div class="testimonial">
        <p class="testimonial-text">
          "Zo gave me my first ever taste of what it must be like to be a builder and it was intoxicating."
        </p>
        <div class="testimonial-author">
          <div class="author-info">
            <div class="author-name">Vrijen Attawar</div>
            <div class="author-title">Founder at Careerspan</div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- About N5 OS Section -->
  <section class="section">
    <div class="container">
      <h2 class="section-title">What Makes N5 OS Different?</h2>
      <p class="section-subtitle">
        N5 OS isn't another productivity app. It's a full operating system for founder work, 
        built on Zo Computer with orchestrated workflows that create a closed-loop system for everything you do.
      </p>
      
      <div class="capabilities-grid">
        <div class="capability-card">
          <span class="capability-number">1</span>
          <h3>Strategic Thinking Partner</h3>
          <p>Talk through strategy, pivots, or decisions. The system maintains conversation history, 
          tracks how strategies evolve, and auto-generates strategy documents with embedded voice notes.</p>
        </div>
        
        <div class="capability-card">
          <span class="capability-number">2</span>
          <h3>Meeting Intelligence Pipeline</h3>
          <p>Record meetings, get automatic transcription with speaker detection, structured follow-ups 
          (thank you notes, action items, CRM updates). Context from months ago surfaces automatically.</p>
        </div>
        
        <div class="capability-card">
          <span class="capability-number">3</span>
          <h3>Networking Event Processor</h3>
          <p>Dump business cards or contact info in any format. The system extracts data, enriches with research, 
          adds to CRM with context, and generates personalized follow-up drafts.</p>
        </div>
        
        <div class="capability-card">
          <span class="capability-number">4</span>
          <h3>Idea Evolution Tracker</h3>
          <p>Capture ideas in any format and watch them compound over time. The system detects themes, 
          surfaces related ideas, and tracks evolution through version history.</p>
        </div>
        
        <div class="capability-card">
          <span class="capability-number">5</span>
          <h3>Warm Introduction Generator</h3>
          <p>Generate personalized intro emails pulling from your CRM's relationship history. 
          The system suggests beneficial connections and drafts intros using actual conversation history.</p>
        </div>
        
        <div class="capability-card">
          <span class="capability-number">6</span>
          <h3>Consistent Messaging Library</h3>
          <p>Build a content library of positioning, value props, and case studies. Auto-insert relevant content 
          when generating communications, maintaining version history and consistent language.</p>
        </div>
        
        <div class="capability-card">
          <span class="capability-number">7</span>
          <h3>Lessons Learned System</h3>
          <p>Capture lessons with context and significance scoring. The system surfaces relevant lessons 
          before similar decisions, tracks patterns, and generates quarterly reviews.</p>
        </div>
        
        <div class="capability-card">
          <span class="capability-number">8</span>
          <h3>Email & Calendar Intelligence</h3>
          <p>AI access to Gmail and Google Calendar for inbox triage, response drafting in your voice, 
          automatic CRM updates, and meeting prep with relevant context pulled from history.</p>
        </div>
        
        <div class="capability-card">
          <span class="capability-number">9</span>
          <h3>After-Action Documentation</h3>
          <p>Automatically generate comprehensive documentation after any session: decisions made, 
          action items with owners, files modified, cross-references. Your institutional memory.</p>
        </div>
        
        <div class="capability-card">
          <span class="capability-number">10</span>
          <h3>Build & Execution Tracking</h3>
          <p>Track what you're building by monitoring commits, script executions, and file modifications. 
          Timeline of features shipped, complexity estimates, architectural decisions—without manual overhead.</p>
        </div>
      </div>
      
      <div style="text-align: center; margin-top: 48px;">
        <p style="font-size: 1.2rem; color: #555; margin-bottom: 24px;">
          <strong>The Common Thread:</strong> Full-context awareness across your CRM, knowledge base, conversation history, 
          and work artifacts. These are orchestrated workflows that create a closed-loop operating system for founder work.
        </p>
      </div>
    </div>
  </section>

  <!-- FAQ Section -->
  <section class="section faq-section">
    <div class="container">
      <h2 class="section-title">Frequently Asked Questions</h2>
      
      <div class="faq-list">
        <div class="faq-item">
          <div class="faq-question">What is N5 OS?</div>
          <div class="faq-answer">
            N5 OS is a complete operating system for founder work, built on top of Zo Computer. 
            It's not just another app—it's a fully integrated system that connects your conversations, 
            meetings, contacts, ideas, and work into an intelligent workspace with orchestrated workflows 
            that actually work the way you think.
          </div>
        </div>
        
        <div class="faq-item">
          <div class="faq-question">How is this different from using ChatGPT or Claude?</div>
          <div class="faq-answer">
            N5 OS maintains persistent context across everything you do. While ChatGPT or Claude give you 
            isolated conversations, N5 OS connects your meeting notes to your CRM, your strategy sessions 
            to your lessons learned, your ideas to your execution tracking. It's a closed-loop system 
            where every piece of information feeds into and enhances every other piece.
          </div>
        </div>
        
        <div class="faq-item">
          <div class="faq-question">Do I need to be technical to use N5 OS?</div>
          <div class="faq-answer">
            No. N5 OS is built on Zo Computer, which is designed for both technical and non-technical users. 
            The system is powered by principles and workflows that I've refined over years of coaching founders. 
            You interact with it naturally—through conversation, voice notes, email, or text.
          </div>
        </div>
        
        <div class="faq-item">
          <div class="faq-question">What's included when N5 OS launches?</div>
          <div class="faq-answer">
            The initial launch includes:
            <ul>
              <li>Complete N5 OS architecture and command system</li>
              <li>All 10 core capabilities (Strategic Thinking Partner, Meeting Intelligence, etc.)</li>
              <li>Pre-configured integrations with Gmail, Google Calendar, and Google Drive</li>
              <li>Documentation and onboarding support</li>
              <li>Access to updates and refinements as the system evolves</li>
            </ul>
          </div>
        </div>
        
        <div class="faq-item">
          <div class="faq-question">How much will it cost?</div>
          <div class="faq-answer">
            Pricing will be announced closer to launch. Waitlist members will get early access pricing 
            and the opportunity to provide feedback that shapes the final product. If you can't wait, 
            you can start building your own system on Zo today with 50% off using promo code VATT50.
          </div>
        </div>
        
        <div class="faq-item">
          <div class="faq-question">Can I build this myself on Zo?</div>
          <div class="faq-answer">
            Absolutely! N5 OS is built entirely on Zo Computer. If you want to start now, sign up for Zo 
            and you'll have access to the same platform. N5 OS is essentially a pre-built, refined system 
            with workflows I've developed through years of coaching founders. You're getting the architecture, 
            principles, and orchestrated workflows without having to figure it all out yourself.
          </div>
        </div>
        
        <div class="faq-item">
          <div class="faq-question">Who is N5 OS for?</div>
          <div class="faq-answer">
            N5 OS is designed for founders, VCs, and operators building in public who need to manage 
            strategy, relationships, ideas, and execution—all while maintaining context across everything. 
            If you've ever felt like your tools are working against you instead of for you, N5 OS is for you.
          </div>
        </div>
        
        <div class="faq-item">
          <div class="faq-question">When will N5 OS launch?</div>
          <div class="faq-answer">
            Launch date TBA. Waitlist members will be notified first and get early access before the public launch.
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <div class="footer-ctas">
        <a href="https://www.linkedin.com/in/vrijenattawar/" class="btn btn-primary" target="_blank" rel="noopener">
          Follow on LinkedIn
        </a>
        <a href="https://www.zo.computer/?promo=VATT50" class="btn btn-outline" target="_blank" rel="noopener">
          Build on Zo (50% off)
        </a>
      </div>
      
      <div class="footer-links">
        <a href="https://www.zo.computer" target="_blank" rel="noopener">Powered by Zo Computer</a>
        <a href="https://www.linkedin.com/in/vrijenattawar/" target="_blank" rel="noopener">About Vrijen</a>
      </div>
      
      <p class="footer-note">
        © 2025 N5 OS. Built on Zo Computer.
      </p>
    </div>
  </footer>
</body>
</html>
  `);
});

export default app;
