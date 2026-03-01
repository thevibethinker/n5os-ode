#!/usr/bin/env bun

import { existsSync } from "fs";

const DB_PATH = "/home/workspace/Datasets/vibe-pill-calls/data.duckdb";

export function generateUUID(): string {
  return crypto.randomUUID();
}

export async function logCallPattern(data: {
  callId?: string;
  memberPhone?: string;
  memberName?: string;
  memberStatus?: string;
  duration?: number;
  pathway?: string;
  outcome?: string;
  topics?: string[];
  escalationRequested?: boolean;
}): Promise<boolean> {
  try {
    const callId = data.callId || generateUUID();
    const start = new Date();
    const durationSeconds = Math.max(0, Math.round(data.duration || 0));
    const end = new Date(start.getTime() + (durationSeconds * 1000));
    const startedAt = start.toISOString();
    const endedAt = end.toISOString();

    const sanitizedTopics = data.topics
      ? data.topics.filter(topic =>
          ["intake", "support", "cobuild", "faq", "assessment",
           "meta-os", "pricing", "onboarding", "build-help",
           "account", "scheduling", "escalation", "general"].includes(topic)
        ).join(",")
      : "general";
    const safeTopics = sanitizedTopics && sanitizedTopics.trim() ? sanitizedTopics : "general";

    const insertScript = `
import duckdb
import json
import sys

try:
    data = json.loads(sys.stdin.read())
    con = duckdb.connect(data['db'])
    con.execute('''
      INSERT OR REPLACE INTO calls
      (id, member_phone, member_name, member_status, started_at, ended_at,
       duration_seconds, pathway, outcome, topics_discussed, escalation_requested, raw_data)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', [
      data['id'], data['member_phone'], data['member_name'], data['member_status'],
      data['started_at'], data['ended_at'], data['duration'],
      data['pathway'], data['outcome'], data['topics'],
      data['escalation'], data['raw']
    ])
    con.close()
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
`;

    const logData = JSON.stringify({
      db: DB_PATH,
      id: callId,
      member_phone: data.memberPhone || null,
      member_name: data.memberName || null,
      member_status: data.memberStatus || "prospect",
      started_at: startedAt,
      ended_at: endedAt,
      duration: durationSeconds,
      pathway: data.pathway || "faq",
      outcome: data.outcome || null,
      topics: safeTopics,
      escalation: data.escalationRequested || false,
      raw: JSON.stringify({
        timestamp: startedAt,
        topics_count: data.topics?.length || 0,
        pattern_type: "vibe_pill_call"
      })
    });

    const proc = Bun.spawn(["python3", "-c", insertScript], {
      stdin: "pipe", stdout: "pipe", stderr: "pipe"
    });
    proc.stdin.write(logData);
    proc.stdin.end();

    const result = await new Response(proc.stdout).text();
    await proc.exited;

    if (result.trim() === "SUCCESS") {
      console.log(`Call pattern logged: ${callId.substring(0, 8)}`);
      return true;
    }
    console.error("Failed to log call pattern");
    return false;
  } catch (error) {
    console.error("Error in logCallPattern:", error);
    return false;
  }
}

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
    ''', [data['id'], data['call_id'], data['name'], data['contact'], data['reason'], data['created_at']])
    con.close()
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
`;

    const proc = Bun.spawn(["python3", "-c", insertScript], {
      stdin: "pipe", stdout: "pipe", stderr: "pipe"
    });
    proc.stdin.write(JSON.stringify({
      db: DB_PATH, id: escalationId, call_id: data.callId || "unknown",
      name: data.name, contact: data.contact, reason: data.reason, created_at: now
    }));
    proc.stdin.end();

    const result = await new Response(proc.stdout).text();
    await proc.exited;

    if (result.trim() === "SUCCESS") {
      console.log(`Escalation logged: ${escalationId.substring(0, 8)} for ${data.name}`);
      return escalationId;
    }
    return null;
  } catch (error) {
    console.error("Error in logEscalation:", error);
    return null;
  }
}

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

    call_stats = con.execute('''
      SELECT
        COUNT(*) as total_calls,
        AVG(duration_seconds) as avg_duration,
        MAX(duration_seconds) as max_duration,
        COUNT(CASE WHEN escalation_requested THEN 1 END) as escalations
      FROM calls WHERE started_at > ?
    ''', [cutoff_date]).fetchone()

    pathway_stats = con.execute('''
      SELECT pathway, COUNT(*) as count
      FROM calls WHERE started_at > ? AND pathway IS NOT NULL
      GROUP BY pathway ORDER BY count DESC
    ''', [cutoff_date]).fetchall()

    status_stats = con.execute('''
      SELECT member_status, COUNT(*) as count
      FROM calls WHERE started_at > ? AND member_status IS NOT NULL
      GROUP BY member_status ORDER BY count DESC
    ''', [cutoff_date]).fetchall()

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
        "pathways": [{"pathway": row[0], "count": row[1]} for row in (pathway_stats or [])],
        "member_statuses": [{"status": row[0], "count": row[1]} for row in (status_stats or [])],
        "daily_rollup_et": [
          {"date_et": str(row[0]), "calls": row[1], "avg_duration_seconds": row[2] or 0}
          for row in (daily_rollup_et or [])
        ],
        "timezone_reporting": "ET (UTC-5 for current period)",
        "source_dataset": "Datasets/vibe-pill-calls/data.duckdb"
    }
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;

    const proc = Bun.spawn(["python3", "-c", analyticsScript], {
      stdin: "pipe", stdout: "pipe", stderr: "pipe"
    });
    proc.stdin.write(JSON.stringify({ db: DB_PATH, days }));
    proc.stdin.end();

    const result = await new Response(proc.stdout).text();
    await proc.exited;

    try { return JSON.parse(result.trim()); }
    catch { return { error: "Failed to generate analytics" }; }
  } catch (error: any) {
    return { error: error.message };
  }
}

export async function getPendingEscalations(): Promise<any[]> {
  try {
    const script = `
import duckdb
import json
import sys

try:
    data = json.loads(sys.stdin.read())
    con = duckdb.connect(data['db'])
    rows = con.execute('''
      SELECT id, call_id, name, contact, reason, created_at
      FROM escalations ORDER BY created_at DESC LIMIT 50
    ''').fetchall()
    con.close()
    result = [{"id": r[0], "call_id": r[1], "name": r[2], "contact": r[3], "reason": r[4], "created_at": r[5]} for r in rows]
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;

    const proc = Bun.spawn(["python3", "-c", script], {
      stdin: "pipe", stdout: "pipe", stderr: "pipe"
    });
    proc.stdin.write(JSON.stringify({ db: DB_PATH }));
    proc.stdin.end();

    const result = await new Response(proc.stdout).text();
    await proc.exited;

    try { return JSON.parse(result.trim()); }
    catch { return []; }
  } catch {
    return [];
  }
}

export async function healthCheck(): Promise<{ status: string; details: any }> {
  try {
    if (!existsSync(DB_PATH)) {
      return { status: "error", details: "Database file not found" };
    }

    const script = `
import duckdb
import json

try:
    con = duckdb.connect("${DB_PATH}")
    tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
    call_count = con.execute("SELECT COUNT(*) FROM calls").fetchone()[0] if 'calls' in tables else 0
    member_count = con.execute("SELECT COUNT(*) FROM member_profiles").fetchone()[0] if 'member_profiles' in tables else 0
    app_count = con.execute("SELECT COUNT(*) FROM applications").fetchone()[0] if 'applications' in tables else 0
    con.close()
    print(json.dumps({"database_exists": True, "tables": tables, "call_count": call_count, "member_count": member_count, "application_count": app_count, "status": "healthy"}))
except Exception as e:
    print(json.dumps({"error": str(e), "status": "error"}))
`;

    const proc = Bun.spawn(["python3", "-c", script], { stdout: "pipe", stderr: "pipe" });
    const result = await new Response(proc.stdout).text();
    await proc.exited;

    try {
      const parsed = JSON.parse(result.trim());
      return { status: parsed.status || "unknown", details: parsed };
    } catch {
      return { status: "error", details: { error: "Failed to parse health check" } };
    }
  } catch (error: any) {
    return { status: "error", details: { error: error.message } };
  }
}

if (import.meta.main) {
  const args = process.argv.slice(2);
  const command = args[0];

  switch (command) {
    case "health":
      console.log(JSON.stringify(await healthCheck(), null, 2));
      break;
    case "analytics":
      console.log(JSON.stringify(await getCallAnalytics(parseInt(args[1]) || 30), null, 2));
      break;
    case "escalations":
      console.log(JSON.stringify(await getPendingEscalations(), null, 2));
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
