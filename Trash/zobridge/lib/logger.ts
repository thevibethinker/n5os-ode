import { appendFileSync } from "fs";
import { readFileSync } from "fs";

const configPath = "/home/workspace/N5/config/zobridge.config.json";
const config = JSON.parse(readFileSync(configPath, "utf-8"));

export function logAudit(event: string, data: any): void {
  const entry = {
    timestamp: new Date().toISOString(),
    event,
    data,
  };
  appendFileSync(config.audit_log_path, JSON.stringify(entry) + "\n");
}

export function logMessage(direction: "received" | "sent", message: any): void {
  logAudit(`message_${direction}`, {
    message_id: message.message_id,
    from: message.from,
    to: message.to,
    type: message.type,
    thread_id: message.thread_id,
  });
}

export function logError(context: string, error: any): void {
  logAudit("error", {
    context,
    error: error.message || String(error),
    stack: error.stack,
  });
}

export function logProcessing(messageId: string, status: string, details?: any): void {
  logAudit("processing", {
    message_id: messageId,
    status,
    details,
  });
}
