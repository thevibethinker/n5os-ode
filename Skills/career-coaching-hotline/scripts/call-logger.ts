#!/usr/bin/env bun

import { existsSync } from "fs";

const DB_PATH = "/home/workspace/Datasets/career-hotline-calls/data.duckdb";

export function generateUUID(): string {
  return crypto.randomUUID();
}

export async function logCallPattern(data: {
  callId?: string;
  duration?: number;
  topics?: string[];
  stageAssessed?: string;
  escalationRequested?: boolean;
  conceptsExplained?: string[];
}): Promise<boolean> {
  try {
    const callId = data.callId || generateUUID();
    const now = new Date().toISOString();

    const validTopics = [
      "resume", "cover_letter", "linkedin", "job_search", "networking",
      "interview_prep", "career_pivot", "salary_negotiation", "self_reflection",
      "ats_systems", "materials_review", "career_direction", "internship",
      "groundwork", "outreach", "performance", "transition", "escalation",
      "careerspan_inquiry", "general"
    ];

    const sanitizedTopics = data.topics
      ? data.topics.filter(t => validTopics.includes(t)).join(",")
      : "general";

    const insertScript = `
import duckdb, json, sys
try:
    data = json.loads(sys.stdin.read())
    con = duckdb.connect(data['db'])
    con.execute('''
      INSERT OR REPLACE INTO calls
      (id, started_at, ended_at, duration_seconds, topics_discussed,
       stage_assessed, escalation_requested, raw_data)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', [
      data['id'], data['started_at'], data['ended_at'], data['duration'],
      data['topics'], data['stage'], data['escalation'], data['raw']
    ])
    con.close()
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
`;

    const logData = JSON.stringify({
      db: DB_PATH,
      id: callId,
      started_at: now,
      ended_at: now,
      duration: data.duration || 0,
      topics: sanitizedTopics,
      stage: data.stageAssessed || null,
      escalation: data.escalationRequested || false,
      raw: JSON.stringify({
        timestamp: now,
        concepts_explained: data.conceptsExplained || [],
        topics_count: data.topics?.length || 0,
        pattern_type: "career_coaching_call"
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
    console.error("Failed to log call pattern:", result);
    return false;
  } catch (error) {
    console.error("Error in logCallPattern:", error);
    return false;
  }
}

export async function logEscalation(data: {
  name: string;
  contact: string;
  careerStage: string;
  reason: string;
  painPoints?: string[];
  callId?: string;
}): Promise<string | null> {
  try {
    const escalationId = generateUUID();
    const now = new Date().toISOString();

    const insertScript = `
import duckdb, json, sys
try:
    data = json.loads(sys.stdin.read())
    con = duckdb.connect(data['db'])
    con.execute('''
      INSERT INTO escalations (id, call_id, name, contact, career_stage, reason, pain_points, created_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', [
      data['id'], data['call_id'], data['name'], data['contact'],
      data['career_stage'], data['reason'], data['pain_points'], data['created_at']
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
      career_stage: data.careerStage,
      reason: data.reason,
      pain_points: JSON.stringify(data.painPoints || []),
      created_at: now
    });

    const proc = Bun.spawn(["python3", "-c", insertScript], {
      stdin: "pipe", stdout: "pipe", stderr: "pipe"
    });
    proc.stdin.write(escalationData);
    proc.stdin.end();
    const result = await new Response(proc.stdout).text();
    await proc.exited;

    if (result.trim() === "SUCCESS") {
      console.log(`Escalation logged: ${escalationId.substring(0, 8)} for ${data.name}`);
      return escalationId;
    }
    console.error("Failed to log escalation:", result);
    return null;
  } catch (error) {
    console.error("Error in logEscalation:", error);
    return null;
  }
}

export async function getCallAnalytics(days: number = 30): Promise<any> {
  try {
    const analyticsScript = `
import duckdb, json, sys
from datetime import datetime, timedelta
try:
    data = json.loads(sys.stdin.read())
    con = duckdb.connect(data['db'])
    cutoff = (datetime.now() - timedelta(days=data['days'])).isoformat()

    call_stats = con.execute('''
      SELECT COUNT(*) as total, AVG(duration_seconds) as avg_dur,
        MAX(duration_seconds) as max_dur,
        COUNT(CASE WHEN escalation_requested THEN 1 END) as escalations
      FROM calls WHERE started_at > ?
    ''', [cutoff]).fetchone()

    topic_stats = con.execute('''
      SELECT topics_discussed, COUNT(*) as cnt FROM calls
      WHERE started_at > ? AND topics_discussed IS NOT NULL
      GROUP BY topics_discussed ORDER BY cnt DESC
    ''', [cutoff]).fetchall()

    stage_stats = con.execute('''
      SELECT stage_assessed, COUNT(*) as cnt FROM calls
      WHERE started_at > ? AND stage_assessed IS NOT NULL
      GROUP BY stage_assessed ORDER BY cnt DESC
    ''', [cutoff]).fetchall()

    con.close()
    print(json.dumps({
      "period_days": data['days'],
      "call_volume": {
        "total": call_stats[0] or 0,
        "avg_duration_sec": round(call_stats[1] or 0, 1),
        "max_duration_sec": call_stats[2] or 0,
        "escalation_rate": round((call_stats[3] or 0) / max(call_stats[0] or 1, 1) * 100, 1)
      },
      "topics": [{"topic": r[0], "count": r[1]} for r in (topic_stats or [])],
      "stages": [{"stage": r[0], "count": r[1]} for r in (stage_stats or [])]
    }))
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
    catch { return { error: "Failed to parse analytics" }; }
  } catch (error) {
    console.error("Error in getCallAnalytics:", error);
    return { error: (error as Error).message };
  }
}

export async function getPendingEscalations(): Promise<any[]> {
  try {
    const script = `
import duckdb, json, sys
try:
    data = json.loads(sys.stdin.read())
    con = duckdb.connect(data['db'])
    rows = con.execute('''
      SELECT id, call_id, name, contact, career_stage, reason, pain_points, created_at
      FROM escalations ORDER BY created_at DESC LIMIT 50
    ''').fetchall()
    con.close()
    print(json.dumps([{
      "id": r[0], "call_id": r[1], "name": r[2], "contact": r[3],
      "career_stage": r[4], "reason": r[5], "pain_points": r[6], "created_at": r[7]
    } for r in rows]))
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
  } catch (error) {
    console.error("Error in getPendingEscalations:", error);
    return [];
  }
}

export async function healthCheck(): Promise<{ status: string; details: any }> {
  try {
    if (!existsSync(DB_PATH)) {
      return { status: "error", details: "Database file not found" };
    }
    const script = `
import duckdb, json
try:
    con = duckdb.connect("${DB_PATH}")
    tables = [r[0] for r in con.execute("SHOW TABLES").fetchall()]
    call_count = con.execute("SELECT COUNT(*) FROM calls").fetchone()[0] if 'calls' in tables else 0
    esc_count = con.execute("SELECT COUNT(*) FROM escalations").fetchone()[0] if 'escalations' in tables else 0
    fb_count = con.execute("SELECT COUNT(*) FROM feedback").fetchone()[0] if 'feedback' in tables else 0
    con.close()
    print(json.dumps({"database_exists": True, "tables": tables, "call_count": call_count, "escalation_count": esc_count, "feedback_count": fb_count, "status": "healthy"}))
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
  } catch (error) {
    return { status: "error", details: { error: (error as Error).message } };
  }
}

if (import.meta.main) {
  const command = process.argv[2];
  switch (command) {
    case "health": {
      const h = await healthCheck();
      console.log(JSON.stringify(h, null, 2));
      break;
    }
    case "analytics": {
      const days = parseInt(process.argv[3]) || 30;
      const a = await getCallAnalytics(days);
      console.log(JSON.stringify(a, null, 2));
      break;
    }
    case "escalations": {
      const e = await getPendingEscalations();
      console.log(JSON.stringify(e, null, 2));
      break;
    }
    default:
      console.log("Usage: bun call-logger.ts <command>");
      console.log("Commands: health, analytics [days], escalations");
      break;
  }
}
