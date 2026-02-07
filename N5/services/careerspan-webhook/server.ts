import { Hono } from 'hono'
import { cors } from 'hono/cors'

const app = new Hono()

const INBOX_DIR = '/home/workspace/N5/inbox/careerspan-webhooks'
const AUDIT_LOG = '/home/workspace/N5/logs/careerspan_webhook_audit.jsonl'
const FOUNDER_TOKEN = process.env.FOUNDER_AUTH_TOKEN
const ZO_TOKEN = process.env.ZO_CLIENT_IDENTITY_TOKEN

// CORS - wide open for webhooks
app.use('*', cors({
  origin: '*',
  allowMethods: ['GET', 'POST', 'OPTIONS'],
  allowHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
}))

// Health check
app.get('/health', (c) => c.json({ 
  status: 'active',
  auth_required: !!FOUNDER_TOKEN,
  inbox: INBOX_DIR
}))

// Webhook endpoint
app.post('/webhook', async (c) => {
  // Auth check
  if (FOUNDER_TOKEN) {
    const auth = c.req.header('Authorization')
    const token = auth?.replace('Bearer ', '')
    if (token !== FOUNDER_TOKEN) {
      return c.json({ error: 'Unauthorized' }, 401)
    }
  }
  
  const body = await c.req.json().catch(() => ({}))
  const headers = Object.fromEntries(c.req.raw.headers.entries())
  
  // Save to inbox
  const ts = new Date().toISOString().replace(/[:.]/g, '-')
  const filename = `${ts}.json`
  await Bun.write(`${INBOX_DIR}/${filename}`, JSON.stringify({
    received_at: new Date().toISOString(),
    headers,
    payload: body
  }, null, 2))
  
  // Audit log
  await Bun.write(Bun.file(AUDIT_LOG), JSON.stringify({
    event: 'webhook_received',
    filename,
    payload_keys: Object.keys(body),
    logged_at: new Date().toISOString()
  }) + '\n', { append: true })
  
  // Notify via SMS
  if (ZO_TOKEN) {
    const summary = body.message || body.type || body.event || `New data (${Object.keys(body).join(', ')})`
    fetch('https://api.zo.computer/zo/ask', {
      method: 'POST',
      headers: { 'Authorization': ZO_TOKEN, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input: `Send an SMS to V: "🔔 Careerspan webhook: ${summary}". Use send_sms_to_user tool immediately.`
      })
    }).catch(e => console.error('SMS failed:', e))
  }
  
  return c.json({ status: 'received', filename, timestamp: new Date().toISOString() })
})

const port = parseInt(process.env.PORT || '53230')
console.log(`Started on port ${port}`)
export default { port, fetch: app.fetch }
