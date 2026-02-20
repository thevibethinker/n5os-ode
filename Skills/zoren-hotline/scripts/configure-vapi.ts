#!/usr/bin/env bun

const VAPI_API_KEY = process.env.VAPI_API_KEY;
const VAPI_BASE_URL = "https://api.vapi.ai";

if (!VAPI_API_KEY) {
  console.error("Error: VAPI_API_KEY environment variable not set");
  process.exit(1);
}

const ZOREN_PHONE_NUMBER_ID = "79741023-6e14-436f-ab85-63d540ac8211";
const ZOREN_PHONE_NUMBER = "+14153408017";

async function vapiRequest(endpoint: string, options: RequestInit = {}) {
  const response = await fetch(`${VAPI_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Authorization": `Bearer ${VAPI_API_KEY}`,
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Vapi API error: ${response.status} - ${error}`);
  }

  return response.json();
}

async function configurePhoneNumber(webhookUrl: string, secret?: string) {
  console.log(`Configuring phone number ${ZOREN_PHONE_NUMBER} → ${webhookUrl}`);

  const serverConfig: any = {
    url: webhookUrl,
    timeoutSeconds: 20,
  };

  if (secret) {
    serverConfig.headers = {
      "X-Vapi-Secret": secret,
    };
  }

  const result = await vapiRequest(`/phone-number/${ZOREN_PHONE_NUMBER_ID}`, {
    method: "PATCH",
    body: JSON.stringify({
      name: "Zøren — The Vibe Pill",
      server: serverConfig,
    }),
  });

  console.log("Phone number configured:", JSON.stringify(result, null, 2));
  return result;
}

async function getPhoneNumber() {
  const result = await vapiRequest(`/phone-number/${ZOREN_PHONE_NUMBER_ID}`);
  console.log("Phone number status:", JSON.stringify(result, null, 2));
  return result;
}

async function listPhoneNumbers() {
  const numbers = await vapiRequest("/phone-number");
  console.log("All phone numbers:", JSON.stringify(numbers, null, 2));
  return numbers;
}

async function testWebhook(webhookUrl: string) {
  console.log(`Testing webhook at ${webhookUrl}...`);
  try {
    const healthResp = await fetch(`${webhookUrl}/health`);
    if (healthResp.ok) {
      const health = await healthResp.json();
      console.log("Health check:", JSON.stringify(health, null, 2));
    } else {
      console.warn(`Health check returned ${healthResp.status}`);
    }

    const assistantResp = await fetch(webhookUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: {
          type: "assistant-request",
          call: { customer: { number: "+15551234567" } }
        }
      })
    });

    if (assistantResp.ok) {
      const config = await assistantResp.json();
      const assistant = config.assistant;
      console.log("\n✅ Assistant config returned successfully:");
      console.log(`  Name: ${assistant?.name}`);
      console.log(`  Voice: ${assistant?.voice?.provider} (${assistant?.voice?.voiceId})`);
      console.log(`  Model: ${assistant?.model?.model}`);
      console.log(`  Tools: ${assistant?.model?.tools?.length || 0}`);

      const toolNames = assistant?.model?.tools?.map((t: any) => t.function?.name).filter(Boolean);
      if (toolNames?.length) {
        console.log(`  Tool names: ${toolNames.join(", ")}`);
      }

      const keywords = assistant?.transcriber?.keywords || [];
      const badKeywords = keywords.filter((k: string) => k.split(":")[0].includes(" "));
      if (badKeywords.length > 0) {
        console.error(`  ❌ BAD KEYWORDS (contain spaces): ${badKeywords.join(", ")}`);
      } else {
        console.log(`  ✅ Keywords: ${keywords.length} (all valid)`);
      }

      const analysisPlan = assistant?.analysisPlan || {};
      if (analysisPlan.summaryPrompt) {
        console.log("  ✅ Analysis plan: FLAT format (correct)");
      } else if (analysisPlan.summaryPlan) {
        console.error("  ❌ Analysis plan: NESTED format (will fail)");
      }
    } else {
      console.error(`Assistant request test failed: ${assistantResp.status}`);
    }
  } catch (error) {
    console.error("Webhook test failed:", error);
  }
}

const command = process.argv[2];
const arg1 = process.argv[3];
const arg2 = process.argv[4];

switch (command) {
  case "configure":
    if (!arg1) {
      console.error("Usage: bun configure-vapi.ts configure <webhook-url> [secret]");
      process.exit(1);
    }
    await configurePhoneNumber(arg1, arg2);
    break;
  case "status":
    await getPhoneNumber();
    break;
  case "list":
    await listPhoneNumbers();
    break;
  case "test":
    if (!arg1) {
      console.error("Usage: bun configure-vapi.ts test <webhook-url>");
      process.exit(1);
    }
    await testWebhook(arg1);
    break;
  case "full-setup": {
    if (!arg1) {
      console.error("Usage: bun configure-vapi.ts full-setup <webhook-url> [secret]");
      process.exit(1);
    }
    console.log("=== Step 1: Test webhook ===");
    await testWebhook(arg1);
    console.log("\n=== Step 2: Configure phone number ===");
    await configurePhoneNumber(arg1, arg2);
    console.log("\n=== Step 3: Verify configuration ===");
    await getPhoneNumber();
    console.log("\n✅ Full setup complete. Call (415) 340-8017 to test.");
    break;
  }
  default:
    console.log(`Usage:
  bun configure-vapi.ts configure <webhook-url> [secret]  - Point Zøren phone to webhook
  bun configure-vapi.ts status                             - Check current phone config
  bun configure-vapi.ts list                               - List all VAPI phone numbers
  bun configure-vapi.ts test <webhook-url>                 - Test webhook response
  bun configure-vapi.ts full-setup <webhook-url> [secret]  - Test + configure + verify`);
}
