# Conversational API Integration Checklist

**For:** N5 Bootstrap Mobius Maneuver  
**System:** AI-to-AI Communication  
**Status:** ✅ Implementation complete

---

## Pre-Bootstrap Checklist

### Parent Workspace Preparation

- [x] Server implemented (`n5_bootstrap_conversational_server.py`)
- [x] Server tested (6/6 tests passed)
- [x] Server running on port 8769
- [x] Health endpoint responding
- [x] Log directory created (`N5/logs/`)
- [x] Conversation log file ready

**Verify server:**
```bash
curl http://localhost:8769/health
ps aux | grep conversational_server
```

### Bootstrap Package Preparation

- [ ] Copy client to package: `bootstrap_conversation_client.py`
- [ ] Copy instructions: `INSTRUCTIONS_FOR_DEMONSTRATOR_AI_CONVERSATION.md`
- [ ] Copy API guide: `AI_TO_AI_CONVERSATION_GUIDE.md`
- [ ] Test package contents
- [ ] Verify demonstrator can access parent IP

**Package files to include:**
```
bootstrap_package/
├── scripts/
│   └── bootstrap_conversation_client.py
├── docs/
│   ├── AI_TO_AI_CONVERSATION_GUIDE.md
│   └── INSTRUCTIONS_FOR_DEMONSTRATOR_AI_CONVERSATION.md
└── ...
```

### Network Setup

- [ ] Confirm parent IP address accessible from demonstrator
- [ ] Verify port 8769 not blocked by firewall
- [ ] Test connection from demonstrator network
- [ ] Document parent IP for demonstrator

**Test from demonstrator:**
```bash
curl http://PARENT_IP:8769/health
```

---

## During Bootstrap Checklist

### Monitoring (Parent)

- [ ] Open log monitoring:
      ```bash
      tail -f /home/workspace/N5/logs/bootstrap_conversations.jsonl
      ```
- [ ] Watch for demonstrator questions
- [ ] Keep response terminal ready

### Question Response Workflow (Parent)

When demonstrator asks question:

1. [ ] See question in log
2. [ ] Review conversation history:
       ```bash
       curl http://localhost:8769/api/converse/history/{conv_id}
       ```
3. [ ] Formulate answer
4. [ ] Submit response:
       ```bash
       curl -X POST http://localhost:8769/api/converse/respond \
         -H "Content-Type: application/json" \
         -d '{"conversation_id": "...", "answer": "..."}'
       ```
5. [ ] Verify demonstrator receives answer (check logs)

### Demonstrator Actions

- [ ] Install dependencies: `pip install requests`
- [ ] Start conversation on bootstrap init
- [ ] Ask questions when stuck/unclear
- [ ] Poll for responses
- [ ] Continue work based on guidance

---

## Post-Bootstrap Checklist

### Validation

- [ ] Review conversation log for issues
- [ ] Count questions asked
- [ ] Measure response times
- [ ] Identify common question patterns
- [ ] Note any unanswered questions

**Review log:**
```bash
# Count conversations
grep '"role": "demonstrator"' N5/logs/bootstrap_conversations.jsonl | wc -l

# Extract questions
grep '"role": "demonstrator"' N5/logs/bootstrap_conversations.jsonl | \
  python3 -c 'import sys, json; [print(json.loads(l)["content"]) for l in sys.stdin]'
```

### Improvement

- [ ] Update instructions based on questions asked
- [ ] Add FAQ for common questions
- [ ] Improve error messages in bootstrap code
- [ ] Consider adding pre-emptive guidance

### Cleanup

- [ ] Archive conversation logs
- [ ] Stop conversational server (if desired)
- [ ] Document lessons learned

---

## Troubleshooting Checklist

### Server Issues

Problem: Server not responding

- [ ] Check if server is running: `ps aux | grep conversational_server`
- [ ] Check port availability: `lsof -i :8769`
- [ ] Restart server: `python3 N5/scripts/n5_bootstrap_conversational_server.py --port 8769`
- [ ] Check server logs

### Connection Issues

Problem: Demonstrator can't reach server

- [ ] Verify parent IP is correct
- [ ] Test network: `ping PARENT_IP`
- [ ] Test port: `nc -zv PARENT_IP 8769`
- [ ] Check firewall rules
- [ ] Try different port

### Question Not Received

Problem: Demonstrator's question not in log

- [ ] Verify conversation was started
- [ ] Check conversation_id is correct
- [ ] Verify request completed (no errors)
- [ ] Check log file permissions
- [ ] Review client debug output

### Response Not Delivered

Problem: Demonstrator not receiving response

- [ ] Verify response was submitted
- [ ] Check conversation_id matches
- [ ] Confirm response in log file
- [ ] Verify demonstrator is polling
- [ ] Check response queue status

---

## Success Metrics

### Quantitative

- [ ] Number of questions asked: _______
- [ ] Number of questions answered: _______
- [ ] Average response time: _______ seconds
- [ ] Bootstrap completion time: _______
- [ ] Errors reduced: _______% 

### Qualitative

- [ ] Demonstrator completed bootstrap without human intervention
- [ ] All questions received clear, actionable answers
- [ ] No blockers required human escalation
- [ ] Conversation flow was smooth
- [ ] Documentation was sufficient

---

## Sign-Off

### Pre-Bootstrap

- [ ] All preparations complete
- [ ] Server running and tested
- [ ] Package ready for demonstrator
- [ ] Network connectivity verified

**Signed:** _________________ **Date:** _______

### Post-Bootstrap

- [ ] Bootstrap completed successfully
- [ ] Conversations logged and reviewed
- [ ] Issues documented
- [ ] Improvements identified

**Signed:** _________________ **Date:** _______

---

## Quick Reference

**Health Check:**
```bash
curl http://localhost:8769/health
```

**Monitor Questions:**
```bash
tail -f /home/workspace/N5/logs/bootstrap_conversations.jsonl | grep demonstrator
```

**Get History:**
```bash
curl http://localhost:8769/api/converse/history/{conv_id} | python3 -m json.tool
```

**Submit Response:**
```bash
curl -X POST http://localhost:8769/api/converse/respond \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "conv_...", "answer": "..."}'
```

---

**Checklist Version:** 1.0  
**Last Updated:** 2025-10-19  
**System:** N5 Bootstrap Conversational API
