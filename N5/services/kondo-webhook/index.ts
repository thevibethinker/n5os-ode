/**
 * Kondo LinkedIn Webhook Receiver
 * 
 * Receives LinkedIn conversation data from Kondo and stores it in SQLite.
 * Validates API key, parses payload, stores conversations + messages.
 * 
 * Version: 2.0.0
 * Created: 2025-10-30
 * Updated: 2025-12-10 - Added connected_at, kondo_note, starred, headline, location, picture
 */

import { Hono } from 'hono';
import { Database } from 'bun:sqlite';
import { readFileSync, existsSync, writeFileSync } from 'fs';

const app = new Hono();

// Configuration
const DB_PATH = '/home/workspace/Knowledge/linkedin/linkedin.db';
const API_KEY_PATH = '/home/workspace/N5/config/secrets/kondo_webhook_key.txt';
const PORT = 8765;

// Load API key
let WEBHOOK_API_KEY: string | null = null;
if (existsSync(API_KEY_PATH)) {
  WEBHOOK_API_KEY = readFileSync(API_KEY_PATH, 'utf-8').trim();
  console.log('✅ API key loaded');
} else {
  console.warn('⚠️  No API key found. Webhook will accept all requests.');
}

// Database connection
const db = new Database(DB_PATH);

// Helper: Validate API key
function validateApiKey(request: Request): boolean {
  if (!WEBHOOK_API_KEY) return true;
  const providedKey = request.headers.get('x-api-key');
  return providedKey === WEBHOOK_API_KEY;
}

// Helper: Log processing event
function logProcessing(eventType: string, eventData: any, status: string, errorMessage?: string, durationMs?: number) {
  const stmt = db.prepare(`
    INSERT INTO processing_log (event_type, event_data, status, error_message, duration_ms)
    VALUES (?, ?, ?, ?, ?)
  `);
  stmt.run(eventType, JSON.stringify(eventData), status, errorMessage || null, durationMs || null);
}

// Helper: Store conversation
function storeConversation(conversationId: string, payload: any): { stored: number; errors: string[] } {
  const errors: string[] = [];
  let storedMessages = 0;
  
  try {
    const data = payload.data || {};
    
    // Extract contact info
    const participantName = `${data.contact_first_name || ''} ${data.contact_last_name || ''}`.trim() || 'Unknown';
    const participantEmail = data.contact_email || null;
    const participantProfileUrl = data.contact_linkedin_url || null;
    const participantHandle = data.contact_linkedin_handle || null;
    
    // NEW: Extract enriched contact data
    const connectedAt = data.contact_connected_at ? 
      new Date(data.contact_connected_at).getTime() : null;
    const contactHeadline = data.contact_headline || null;
    const contactLocation = data.contact_location || null;
    const contactPicture = data.contact_picture || null;
    const kondoNote = data.kondo_note || null;
    const starred = data.conversation_starred ? 1 : 0;
    
    // Extract conversation metadata
    const latestMessageContent = data.conversation_latest_content || '';
    const latestMessageTimestamp = data.conversation_latest_timestamp ? 
      new Date(data.conversation_latest_timestamp).getTime() : Date.now();
    
    // Determine status
    const conversationStatus = data.conversation_status || '';
    const status = conversationStatus.includes('waiting_for_my_reply') || 
                   conversationStatus.includes('waiting_for_reply') ? 
                   'PENDING_RESPONSE' : 'ACTIVE';
    
    // Determine who sent the last message
    const lastMessageFrom = status === 'PENDING_RESPONSE' ? 'them' : 'me';
    
    if (!latestMessageContent) {
      errors.push('No message content in payload');
      return { stored: 0, errors };
    }
    
    // Upsert conversation with all enriched fields
    const upsertConv = db.prepare(`
      INSERT INTO conversations (
        id, linkedin_profile_url, participant_name, participant_email,
        first_message_at, last_message_at, last_message_from, message_count,
        status, metadata, updated_at,
        connected_at, kondo_note, starred, contact_headline, contact_location, contact_picture_url
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(id) DO UPDATE SET
        last_message_at = excluded.last_message_at,
        last_message_from = excluded.last_message_from,
        message_count = conversations.message_count + 1,
        status = excluded.status,
        participant_name = excluded.participant_name,
        participant_email = COALESCE(excluded.participant_email, conversations.participant_email),
        updated_at = excluded.updated_at,
        connected_at = COALESCE(excluded.connected_at, conversations.connected_at),
        kondo_note = COALESCE(excluded.kondo_note, conversations.kondo_note),
        starred = excluded.starred,
        contact_headline = COALESCE(excluded.contact_headline, conversations.contact_headline),
        contact_location = COALESCE(excluded.contact_location, conversations.contact_location),
        contact_picture_url = COALESCE(excluded.contact_picture_url, conversations.contact_picture_url),
        metadata = excluded.metadata
    `);
    
    const metadata = JSON.stringify({
      workspace: payload.event?.workspace,
      linkedin_handle: participantHandle,
      linkedin_uid: data.contact_linkedin_uid,
      kondo_url: data.kondo_url,
      kondo_labels: data.kondo_labels,
      conversation_state: data.conversation_state,
      connected_by: data.contact_connected_by
    });
    
    upsertConv.run(
      conversationId,
      participantProfileUrl,
      participantName,
      participantEmail,
      latestMessageTimestamp, // first_message_at (will be preserved if exists due to ON CONFLICT)
      latestMessageTimestamp, // last_message_at
      lastMessageFrom,
      1, // message_count
      status,
      metadata,
      Date.now(),
      connectedAt,
      kondoNote,
      starred,
      contactHeadline,
      contactLocation,
      contactPicture
    );
    
    // Store the latest message
    const messageId = `msg_${conversationId}_${latestMessageTimestamp}`;
    const insertMsg = db.prepare(`
      INSERT INTO messages (
        conversation_id, message_id, sender, sender_profile_url,
        content, sent_at, commitment_extraction_needed, metadata
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT DO NOTHING
    `);
    
    insertMsg.run(
      conversationId,
      messageId,
      participantName,
      participantProfileUrl,
      latestMessageContent,
      latestMessageTimestamp,
      1, // needs extraction
      JSON.stringify({ from_kondo: true })
    );
    
    storedMessages = 1;
    
    // Log enriched data captured
    console.log(`📊 Enriched: connected=${connectedAt ? 'yes' : 'no'}, headline=${contactHeadline ? 'yes' : 'no'}, note=${kondoNote ? 'yes' : 'no'}, starred=${starred}`);
    
  } catch (error: any) {
    errors.push(`Storage error: ${error.message}`);
  }
  
  return { stored: storedMessages, errors };
}

// After the conversation upsert, add to review queue if no CRM match
const checkAndQueueForReview = (
  conversationId: string,
  participantName: string,
  linkedinUrl: string | null,
  headline: string | null,
  location: string | null,
  messageCount: number,
  lastMessageAt: number
) => {
  // Check if already in queue
  const existing = db.prepare(`
    SELECT id FROM crm_review_queue WHERE conversation_id = ?
  `).get(conversationId);
  
  if (existing) return;
  
  // Check if they have a CRM profile (simple name match)
  // Note: More sophisticated matching happens in the Python sync script
  const cleanName = participantName.replace(/[^\w\s]/g, '').toLowerCase();
  const nameParts = cleanName.split(/\s+/);
  
  if (nameParts.length < 2) return; // Need first + last name
  
  // For now, just add to queue - the Python script does proper CRM matching
  try {
    db.prepare(`
      INSERT OR IGNORE INTO crm_review_queue 
      (conversation_id, participant_name, linkedin_url, headline, location, message_count, last_message_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `).run(conversationId, participantName, linkedinUrl, headline, location, messageCount, lastMessageAt);
  } catch (e) {
    // Ignore duplicates
  }
};

// Routes

app.get('/health', (c) => {
  return c.json({ 
    status: 'healthy',
    service: 'kondo-webhook',
    version: '2.0.0',
    database: existsSync(DB_PATH) ? 'connected' : 'missing',
    apiKey: WEBHOOK_API_KEY ? 'configured' : 'not_configured'
  });
});

app.post('/webhook/kondo', async (c) => {
  const startTime = Date.now();
  
  if (!validateApiKey(c.req.raw)) {
    logProcessing('WEBHOOK_RECEIVED', { error: 'invalid_api_key' }, 'ERROR', 'Invalid API key');
    return c.json({ error: 'Unauthorized' }, 401);
  }
  
  try {
    const payload = await c.req.json();
    
    // DEBUG: Write payload to file
    writeFileSync('/home/workspace/Knowledge/linkedin/debug_payload_latest.json', JSON.stringify(payload, null, 2));
    
    const conversationId = payload.event?._id || 
                          payload.event?.id || 
                          payload.data?.conversation_id ||
                          `conv_${Date.now()}`;
    
    console.log(`📥 Webhook received: ${conversationId}`);

    const result = storeConversation(conversationId, payload);
    const duration = Date.now() - startTime;
    
    logProcessing('WEBHOOK_RECEIVED', {
      conversation_id: conversationId,
      messages_stored: result.stored,
      has_enrichment: true
    }, result.errors.length > 0 ? 'PARTIAL' : 'SUCCESS', result.errors.join('; '), duration);
    
    console.log(`✅ ${result.stored} messages in ${duration}ms`);
    
    return c.json({
      success: true,
      conversation_id: conversationId,
      messages_stored: result.stored,
      errors: result.errors.length > 0 ? result.errors : undefined
    });
    
  } catch (error: any) {
    console.error('❌ Error:', error);
    logProcessing('WEBHOOK_RECEIVED', {}, 'ERROR', error.message, Date.now() - startTime);
    return c.json({ success: false, error: error.message }, 500);
  }
});

app.post('/webhook/test', async (c) => {
  const payload = await c.req.json();
  console.log('🧪 Test:', JSON.stringify(payload, null, 2));
  return c.json({ success: true, message: 'Test received' });
});

app.get('/stats', (c) => {
  try {
    const convCount = db.query('SELECT COUNT(*) as count FROM conversations').get() as any;
    const msgCount = db.query('SELECT COUNT(*) as count FROM messages').get() as any;
    const commitCount = db.query('SELECT COUNT(*) as count FROM commitments').get() as any;
    const pendingCount = db.query(`
      SELECT COUNT(*) as count FROM conversations 
      WHERE status = 'PENDING_RESPONSE'
    `).get() as any;
    const withHeadlineCount = db.query(`
      SELECT COUNT(*) as count FROM conversations 
      WHERE contact_headline IS NOT NULL
    `).get() as any;
    const withConnectedAt = db.query(`
      SELECT COUNT(*) as count FROM conversations 
      WHERE connected_at IS NOT NULL
    `).get() as any;
    
    return c.json({
      conversations: convCount.count,
      messages: msgCount.count,
      commitments: commitCount.count,
      pending_responses: pendingCount.count,
      enrichment: {
        with_headline: withHeadlineCount.count,
        with_connected_at: withConnectedAt.count
      }
    });
  } catch (error: any) {
    return c.json({ error: error.message }, 500);
  }
});

// NEW: Endpoint to get enrichment stats
app.get('/enrichment/:conversationId', (c) => {
  const id = c.req.param('conversationId');
  try {
    const conv = db.query(`
      SELECT 
        participant_name,
        connected_at,
        kondo_note,
        starred,
        contact_headline,
        contact_location,
        contact_picture_url,
        linkedin_profile_url
      FROM conversations 
      WHERE id = ?
    `).get(id) as any;
    
    if (!conv) {
      return c.json({ error: 'Conversation not found' }, 404);
    }
    
    return c.json({
      name: conv.participant_name,
      linkedin_url: conv.linkedin_profile_url,
      connected_at: conv.connected_at ? new Date(conv.connected_at).toISOString() : null,
      headline: conv.contact_headline,
      location: conv.contact_location,
      picture_url: conv.contact_picture_url,
      kondo_note: conv.kondo_note,
      starred: conv.starred === 1
    });
  } catch (error: any) {
    return c.json({ error: error.message }, 500);
  }
});

console.log(`🚀 Kondo webhook service v2.0.0 on port ${PORT}`);
console.log(`📊 Database: ${DB_PATH}`);
console.log(`🔑 API key: ${WEBHOOK_API_KEY ? 'configured' : 'open'}`);
console.log(`✨ Enrichment fields: connected_at, headline, location, picture, kondo_note, starred`);

export default { port: PORT, fetch: app.fetch };


