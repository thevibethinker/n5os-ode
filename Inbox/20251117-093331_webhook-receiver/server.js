const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 8900;
const LOG_FILE = path.join(__dirname, 'webhook-logs.jsonl');
const MEETINGS_INBOX_DIR = '/home/workspace/Personal/Meetings/Inbox';

app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Ensure meeting inbox directory exists
if (!fs.existsSync(MEETINGS_INBOX_DIR)) {
  fs.mkdirSync(MEETINGS_INBOX_DIR, { recursive: true });
}

// Log incoming webhook data
function logWebhook(data) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    ...data
  };
  fs.appendFileSync(LOG_FILE, JSON.stringify(logEntry) + '\n');
}

// Sanitize filename
function sanitizeFilename(name) {
  return name.replace(/[^a-z0-9_\-]/gi, '_').toLowerCase();
}

// Format date for filename
function formatDateForFilename(dateString) {
  try {
    const date = new Date(dateString);
    return date.toISOString().split('T')[0]; // YYYY-MM-DD
  } catch (error) {
    return new Date().toISOString().split('T')[0];
  }
}

// Main webhook endpoint
app.post('/webhook', (req, res) => {
  try {
    logWebhook({
      method: req.method,
      headers: req.headers,
      body: req.body,
      query: req.query
    });
    
    console.log(`[${new Date().toISOString()}] Webhook received`);
    
    res.status(200).json({
      success: true,
      message: 'Webhook received successfully',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Error processing webhook:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Zapier/Granola meeting webhook endpoint
app.post('/webhook/zapier/granola', (req, res) => {
  try {
    const payload = req.body;
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    
    console.log(`[${new Date().toISOString()}] Granola webhook received`);
    
    // Validate required fields
    const requiredFields = ['transcript', 'meeting_title', 'meeting_time'];
    for (const field of requiredFields) {
      if (!payload[field]) {
        return res.status(400).json({
          success: false,
          error: `Missing required field: ${field}`
        });
      }
    }
    
    // Generate meeting folder name (YYYY-MM-DD_sanitized_title format)
    const meetingDate = formatDateForFilename(payload.meeting_time);
    const meetingName = payload.calendar_title || payload.meeting_title;
    const sanitizedName = sanitizeFilename(meetingName).substring(0, 80);
    const folderName = `${meetingDate}_${sanitizedName}`;
    const meetingFolder = path.join(MEETINGS_INBOX_DIR, folderName);
    
    // Create meeting folder
    if (!fs.existsSync(meetingFolder)) {
      fs.mkdirSync(meetingFolder, { recursive: true });
    }
    
    // Handle attendees (array or string)
    let attendees = [];
    if (Array.isArray(payload.attendees)) {
      attendees = payload.attendees;
    } else if (typeof payload.attendees === 'string') {
      attendees = payload.attendees.split(',').map(a => a.trim());
    }
    
    // Build transcript.md with essential metadata at the top
    const transcriptHeader = `Meeting Title: ${payload.meeting_title}

Calendar Event ID: ${payload.meeting_id || 'N/A'}

Attendee Emails: ${attendees.join(', ')}

Creator Email: ${payload.creator_email || 'N/A'}

${payload.enhanced_notes ? `Enhanced Notes:\n${payload.enhanced_notes}\n\n` : ''}Transcript:

`;
    
    const transcriptContent = transcriptHeader + payload.transcript;
    const transcriptFile = path.join(meetingFolder, 'transcript.md');
    fs.writeFileSync(transcriptFile, transcriptContent);
    
    // Create _metadata.json with full metadata
    const metadata = {
      meeting_id: payload.meeting_id || `granola_${timestamp}`,
      meeting_title: payload.meeting_title,
      calendar_title: payload.calendar_title,
      meeting_time: payload.meeting_time,
      meeting_date: meetingDate,
      attendees: attendees,
      creator_name: payload.creator_name || 'Unknown',
      creator_email: payload.creator_email || '',
      granola_link: payload.granola_link || '',
      enhanced_notes: payload.enhanced_notes || '',
      source: 'granola_zapier',
      ingested_at: new Date().toISOString(),
      folder_name: folderName,
      transcript_path: transcriptFile
    };
    
    const metadataFile = path.join(meetingFolder, '_metadata.json');
    fs.writeFileSync(metadataFile, JSON.stringify(metadata, null, 2));
    
    // Log the webhook
    logWebhook({
      method: req.method,
      endpoint: '/webhook/zapier/granola',
      meeting_title: payload.meeting_title,
      meeting_time: payload.meeting_time,
      folder_created: meetingFolder,
      timestamp: timestamp
    });
    
    console.log(`[${new Date().toISOString()}] Meeting saved to: ${meetingFolder}`);
    
    res.status(200).json({
      success: true,
      message: 'Meeting received and saved to Inbox',
      meeting_title: payload.meeting_title,
      meeting_time: payload.meeting_time,
      folder_path: meetingFolder,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('Error processing Granola webhook:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// View recent webhooks
app.get('/logs', (req, res) => {
  try {
    if (!fs.existsSync(LOG_FILE)) {
      return res.json({ logs: [] });
    }
    
    const logs = fs.readFileSync(LOG_FILE, 'utf8')
      .split('\n')
      .filter(line => line.trim())
      .map(line => JSON.parse(line))
      .slice(-50); // Last 50 entries
    
    res.json({ logs });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// List recent meeting files
app.get('/meetings', (req, res) => {
  try {
    const folders = fs.readdirSync(MEETINGS_INBOX_DIR)
      .filter(f => {
        const fullPath = path.join(MEETINGS_INBOX_DIR, f);
        return fs.statSync(fullPath).isDirectory() && f.startsWith('2025-');
      })
      .sort()
      .reverse()
      .slice(0, 20);
    
    res.json({
      meetings: folders,
      count: folders.length,
      directory: MEETINGS_INBOX_DIR
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Webhook receiver running on port ${PORT}`);
  console.log(`Webhook endpoint: POST /webhook`);
  console.log(`Granola webhook: POST /webhook/zapier/granola`);
  console.log(`Logs endpoint: GET /logs`);
  console.log(`Health check: GET /health`);
  console.log(`Recent meetings: GET /meetings`);
});





