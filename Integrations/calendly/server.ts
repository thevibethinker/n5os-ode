import { Hono } from "hono";
import { serve } from "bun";

const app = new Hono();

const CALENDLY_CLIENT_ID = (
  process.env.CALENDLY_CLIENT_ID ||
  process.env["Calendly-Client-ID"] ||
  process.env["CALENDLY-CLIENT-ID"] ||
  ""
).trim();

const CALENDLY_CLIENT_SECRET = (
  process.env.CALENDLY_CLIENT_SECRET ||
  process.env["Calendly-Client-Secret"] ||
  process.env["CALENDLY-CLIENT-SECRET"] ||
  ""
).trim();

const CALENDLY_WEBHOOK_SIGNING_KEY = (
  process.env.CALENDLY_WEBHOOK_SIGNING_KEY ||
  process.env["Calendly-Webhook-Signing-Key"] ||
  process.env["CALENDLY-WEBHOOK-SIGNING-KEY"] ||
  ""
).trim();

const REDIRECT_URI = "https://calendly-auth-va.zocomputer.io/callback";
const TOKEN_FILE = `${process.env.HOME}/.config/calendly_tokens.json`;
const PKCE_FILE = `${process.env.HOME}/.config/calendly_pkce.json`;
// Note: Calendly OAuth does not accept scope parameter - omit entirely

interface TokenData {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_at: number;
  created_at: string;
  owner_uri: string;
  organization_uri: string;
}

type PkceRecord = {
  code_verifier: string;
  created_at_ms: number;
};

function base64urlFromBytes(bytes: Uint8Array): string {
  return Buffer.from(bytes)
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/g, "");
}

function randomBase64Url(nBytes: number): string {
  const bytes = new Uint8Array(nBytes);
  crypto.getRandomValues(bytes);
  return base64urlFromBytes(bytes);
}

async function sha256Base64Url(input: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(input));
  return base64urlFromBytes(new Uint8Array(digest));
}

async function loadPkceStore(): Promise<Record<string, PkceRecord>> {
  try {
    const f = Bun.file(PKCE_FILE);
    if (await f.exists()) return await f.json();
  } catch {
    // ignore
  }
  return {};
}

async function savePkceStore(store: Record<string, PkceRecord>): Promise<void> {
  await Bun.write(PKCE_FILE, JSON.stringify(store, null, 2));
}

async function putPkce(state: string, code_verifier: string): Promise<void> {
  const store = await loadPkceStore();
  store[state] = { code_verifier, created_at_ms: Date.now() };
  // prune > 20 minutes
  const cutoff = Date.now() - 20 * 60 * 1000;
  for (const [k, v] of Object.entries(store)) {
    if (v.created_at_ms < cutoff) delete store[k];
  }
  await savePkceStore(store);
}

async function takePkce(state: string): Promise<string | null> {
  const store = await loadPkceStore();
  const rec = store[state];
  if (!rec) return null;
  delete store[state];
  await savePkceStore(store);
  return rec.code_verifier;
}

async function saveTokens(tokens: TokenData): Promise<void> {
  await Bun.write(TOKEN_FILE, JSON.stringify(tokens, null, 2));
  console.log(`[${new Date().toISOString()}] Tokens saved to ${TOKEN_FILE}`);
}

async function loadTokens(): Promise<TokenData | null> {
  try {
    const file = Bun.file(TOKEN_FILE);
    if (await file.exists()) {
      return await file.json();
    }
  } catch (e) {
    console.error("Failed to load tokens:", e);
  }
  return null;
}

app.get("/", async (c) => {
  const state = randomBase64Url(16);
  const code_verifier = randomBase64Url(32);
  const code_challenge = await sha256Base64Url(code_verifier);
  await putPkce(state, code_verifier);

  const authUrl = "https://auth.calendly.com/oauth/authorize"
    + `?client_id=${encodeURIComponent(CALENDLY_CLIENT_ID)}`
    + `&redirect_uri=${encodeURIComponent(REDIRECT_URI)}`
    + `&response_type=code`
    + `&state=${state}`
    + `&code_challenge=${code_challenge}`
    + `&code_challenge_method=S256`;

  return c.html(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Calendly Integration - Zo</title>
      <style>
        body { font-family: system-ui, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        h1 { color: #006bff; }
        .btn { display: inline-block; background: #006bff; color: white; padding: 12px 24px; 
               text-decoration: none; border-radius: 8px; font-weight: 600; }
        .btn:hover { background: #0052cc; }
        .status { margin-top: 20px; padding: 15px; background: #f0f0f0; border-radius: 8px; }
        code { background: #f5f5f5; padding: 2px 6px; border-radius: 4px; }
      </style>
    </head>
    <body>
      <h1>🗓️ Calendly Integration</h1>
      <p>This flow uses OAuth + PKCE.</p>
      <p><strong>Redirect URI:</strong> <code>${REDIRECT_URI}</code></p>
      <a href="${authUrl}" class="btn">Connect Calendly</a>
      <div class="status">
        <strong>Status:</strong> Ready to authorize
      </div>
    </body>
    </html>
  `);
});

app.get("/callback", async (c) => {
  const code = c.req.query("code");
  const state = c.req.query("state");
  const error = c.req.query("error");

  if (error) {
    return c.html(`<h1>Authorization Error</h1><p>${error}</p>`);
  }

  if (!code) {
    return c.html(`<h1>Missing authorization code</h1>`);
  }

  if (!state) {
    return c.html(`<h1>Missing state</h1><p>Please start over from <a href="/">/</a></p>`);
  }

  const code_verifier = await takePkce(state);
  if (!code_verifier) {
    return c.html(`<h1>Missing PKCE verifier</h1><p>Please start over from <a href="/">/</a></p>`);
  }

  if (!CALENDLY_CLIENT_ID || !CALENDLY_CLIENT_SECRET) {
    return c.html(`<h1>Missing Calendly OAuth credentials</h1><p>CALENDLY_CLIENT_ID / CALENDLY_CLIENT_SECRET not set</p>`);
  }

  const tokenUrl = "https://auth.calendly.com/oauth/token";
  const tokenBodyBase = {
    grant_type: "authorization_code",
    code: code,
    redirect_uri: REDIRECT_URI,
    code_verifier: code_verifier,
  };

  const basicAuth = Buffer.from(`${CALENDLY_CLIENT_ID}:${CALENDLY_CLIENT_SECRET}`).toString("base64");

  async function tryTokenExchange(mode: "basic" | "post") {
    const headers: Record<string, string> = {
      "Content-Type": "application/x-www-form-urlencoded",
      "Accept": "application/json",
    };

    const body = new URLSearchParams({
      ...tokenBodyBase,
      ...(mode === "post" ? { client_id: CALENDLY_CLIENT_ID, client_secret: CALENDLY_CLIENT_SECRET } : {}),
    }).toString();

    if (mode === "basic") {
      headers["Authorization"] = `Basic ${basicAuth}`;
    }

    const resp = await fetch(tokenUrl, {
      method: "POST",
      headers,
      body,
    });

    const text = await resp.text();
    return { ok: resp.ok, status: resp.status, text };
  }

  // 1) Try client_secret_basic
  let attempt = await tryTokenExchange("basic");
  if (!attempt.ok) {
    console.error(`Token exchange failed (basic): status=${attempt.status} body=${attempt.text}`);
    // 2) Try client_secret_post (some providers prefer this)
    const attempt2 = await tryTokenExchange("post");
    if (!attempt2.ok) {
      console.error(`Token exchange failed (post): status=${attempt2.status} body=${attempt2.text}`);
      return c.html(`
        <!DOCTYPE html>
        <html>
        <head><title>Token Exchange Failed</title></head>
        <body>
          <h1>❌ Token Exchange Failed</h1>
          <p>Tried client_secret_basic and client_secret_post.</p>
          <p>Basic status: ${attempt.status}</p>
          <pre>${attempt.text}</pre>
          <p>Post status: ${attempt2.status}</p>
          <pre>${attempt2.text}</pre>
          <a href="/">Try again</a>
        </body>
        </html>
      `);
    }
    attempt = attempt2;
  }

  const tokenData = JSON.parse(attempt.text);

  const tokens: TokenData = {
    access_token: tokenData.access_token,
    refresh_token: tokenData.refresh_token,
    token_type: tokenData.token_type,
    expires_at: Date.now() + (tokenData.expires_in * 1000),
    created_at: new Date().toISOString(),
    owner_uri: tokenData.owner,
    organization_uri: tokenData.organization,
  };

  await saveTokens(tokens);

  return c.html(`
    <!DOCTYPE html>
    <html>
    <head>
      <title>Connected!</title>
      <style>
        body { font-family: system-ui, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
        h1 { color: #00c853; }
        .success { background: #e8f5e9; padding: 20px; border-radius: 8px; margin: 20px 0; }
        code { background: #f5f5f5; padding: 2px 6px; border-radius: 4px; }
      </style>
    </head>
    <body>
      <h1>✅ Calendly Connected!</h1>
      <div class="success">
        <p><strong>Access Token:</strong> Saved</p>
        <p><strong>Refresh Token:</strong> Saved</p>
        <p><strong>Expires:</strong> ${new Date(tokens.expires_at).toLocaleString()}</p>
      </div>
      <p>You can now use the Calendly CLI:</p>
      <pre><code>python3 Integrations/calendly/calendly_cli.py verify</code></pre>
      <p>Or close this window and return to Zo.</p>
    </body>
    </html>
  `);

});

app.post("/webhook", async (c) => {
  const signature = c.req.header("Calendly-Webhook-Signature");
  const body = await c.req.text();

  if (!signature) {
    console.error("Missing webhook signature");
    return c.json({ error: "Missing signature" }, 401);
  }

  // Verify signature
  const [t, v1] = signature.split(",").reduce((acc, part) => {
    const [key, value] = part.split("=");
    if (key === "t") acc[0] = value;
    if (key === "v1") acc[1] = value;
    return acc;
  }, ["", ""] as [string, string]);

  const payload = `${t}.${body}`;
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(CALENDLY_WEBHOOK_SIGNING_KEY),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const signatureBytes = await crypto.subtle.sign("HMAC", key, encoder.encode(payload));
  const expectedSignature = Array.from(new Uint8Array(signatureBytes))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");

  if (expectedSignature !== v1) {
    console.error("Invalid webhook signature");
    return c.json({ error: "Invalid signature" }, 401);
  }

  const event = JSON.parse(body);
  console.log(`[${new Date().toISOString()}] Webhook received: ${event.event}`);

  if (event.event === "invitee.created") {
    const payload = event.payload;
    const inviteeName = payload.name || "Unknown";
    const inviteeEmail = payload.email || "";
    const eventTypeName = payload.event_type?.name || "Meeting";
    const scheduledTime = payload.scheduled_event?.start_time || "";
    
    console.log(`[${new Date().toISOString()}] New booking: ${inviteeName} (${inviteeEmail}) for "${eventTypeName}" at ${scheduledTime}`);

    // Trigger CRM profile creation + enrichment via Python script
    if (inviteeEmail) {
      try {
        const proc = Bun.spawn([
          "python3",
          "/home/workspace/Integrations/calendly/crm_intake.py",
          "--email", inviteeEmail,
          "--name", inviteeName,
          "--event-type", eventTypeName,
          "--scheduled-time", scheduledTime
        ], {
          stdout: "pipe",
          stderr: "pipe"
        });

        const output = await new Response(proc.stdout).text();
        const errors = await new Response(proc.stderr).text();
        
        if (errors) {
          console.error(`[CRM Intake Error] ${errors}`);
        }
        if (output) {
          console.log(`[CRM Intake] ${output.trim()}`);
        }
      } catch (e) {
        console.error(`[CRM Intake Exception] ${e}`);
      }
    }
  }

  if (event.event === "invitee.canceled") {
    const payload = event.payload;
    console.log(`[${new Date().toISOString()}] Booking canceled: ${payload.name} (${payload.email})`);
    // Could update CRM to note cancellation, but not critical
  }

  return c.json({ received: true });
});

app.get("/health", (c) => {
  return c.json({ 
    status: "ok", 
    service: "calendly-auth",
    timestamp: new Date().toISOString()
  });
});

const port = parseInt(process.env.PORT || "50001");
console.log(`[${new Date().toISOString()}] Calendly integration server starting on port ${port}`);

serve({
  fetch: app.fetch,
  port: port,
});
