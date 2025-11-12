import { readFileSync } from 'fs';
import { join } from 'path';

export async function GET() {
  try {
    const dataPath = '/home/workspace/wheresv-data/trips.jsonl';
    const content = readFileSync(dataPath, 'utf-8');
    
    // Read last line (most recent trip)
    const lines = content.trim().split('\n');
    const lastLine = lines[lines.length - 1];
    
    if (!lastLine) {
      return new Response(JSON.stringify({ status: 'no_trips' }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    const tripData = JSON.parse(lastLine);
    
    return new Response(JSON.stringify(tripData), {
      headers: { 
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache, no-store, must-revalidate'
      }
    });
  } catch (error) {
    console.error('Error reading trip data:', error);
    return new Response(JSON.stringify({ error: 'Failed to load trip data' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
