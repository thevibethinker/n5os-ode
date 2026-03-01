#!/usr/bin/env bun

/**
 * Anonymous Call Logging Utilities for Zo Hotline
 * 
 * PRIVACY FIRST: This module handles anonymous pattern logging only.
 * NO PII (names, phone numbers, specific details) is ever stored.
 * Only aggregate patterns for improving the advisory system.
 */

import { existsSync } from "fs";

const DB_PATH = "/home/workspace/Datasets/zo-hotline-calls/data.duckdb";

export function generateUUID(): string {
  return crypto.randomUUID();
}

/**
 * Log anonymous call patterns to DuckDB
 * NO PERSONAL INFORMATION - patterns only
 */
export async function logCallPattern(data: {
  callId?: string;
  duration?: number;
  topics?: string[];
  levelAssessed?: number;
  escalationRequested?: boolean;
  conceptsExplained?: string[];
}): Promise<boolean> {
  try {
    const callId = data.callId || generateUUID();
    const start = new Date();
    const durationSeconds = Math.max(0, Math.round(data.duration || 0));
    const end = new Date(start.getTime() + (durationSeconds * 1000));
    const startedAt = start.toISOString();
    const endedAt = end.toISOString();
    
    // Sanitize topics to remove any PII
    const sanitizedTopics = data.topics
      ? data.topics.filter(topic => 
          // Only allow predefined topic categories
          ['assessment', 'level-1', 'level-2', 'level-3', 'meta-os', 
           'delay-the-draft', 'clarification-gates', 'adversarial-probing',
           'semantic-hunger', 'pools-vs-flows', 'escalation', 'general'].includes(topic)
        ).join(',')
      : 'general';
    const safeTopics = sanitizedTopics && sanitizedTopics.trim() ? sanitizedTopics : 'general';
    
    const insertScript = `
import duckdb
import json
import sys

try:
    data = json.loads(sys.stdin.read())
    con = duckdb.connect(data['db'])
    
    con.execute('''
      INSERT OR REPLACE INTO calls 
      (id, started_at, ended_at, duration_seconds, topics_discussed, 
       level_assessed, escalation_requested, raw_data)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', [
      data['id'], 
      data['started_at'],
      data['ended_at'], 
      data['duration'],
      data['topics'],
      data['level'],
      data['escalation'],
      data['raw']
    ])
    
    con.close()
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
`;
    
    const logData = JSON.stringify({
      db: DB_PATH,
      id: callId,
      started_at: startedAt,
      ended_at: endedAt,
      duration: durationSeconds,
      topics: safeTopics,
      level: data.levelAssessed || null,
      escalation: data.escalationRequested || false,
      raw: JSON.stringify({
        // Only anonymous metadata
        timestamp: startedAt,
        concepts_explained: data.conceptsExplained || [],
        topics_count: data.topics?.length || 0,
        pattern_type: "advisory_call"
      })
    });
    
    const proc = Bun.spawn(["python3", "-c", insertScript], {
      stdin: "pipe",
      stdout: "pipe",
      stderr: "pipe"
    });
    
    proc.stdin.write(logData);
    proc.stdin.end();
    
    const result = await new Response(proc.stdout).text();
    const error = await new Response(proc.stderr).text();
    await proc.exited;
    
    if (result.trim() === "SUCCESS") {
      console.log(`Call pattern logged: ${callId.substring(0, 8)}`);
      return true;
    } else {
      console.error("Failed to log call pattern:", error);
      return false;
    }
    
  } catch (error) {
    console.error("Error in logCallPattern:", error);
    return false;
  }
}

/**
 * Log escalation request (includes contact info for V's follow-up)
 */
export async function logEscalation(data: {
  name: string;
  contact: string;
  reason: string;
  callId?: string;
}): Promise<string | null> {
  try {
    const escalationId = generateUUID();
    const now = new Date().toISOString();
    
    const insertScript = `
import duckdb
import json
import sys

try:
    data = json.loads(sys.stdin.read())
    con = duckdb.connect(data['db'])
    
    con.execute('''
      INSERT INTO escalations (id, call_id, name, contact, reason, created_at)
      VALUES (?, ?, ?, ?, ?, ?)
    ''', [
      data['id'],
      data['call_id'], 
      data['name'],
      data['contact'],
      data['reason'],
      data['created_at']
    ])
    
    con.close()
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
`;
    
    const escalationData = JSON.stringify({
      db: DB_PATH,
      id: escalationId,
      call_id: data.callId || "unknown",
      name: data.name,
      contact: data.contact,
      reason: data.reason,
      created_at: now
    });
    
    const proc = Bun.spawn(["python3", "-c", insertScript], {
      stdin: "pipe",
      stdout: "pipe", 
      stderr: "pipe"
    });
    
    proc.stdin.write(escalationData);
    proc.stdin.end();
    
    const result = await new Response(proc.stdout).text();
    const error = await new Response(proc.stderr).text();
    await proc.exited;
    
    if (result.trim() === "SUCCESS") {
      console.log(`Escalation logged: ${escalationId.substring(0, 8)} for ${data.name}`);
      return escalationId;
    } else {
      console.error("Failed to log escalation:", error);
      return null;
    }
    
  } catch (error) {
    console.error("Error in logEscalation:", error);
    return null;
  }
}

/**
 * Get call analytics (anonymous patterns only)
 */
export async function getCallAnalytics(days: number = 30): Promise<any> {
  try {
    const analyticsScript = `
import duckdb
import json
import sys
from datetime import datetime, timedelta

try:
    data = json.loads(sys.stdin.read())
    con = duckdb.connect(data['db'])
    
    cutoff_date = (datetime.now() - timedelta(days=data['days'])).isoformat()
    
    # Call volume and duration stats
    call_stats = con.execute('''
      SELECT 
        COUNT(*) as total_calls,
        AVG(duration_seconds) as avg_duration,
        MAX(duration_seconds) as max_duration,
        COUNT(CASE WHEN escalation_requested THEN 1 END) as escalations
      FROM calls 
      WHERE started_at > ?
    ''', [cutoff_date]).fetchone()
    
    # Topic distribution
    topic_stats = con.execute('''
      SELECT 
        topics_discussed,
        COUNT(*) as count
      FROM calls 
      WHERE started_at > ? AND topics_discussed IS NOT NULL
      GROUP BY topics_discussed
      ORDER BY count DESC
    ''', [cutoff_date]).fetchall()
    
    # Level assessment distribution
    level_stats = con.execute('''
      SELECT 
        level_assessed,
        COUNT(*) as count
      FROM calls 
      WHERE started_at > ? AND level_assessed IS NOT NULL
      GROUP BY level_assessed
      ORDER BY level_assessed
    ''', [cutoff_date]).fetchall()

    # Daily rollup in ET (current period uses UTC-5)
    daily_rollup_et = con.execute('''
      SELECT
        CAST(started_at - INTERVAL 5 HOUR AS DATE) as date_et,
        COUNT(*) as calls,
        ROUND(AVG(duration_seconds), 1) as avg_duration_seconds
      FROM calls
      WHERE started_at > ?
      GROUP BY date_et
      ORDER BY date_et DESC
    ''', [cutoff_date]).fetchall()
    
    con.close()
    
    result = {
      "period_days": data['days'],
      "call_volume": {
        "total_calls": call_stats[0] if call_stats[0] else 0,
        "avg_duration_seconds": round(call_stats[1] or 0, 1),
        "max_duration_seconds": call_stats[2] or 0,
        "escalation_rate": round((call_stats[3] or 0) / max(call_stats[0] or 1, 1) * 100, 1)
      },
      "topics": [{"topic": row[0], "count": row[1]} for row in (topic_stats or [])],
      "levels": [{"level": row[0], "count": row[1]} for row in (level_stats or [])],
      "daily_rollup_et": [
        {"date_et": str(row[0]), "calls": row[1], "avg_duration_seconds": row[2] or 0}
        for row in (daily_rollup_et or [])
      ],
      "timezone_reporting": "ET (UTC-5 for current period)",
      "source_dataset": "Datasets/zo-hotline-calls/data.duckdb"
    }
    
    print(json.dumps(result))
    
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;
    
    const queryData = JSON.stringify({
      db: DB_PATH,
      days: days
    });
    
    const proc = Bun.spawn(["python3", "-c", analyticsScript], {
      stdin: "pipe",
      stdout: "pipe",
      stderr: "pipe"
    });
    
    proc.stdin.write(queryData);
    proc.stdin.end();
    
    const result = await new Response(proc.stdout).text();
    const error = await new Response(proc.stderr).text();
    await proc.exited;
    
    try {
      return JSON.parse(result.trim());
    } catch {
      console.error("Failed to parse analytics:", error);
      return { error: "Failed to generate analytics" };
    }
    
  } catch (error) {
    console.error("Error in getCallAnalytics:", error);
    return { error: error.message };
  }
}

/**
 * Get pending escalations for V's review
 */
export async function getPendingEscalations(): Promise<any[]> {
  try {
    const escalationsScript = `
import duckdb
import json
import sys

try:
    data = json.loads(sys.stdin.read())
    con = duckdb.connect(data['db'])
    
    escalations = con.execute('''
      SELECT id, call_id, name, contact, reason, created_at
      FROM escalations 
      ORDER BY created_at DESC
      LIMIT 50
    ''').fetchall()
    
    con.close()
    
    result = []
    for row in escalations:
        result.append({
            "id": row[0],
            "call_id": row[1],
            "name": row[2],
            "contact": row[3], 
            "reason": row[4],
            "created_at": row[5]
        })
    
    print(json.dumps(result))
    
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;
    
    const queryData = JSON.stringify({ db: DB_PATH });
    
    const proc = Bun.spawn(["python3", "-c", escalationsScript], {
      stdin: "pipe",
      stdout: "pipe",
      stderr: "pipe"
    });
    
    proc.stdin.write(queryData);
    proc.stdin.end();
    
    const result = await new Response(proc.stdout).text();
    const error = await new Response(proc.stderr).text();
    await proc.exited;
    
    try {
      return JSON.parse(result.trim());
    } catch {
      console.error("Failed to parse escalations:", error);
      return [];
    }
    
  } catch (error) {
    console.error("Error in getPendingEscalations:", error);
    return [];
  }
}

/**
 * Health check for the logging system
 */
export async function healthCheck(): Promise<{ status: string; details: any }> {
  try {
    if (!existsSync(DB_PATH)) {
      return { status: "error", details: "Database file not found" };
    }
    
    const healthScript = `
import duckdb
import json

try:
    con = duckdb.connect("${DB_PATH}")
    
    # Check tables exist
    tables = con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    table_names = [row[0] for row in tables]
    
    # Get basic counts
    call_count = con.execute("SELECT COUNT(*) FROM calls").fetchone()[0] if 'calls' in table_names else 0
    escalation_count = con.execute("SELECT COUNT(*) FROM escalations").fetchone()[0] if 'escalations' in table_names else 0
    
    con.close()
    
    result = {
        "database_exists": True,
        "tables": table_names,
        "call_count": call_count,
        "escalation_count": escalation_count,
        "status": "healthy"
    }
    
    print(json.dumps(result))
    
except Exception as e:
    print(json.dumps({"error": str(e), "status": "error"}))
`;
    
    const proc = Bun.spawn(["python3", "-c", healthScript], {
      stdout: "pipe",
      stderr: "pipe"
    });
    
    const result = await new Response(proc.stdout).text();
    const error = await new Response(proc.stderr).text();
    await proc.exited;
    
    try {
      const parsed = JSON.parse(result.trim());
      return { 
        status: parsed.status || "unknown", 
        details: parsed 
      };
    } catch {
      return { 
        status: "error", 
        details: { error: "Failed to parse health check", stderr: error } 
      };
    }
    
  } catch (error) {
    return { 
      status: "error", 
      details: { error: error.message } 
    };
  }
}

// CLI interface
if (import.meta.main) {
  const args = process.argv.slice(2);
  const command = args[0];
  
  switch (command) {
    case "health":
      const health = await healthCheck();
      console.log(JSON.stringify(health, null, 2));
      break;
      
    case "analytics":
      const days = parseInt(args[1]) || 30;
      const analytics = await getCallAnalytics(days);
      console.log(JSON.stringify(analytics, null, 2));
      break;
      
    case "escalations":
      const escalations = await getPendingEscalations();
      console.log(JSON.stringify(escalations, null, 2));
      break;
      
    default:
      console.log("Usage: bun call-logger.ts <command>");
      console.log("Commands:");
      console.log("  health          - Check system health");
      console.log("  analytics [days] - Get call analytics (default: 30 days)");
      console.log("  escalations     - Get pending escalation requests");
      break;
  }
}
