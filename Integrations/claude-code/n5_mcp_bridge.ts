import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { execSync, spawn } from "child_process";
import { ProtectionChecker } from "./protection_checker.js";

// Initialize native TypeScript protection checker (WS3 optimization)
const protectionChecker = new ProtectionChecker();

/**
 * N5-Bridge MCP Server
 * Acts as a translator between Claude Code and N5OS core tools.
 */

const server = new Server(
  {
    name: "n5-bridge",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const TOOLS = [
  {
    name: "n5_protect_check",
    description: "Check if a path is protected by N5 safety rules.",
    inputSchema: {
      type: "object",
      properties: {
        path: { type: "string" },
      },
      required: ["path"],
    },
  },
  {
    name: "n5_log_bio",
    description: "Log a bio-reply (emoji/food) to the N5 health system.",
    inputSchema: {
      type: "object",
      properties: {
        message: { type: "string" },
      },
      required: ["message"],
    },
  },
  {
    name: "n5_close_conversation",
    description: "Trigger the N5 conversation-close workflow for the current session.",
    inputSchema: {
      type: "object",
      properties: {
        summary: { type: "string", description: "Summary of work completed." },
      },
      required: ["summary"],
    },
  },
];

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: TOOLS,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "n5_protect_check": {
        // WS3 optimization: Use native TypeScript checker instead of Python subprocess
        // Performance: 300ms (Python) -> <1ms (TypeScript + cache)
        const targetPath = args?.path as string;
        const result = protectionChecker.isProtected(targetPath);
        const formattedResult = protectionChecker.formatResult(result, targetPath);
        return { content: [{ type: "text", text: formattedResult }] };
      }
      case "n5_log_bio": {
        const msg = args?.message as string;
        const result = execSync(`python3 /home/workspace/N5/scripts/log_bio_reply.py "${msg}"`).toString();
        return { content: [{ type: "text", text: result }] };
      }
      case "n5_close_conversation": {
        // WS3 optimization: Use async mode for non-blocking session close
        // Performance: 30s blocking -> <100ms (local log + background API call)
        const summary = args?.summary as string;
        // Escape quotes in summary for shell safety
        const escapedSummary = summary.replace(/"/g, '\\"');
        const result = execSync(
          `python3 /home/workspace/N5/scripts/close_convo_bridge.py --summary "${escapedSummary}" --async`
        ).toString();
        return { content: [{ type: "text", text: result }] };
      }
      default:
        throw new Error(`Tool not found: ${name}`);
    }
  } catch (error: any) {
    return {
      isError: true,
      content: [{ type: "text", text: error.message }],
    };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});

