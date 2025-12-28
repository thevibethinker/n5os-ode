/**
 * TypeScript wrapper for Python trip_manager
 * Bridges Hono API to Python data layer
 */
import { spawn } from 'bun'

const PYTHON_SCRIPT = `${import.meta.dir}/trip_manager.py`

interface Trip {
  id: string
  source_email_id: string
  flights: Flight[]
  status: 'scheduled' | 'boarding' | 'in_flight' | 'landed'
}

interface Flight {
  airline: string
  flight_number: string
  departure: { airport: string; datetime: string }
  arrival: { airport: string; datetime: string }
  status: string
}

interface StatusResult {
  current_trip: Trip | null
  next_trip: Trip | null
  is_home: boolean
}

/**
 * Run Python script and return parsed output
 */
async function runPython(args: string[]): Promise<any> {
  const proc = spawn(['python3', PYTHON_SCRIPT, ...args], {
    stdout: 'pipe',
    stderr: 'pipe'
  })

  const [exitCode, stdout, stderr] = await Promise.all([
    proc.exited,
    proc.stdout.text(),
    proc.stderr.text()
  ])

  if (exitCode !== 0) {
    console.error(`Python script error: ${stderr}`)
    throw new Error(`Python script failed: ${stderr}`)
  }

  return JSON.parse(stdout)
}

/**
 * GET /api/status - Get current/next trip
 */
async function get_status(): Promise<StatusResult> {
  return await runPython(['get-status'])
}

/**
 * GET /api/trips - List all trips
 */
async function list_all_trips(): Promise<Trip[]> {
  return await runPython(['list'])
}

/**
 * POST /api/trips/sync - Scan email for new trips
 */
async function sync_trips(): Promise<{ added: number; duplicates: number }> {
  return await runPython(['sync-emails'])
}

export default {
  get_status,
  list_all_trips,
  sync_trips
}

