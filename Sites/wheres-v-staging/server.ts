import { Hono } from 'hono'
import { serveStatic } from 'hono/bun'
import { cors } from 'hono/cors'
import { $ } from 'bun'
import { WorkOS } from '@workos-inc/node'
import { serialize, parse } from 'cookie'

const app = new Hono()

// Environment variables
const WORKOS_API_KEY = process.env.WORKOS_API_KEY
const WORKOS_CLIENT_ID = process.env.WORKOS_CLIENT_ID
const WORKOS_COOKIE_PASSWORD = process.env.WORKOS_COOKIE_PASSWORD
const WORKOS_REDIRECT_URI = process.env.WORKOS_REDIRECT_URI
const WHERES_V_ALLOWED_EMAILS = process.env.WHERES_V_ALLOWED_EMAILS

// Validate required env vars
if (!WORKOS_API_KEY || !WORKOS_CLIENT_ID || !WORKOS_COOKIE_PASSWORD || !WORKOS_REDIRECT_URI) {
  throw new Error('Missing required WorkOS environment variables: WORKOS_API_KEY, WORKOS_CLIENT_ID, WORKOS_COOKIE_PASSWORD, WORKOS_REDIRECT_URI')
}

if (!WHERES_V_ALLOWED_EMAILS) {
  throw new Error('Missing required WHERES_V_ALLOWED_EMAILS environment variable')
}

if (WORKOS_COOKIE_PASSWORD.length !== 32) {
  throw new Error('WORKOS_COOKIE_PASSWORD must be exactly 32 characters')
}

// Parse allowed emails (comma-separated, trimmed, case-insensitive)
const allowedEmails = new Set(
  WHERES_V_ALLOWED_EMAILS.split(',').map(e => e.trim().toLowerCase()).filter(Boolean)
)

console.log(`[Auth] Loaded ${allowedEmails.size} allowed emails`)

// Initialize WorkOS
const workos = new WorkOS(WORKOS_API_KEY)
const SESSION_COOKIE_NAME = 'wos-session'

// CORS middleware
app.use('*', cors({
  origin: '*',
  allowMethods: ['GET', 'POST', 'OPTIONS'],
  allowHeaders: ['Content-Type'],
}))

// Helper to parse cookies from request
const getCookies = (c: any) => {
  const cookieHeader = c.req.header('Cookie')
  return parse(cookieHeader || '')
}

// Helper to set cookie in response
const setCookie = (c: any, name: string, value: string, options: any = {}) => {
  const serialized = serialize(name, value, {
    path: '/',
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    ...options
  })
  c.header('Set-Cookie', serialized)
}

// Helper to delete cookie
const deleteCookie = (c: any, name: string) => {
  const serialized = serialize(name, '', {
    path: '/',
    httpOnly: true,
    secure: true,
    sameSite: 'lax',
    maxAge: 0
  })
  c.header('Set-Cookie', serialized)
}

// Helper to check if request is for a public asset
const isPublicAsset = (path: string): boolean => {
  if (path.startsWith('/assets/') || path.startsWith('/health')) return true
  if (path.match(/\.(js|css|svg|png|jpg|jpeg|gif|ico|webp|woff|woff2|ttf|eot|map)$/i)) {
    return true
  }
  return false
}

// Public routes (no auth required)
const publicRoutes = ['/login', '/callback', '/logout', '/health']

// Auth middleware
app.use('*', async (c, next) => {
  const path = c.req.path

  // Skip auth for public routes and static assets
  if (publicRoutes.some(route => path.startsWith(route)) || isPublicAsset(path)) {
    return next()
  }

  const cookies = getCookies(c)
  const sessionData = cookies[SESSION_COOKIE_NAME]

  // No session cookie - redirect to login
  if (!sessionData) {
    console.log(`[Auth] No session cookie for ${path}`)
    return c.redirect('/login')
  }

  try {
    // Load and verify session
    const result = await workos.userManagement.authenticateWithSessionCookie({
      sessionData,
      cookiePassword: WORKOS_COOKIE_PASSWORD
    })

    if (result.authenticated) {
      const user = result.user

      // Check allowlist
      if (!allowedEmails.has(user.email.toLowerCase())) {
        console.log(`[Auth] Email not in allowlist: ${user.email}`)
        deleteCookie(c, SESSION_COOKIE_NAME)
        return c.text('Access denied: your email is not authorized', 403)
      }

      console.log(`[Auth] Authenticated: ${user.email}`)
      // Store user in context for downstream handlers
      c.set('user' as never, user)
      return next()
    }

    // Session not authenticated
    const reason = !result.authenticated && 'reason' in result ? (result as any).reason : 'unknown'
    console.log(`[Auth] Invalid session for ${path} - reason: ${reason}`)
    deleteCookie(c, SESSION_COOKIE_NAME)
    return c.redirect('/login')

  } catch (error) {
    console.error('[Auth] Session verification error:', error)
    deleteCookie(c, SESSION_COOKIE_NAME)
    return c.redirect('/login')
  }
})

/**
 * GET /login
 * Redirect to WorkOS AuthKit authorization URL
 */
app.get('/login', (c) => {
  const authorizationUrl = workos.userManagement.getAuthorizationUrl({
    clientId: WORKOS_CLIENT_ID,
    redirectUri: WORKOS_REDIRECT_URI,
    provider: 'authkit'
  })
  console.log(`[Auth] Redirecting to WorkOS authorization`)
  return c.redirect(authorizationUrl)
})

/**
 * GET /callback
 * Handle OAuth callback from WorkOS
 */
app.get('/callback', async (c) => {
  const code = c.req.query('code')

  if (!code) {
    console.error('[Auth] No code parameter in callback')
    return c.text('Authorization failed: no code received', 400)
  }

  try {
    console.log('[Auth] Exchanging code for session')
    const authResponse = await workos.userManagement.authenticateWithCode({
      code,
      clientId: WORKOS_CLIENT_ID,
      session: {
        sealSession: true,
        cookiePassword: WORKOS_COOKIE_PASSWORD
      }
    })

    // WorkOS AuthKit should include sealedSession in the response
    if (!authResponse.sealedSession) {
      console.error('[Auth] No sealedSession in response')
      return c.text('Authentication failed: no session data received', 500)
    }

    // Set session cookie
    setCookie(c, SESSION_COOKIE_NAME, authResponse.sealedSession)
    console.log('[Auth] Session created, redirecting to /')

    return c.redirect('/')
  } catch (error) {
    console.error('[Auth] Authentication failed:', error)
    return c.text('Authentication failed', 500)
  }
})

/**
 * GET /logout
 * Logout user and redirect to login
 */
app.get('/logout', (c) => {
  deleteCookie(c, SESSION_COOKIE_NAME)
  console.log('[Auth] Cleared session cookie, redirecting to /login')
  return c.redirect('/login')
})

/**
 * GET /api/current-state
 * Returns full state machine output with trip context
 *
 * Response shape:
 * {
 *   state: "home" | "pre_departure" | "in_transit" | "at_destination",
 *   current_leg: Leg | null,
 *   current_trip: Trip | null,
 *   last_trip: Trip | null,
 *   next_trip: Trip | null,
 *   message: string,
 *   context: {
 *     last_destination: string | null,
 *     next_destination: string | null,
 *     leg_number?: number,
 *     total_legs?: number,
 *     hotel?: { name, address, check_in, check_out } | null,
 *     countdown_days?: number
 *   }
 * }
 */
app.get('/api/current-state', async (c) => {
  try {
    const result = await $`python3 ${import.meta.dir}/scripts/trip_store_v2.py state`.text()
    return c.json(JSON.parse(result))
  } catch (error) {
    console.error('Error in /api/current-state:', error)
    // Graceful fallback
    return c.json({
      state: 'home',
      current_leg: null,
      current_trip: null,
      last_trip: null,
      next_trip: null,
      message: 'V is home in NYC',
      context: {
        last_destination: null,
        next_destination: null
      }
    })
  }
})

/**
 * GET /api/status (LEGACY)
 * Backward compatible endpoint - maps to new state machine
 */
app.get('/api/status', async (c) => {
  try {
    const result = await $`python3 ${import.meta.dir}/scripts/trip_store_v2.py state`.text()
    const state = JSON.parse(result)

    // Map new state to legacy format
    const statusMap = {
      home: 'home',
      pre_departure: 'departing',
      in_transit: 'flying',
      at_destination: 'arrived'
    }
    const legacyStatus = statusMap[state.state as keyof typeof statusMap] || 'home'

    // Build legacy flight object if there's an active leg
    let flight = null
    if (state.current_leg) {
      const leg = state.current_leg
      flight = {
        flight_number: leg.flight?.number || null,
        departure_airport: leg.flight?.departure_airport || null,
        arrival_airport: leg.flight?.arrival_airport || null,
        departure_time: leg.flight?.departure_time || null,
        arrival_time: leg.flight?.arrival_time || null
      }
    }

    return c.json({
      status: legacyStatus,
      message: state.message,
      flight
    })
  } catch (error) {
    console.error('Error in /api/status:', error)
    return c.json({
      status: 'home',
      message: 'V is home in NYC',
      flight: null
    })
  }
})

/**
 * GET /api/trips
 * List all trips (for debugging/admin)
 */
app.get('/api/trips', async (c) => {
  try {
    const tripsResult = await $`python3 ${import.meta.dir}/scripts/trip_store_v2.py list-trips`.text()
    const legsResult = await $`python3 ${import.meta.dir}/scripts/trip_store_v2.py list-legs`.text()

    return c.json({
      trips: JSON.parse(tripsResult),
      legs: JSON.parse(legsResult)
    })
  } catch (error) {
    console.error('Error in /api/trips:', error)
    return c.json({ trips: [], legs: [] })
  }
})

/**
 * GET /api/leg/:legId
 * Get details for a specific leg
 */
app.get('/api/leg/:legId', async (c) => {
  try {
    const legId = c.req.param('legId')
    const result = await $`python3 ${import.meta.dir}/scripts/trip_store_v2.py get-leg ${legId}`.text()
    return c.json(JSON.parse(result))
  } catch (error) {
    console.error('Error in /api/leg:', error)
    return c.json({ error: 'Leg not found' }, 404)
  }
})

// Health check
app.get('/health', (c) => c.json({ status: 'ok' }))

// Serve static files for SPA (auth middleware will gate this)
app.use('/*', serveStatic({ root: './dist' }))

const PORT = 54179

Bun.serve({
  fetch: app.fetch,
  port: PORT
})

console.log(`✈️ Where's V running on http://localhost:${PORT}`)
