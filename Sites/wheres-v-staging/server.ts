import { Hono } from 'hono'
import { serveStatic } from 'hono/bun'
import { cors } from 'hono/cors'
import { $ } from 'bun'

const app = new Hono()

// CORS middleware
app.use('*', cors({
  origin: '*',
  allowMethods: ['GET', 'POST', 'OPTIONS'],
  allowHeaders: ['Content-Type'],
}))

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
    const legacyStatus = {
      home: 'home',
      pre_departure: 'departing',
      in_transit: 'flying',
      at_destination: 'arrived'
    }[state.state] || 'home'
    
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

// Serve static files for SPA
app.use('/*', serveStatic({ root: './dist' }))

const PORT = 54179

Bun.serve({
  fetch: app.fetch,
  port: PORT
})

console.log(`✈️ Where's V running on http://localhost:${PORT}`)

