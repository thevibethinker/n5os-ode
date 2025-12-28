import { Hono } from 'hono'
import { serveStatic } from 'hono/bun'
import { readFileSync, existsSync, writeFileSync } from 'fs'

const app = new Hono()

const LUMA_CANDIDATES = '/home/workspace/N5/data/luma_candidates.json'
const DECISIONS_FILE = '/home/workspace/N5/data/event_decisions.json'

interface LumaEvent {
  id: string
  title: string
  url: string
  event_date: string
  event_time?: string
  venue_name?: string
  venue_address?: string
  price?: string
  attendee_count?: number
  score?: number
  organizers?: string
  invitation_status?: string  // going, invited, pending, public
}

interface Decision {
  eventId: string
  decision: 'yes' | 'no' | 'maybe'
  decidedAt: string
  notes?: string
}

function loadEvents(): any[] {
  if (!existsSync(LUMA_CANDIDATES)) {
    return []
  }
  try {
    const raw = JSON.parse(readFileSync(LUMA_CANDIDATES, 'utf-8'))
    return raw.map((e: LumaEvent) => {
      let organizer = ''
      try {
        const orgs = JSON.parse(e.organizers || '[]')
        organizer = orgs.map((o: any) => o.name).join(', ')
      } catch {}
      
      return {
        id: e.id,
        title: e.title,
        url: e.url,
        date: e.event_date,
        time: e.event_time || '',
        location: e.venue_name || '',
        address: e.venue_address || '',
        price: e.price || 'TBD',
        attendees: e.attendee_count || 0,
        score: e.score || 0,
        organizer,
        coverImage: e.cover_image_url || '',
        source: 'luma',
        invitationStatus: e.invitation_status || 'public'  // going, invited, pending, public
      }
    })
  } catch (err) {
    console.error('Error loading events:', err)
    return []
  }
}

function loadDecisions(): Record<string, Decision> {
  if (!existsSync(DECISIONS_FILE)) {
    return {}
  }
  try {
    return JSON.parse(readFileSync(DECISIONS_FILE, 'utf-8'))
  } catch {
    return {}
  }
}

function saveDecisions(decisions: Record<string, Decision>) {
  writeFileSync(DECISIONS_FILE, JSON.stringify(decisions, null, 2))
}

// API Routes
app.get('/api/events', (c) => {
  const events = loadEvents()
  const decisions = loadDecisions()
  
  // Filter to next 30 days
  const now = new Date()
  const thirtyDaysOut = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000)
  
  const filtered = events
    .filter(e => {
      const eventDate = new Date(e.date)
      return eventDate >= now && eventDate <= thirtyDaysOut
    })
    .map(e => ({
      ...e,
      decision: decisions[e.id]?.decision || null,
      decisionNotes: decisions[e.id]?.notes || null
    }))
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
  
  return c.json({ events: filtered, total: filtered.length })
})

app.post('/api/events/:id/decide', async (c) => {
  const id = c.req.param('id')
  const body = await c.req.json()
  const { decision, notes } = body
  
  if (!['yes', 'no', 'maybe'].includes(decision)) {
    return c.json({ error: 'Invalid decision' }, 400)
  }
  
  const decisions = loadDecisions()
  decisions[id] = {
    eventId: id,
    decision,
    decidedAt: new Date().toISOString(),
    notes
  }
  saveDecisions(decisions)
  
  return c.json({ success: true, decision: decisions[id] })
})

app.get('/api/stats', (c) => {
  const events = loadEvents()
  const decisions = loadDecisions()
  
  const now = new Date()
  const thirtyDaysOut = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000)
  
  const upcoming = events.filter(e => {
    const d = new Date(e.date)
    return d >= now && d <= thirtyDaysOut
  })
  
  const eventIds = new Set(upcoming.map(e => e.id))
  const yes = Object.values(decisions).filter(d => eventIds.has(d.eventId) && d.decision === 'yes').length
  const no = Object.values(decisions).filter(d => eventIds.has(d.eventId) && d.decision === 'no').length
  const maybe = Object.values(decisions).filter(d => eventIds.has(d.eventId) && d.decision === 'maybe').length
  const undecided = upcoming.length - yes - no - maybe
  
  return c.json({
    total: upcoming.length,
    decided: { yes, no, maybe },
    undecided
  })
})

// Serve static files
app.use('/*', serveStatic({ root: './public' }))

// Fallback to index
app.get('/', (c) => {
  return c.html(readFileSync('./public/index.html', 'utf-8'))
})

export default {
  port: 3047,
  fetch: app.fetch,
}




