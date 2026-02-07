import { Hono } from 'hono'
import { cors } from 'hono/cors'

const PORT = 8847
const INBOX_DIR = '/home/workspace/Careerspan/resumes/inbox'
const AUDIT_LOG = '/home/workspace/N5/logs/careerspan_webhook_v2.jsonl'
const EXPECTED_TOKEN = 'YummyYummyDataNomNomNom'

const app = new Hono()

app.use('*', cors({ origin: '*', allowMethods: ['GET', 'POST', 'OPTIONS'] }))

// Health check - no auth required
app.get('/health', (c) => c.json({ 
  status: 'ok', 
  version: '2.0.0',
  port: PORT,
  timestamp: new Date().toISOString()
}))

// Main webhook endpoint
app.post('/webhook', async (c) => {
  // 1. Validate auth
  const authHeader = c.req.header('Authorization')
  if (!authHeader) {
    await audit('auth_missing', { ip: c.req.header('x-forwarded-for') })
    return c.json({ error: 'Missing Authorization header' }, 401)
  }
  
  const token = authHeader.replace('Bearer ', '')
  if (token !== EXPECTED_TOKEN) {
    await audit('auth_invalid', { token_prefix: token.slice(0, 5) })
    return c.json({ error: 'Invalid token' }, 401)
  }

  // 2. Parse payload
  let payload: any
  try {
    payload = await c.req.json()
  } catch (e) {
    await audit('parse_error', { error: String(e) })
    return c.json({ error: 'Invalid JSON' }, 400)
  }

  // 3. Validate minimum required fields
  if (!payload.candidate?.name) {
    await audit('validation_error', { missing: 'candidate.name' })
    return c.json({ error: 'Missing required field: candidate.name' }, 400)
  }

  // 4. Save to inbox
  const filename = await saveToInbox(payload)
  
  // 5. Log success
  await audit('received', {
    filename,
    candidate: payload.candidate?.name,
    role: payload.role?.title,
    company: payload.role?.company,
    score: payload.overall_assessment?.score
  })

  // 6. Trigger async notification (fire and forget)
  notifyV(payload, filename).catch(console.error)

  return c.json({
    status: 'received',
    filename,
    timestamp: new Date().toISOString()
  })
})

// ─────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────

async function saveToInbox(payload: any): Promise<string> {
  await Bun.write('/dev/null', '').catch(() => {}) // ensure dirs via side effect
  
  const ts = new Date().toISOString().replace(/[:.]/g, '-')
  const slug = (payload.candidate?.name || 'unknown')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .slice(0, 30)
  
  const filename = `${ts}_${slug}.json`
  const filepath = `${INBOX_DIR}/${filename}`
  
  // Ensure inbox exists
  await Bun.spawn(['mkdir', '-p', INBOX_DIR]).exited
  
  await Bun.write(filepath, JSON.stringify({
    _meta: {
      received_at: new Date().toISOString(),
      source: 'dossier-webhook-v2'
    },
    ...payload
  }, null, 2))
  
  return filename
}

async function audit(event: string, data: Record<string, any>) {
  const entry = JSON.stringify({
    ts: new Date().toISOString(),
    event,
    ...data
  }) + '\n'
  
  await Bun.spawn(['mkdir', '-p', '/home/workspace/N5/logs']).exited
  const file = Bun.file(AUDIT_LOG)
  const existing = await file.exists() ? await file.text() : ''
  await Bun.write(AUDIT_LOG, existing + entry)
}

async function notifyV(payload: any, filename: string) {
  const token = process.env.ZO_CLIENT_IDENTITY_TOKEN
  if (!token) return
  
  const { candidate, role, overall_assessment } = payload
  const score = overall_assessment?.score ?? 'N/A'
  
  const body = `# Intelligence Brief Received

**Candidate:** ${candidate?.name}${candidate?.email ? ` (${candidate.email})` : ''}
**Role:** ${role?.title || 'Unknown'} @ ${role?.company || 'Unknown'}
**Score:** ${score}/100

**Bottom Line:** ${overall_assessment?.bottom_line || 'N/A'}

*File: \`${filename}\`*`

  await fetch('https://api.zo.computer/zo/ask', {
    method: 'POST',
    headers: {
      'Authorization': token,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      input: `Send email to V using send_email_to_user:
Subject: "📋 Brief: ${candidate?.name} → ${role?.title || 'Role'} @ ${role?.company || 'Company'} (${score}/100)"
Body:\n${body}\n\nSend immediately.`
    })
  })
}

// ─────────────────────────────────────────────────────────────
// Start
// ─────────────────────────────────────────────────────────────

console.log(`[careerspan-webhook-v2] Starting on port ${PORT}`)

export default {
  port: PORT,
  hostname: '0.0.0.0',
  fetch: app.fetch
}
