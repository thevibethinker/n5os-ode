import { readFileSync } from "fs";

const schemaPath = "/home/workspace/N5/schemas/zobridge.schema.json";
const schema = JSON.parse(readFileSync(schemaPath, "utf-8"));

// Load limits from main config
const mainConfigPath = "/home/workspace/N5/config/zobridge.config.json";
const mainConfig = JSON.parse(readFileSync(mainConfigPath, "utf-8"));
const MAX_SIZE = Number(mainConfig.max_message_size_bytes || 102400);

// Read secret from local config file instead of process.env
function getSecret(): string | null {
  try {
    const configPath = "/home/workspace/N5/services/zobridge/zobridge.config.json";
    const localConfig = JSON.parse(readFileSync(configPath, "utf-8"));
    return localConfig.secret || null;
  } catch {
    return process.env.ZOBRIDGE_SECRET || null;
  }
}

export function validateMessage(msg: any): { valid: boolean; errors?: string[] } {
  const errors: string[] = [];

  // Check required fields
  const required = ["message_id", "timestamp", "from", "to", "type", "content"];
  for (const field of required) {
    if (!(field in msg)) {
      errors.push(`Missing required field: ${field}`);
    }
  }

  // Validate message_id format
  if (msg.message_id && !/^(msg|resp_msg)_[0-9]+$/.test(msg.message_id)) {
    errors.push(`Invalid message_id format: ${msg.message_id}`);
  }

  // Validate timestamp format (basic ISO check)
  if (msg.timestamp && isNaN(Date.parse(msg.timestamp))) {
    errors.push(`Invalid timestamp format: ${msg.timestamp}`);
  }

  // Validate from/to values
  const validSystems = ["ParentZo", "ChildZo"];
  if (msg.from && !validSystems.includes(msg.from)) {
    errors.push(`Invalid from value: ${msg.from}`);
  }
  if (msg.to && !validSystems.includes(msg.to)) {
    errors.push(`Invalid to value: ${msg.to}`);
  }

  // Validate type
  const validTypes = ["instruction", "question", "proposal", "response", "feedback", "checkpoint"];
  if (msg.type && !validTypes.includes(msg.type)) {
    errors.push(`Invalid type value: ${msg.type}`);
  }

  // Validate content is an object
  if (msg.content && typeof msg.content !== "object") {
    errors.push("Content must be an object");
  }

  // Check message size (from config)
  const size = JSON.stringify(msg).length;
  if (size > MAX_SIZE) {
    errors.push(`Message too large: ${size} bytes (max ${MAX_SIZE})`);
  }

  return {
    valid: errors.length === 0,
    errors: errors.length > 0 ? errors : undefined,
  };
}

export function validateAuth(authHeader: string | null): boolean {
  if (!authHeader) return false;
  
  const expectedSecret = getSecret();
  if (!expectedSecret) {
    console.warn("ZOBRIDGE_SECRET not set - authentication disabled");
    return true; // Allow for testing
  }

  const parts = authHeader.split(" ");
  if (parts.length !== 2 || parts[0] !== "Bearer") return false;

  return parts[1] === expectedSecret;
}
