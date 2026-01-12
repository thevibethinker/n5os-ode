import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

const api = new Hono()

api.use('/*', cors())

// Get current trip status
api.get('/status', async (c) => {
  try {
    // Get active trip
    const { stdout: tripData } = await execAsync(
      'python3 scripts/trip_manager.py',
      { cwd: '/home/workspace/wheres-v' }
    )
    
    if (!tripData.includes('Active trip:')) {
      return c.json({ 
        hasTrip: false,
        message: 'No active trip'
      })
    }
    
    // Extract JSON from output
    const jsonMatch = tripData.match(/Active trip: (\{[\s\S]*\})/)
    if (!jsonMatch) {
      return c.json({ hasTrip: false })
    }
    
    const trip = JSON.parse(jsonMatch[1])
    
    // Calculate stage
    const { stdout: stageData } = await execAsync(
      `python3 -c "
import json
import sys
sys.path.insert(0, '/home/workspace/wheres-v/scripts')
from stage_calculator import calculate_stage
from trip_manager import get_active_trip

trip = get_active_trip()
if trip:
    stage = calculate_stage(trip)
    print(json.dumps(stage))
"`,
      { cwd: '/home/workspace/wheres-v' }
    )
    
    const stage = JSON.parse(stageData)
    
    return c.json({
      hasTrip: true,
      trip,
      stage
    })
    
  } catch (error) {
    console.error('Error getting status:', error)
    return c.json({ 
      hasTrip: false, 
      error: error.message 
    }, 500)
  }
})

// Scan emails (manual trigger for now)
api.post('/scan-emails', async (c) => {
  try {
    // This will be integrated with Gmail API
    // For now, return success
    return c.json({ success: true, message: 'Email scan initiated' })
  } catch (error) {
    return c.json({ success: false, error: error.message }, 500)
  }
})

// Create trip manually (admin)
api.post('/create-trip', async (c) => {
  const tripData = await c.req.json()
  
  try {
    const { stdout } = await execAsync(
      `python3 -c "
import json
import sys
sys.path.insert(0, '/home/workspace/wheres-v/scripts')
from trip_manager import create_trip

trip_data = json.loads('${JSON.stringify(tripData).replace(/'/g, "\\'")}')
trip_id = create_trip(trip_data)
print(trip_id)
"`,
      { cwd: '/home/workspace/wheres-v' }
    )
    
    return c.json({ success: true, trip_id: stdout.trim() })
  } catch (error) {
    return c.json({ success: false, error: error.message }, 500)
  }
})

export default api
