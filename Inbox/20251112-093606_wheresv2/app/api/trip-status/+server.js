import { readFileSync } from 'fs';

export async function GET() {
  try {
    const dataPath = '/home/workspace/wheresv2-data/trips.jsonl';
    const fileContent = readFileSync(dataPath, 'utf-8');
    
    if (!fileContent.trim()) {
      return new Response(JSON.stringify({ error: 'No active trips' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Read the last line (most recent trip)
    const lines = fileContent.trim().split('\n');
    const lastLine = lines[lines.length - 1];
    const tripData = JSON.parse(lastLine);
    
    return new Response(JSON.stringify(tripData), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('Error loading trip data:', error);
    return new Response(JSON.stringify({ error: 'Failed to load trip data' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
