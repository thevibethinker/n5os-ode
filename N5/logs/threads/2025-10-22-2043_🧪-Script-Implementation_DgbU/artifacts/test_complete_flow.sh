#!/bin/bash
# Test complete email validation flow end-to-end

set -e

WORKSPACE="/home/workspace"
TEST_DIR="/home/.z/workspaces/con_frSxWyuzF9e9DgbU/flow_test"
MEETING_DIR="$WORKSPACE/N5/records/meetings/2025-10-22_external-brin"

echo "========================================="
echo "Complete Flow Test: Content Library + Validation"
echo "========================================="
echo ""

# Clean up previous test
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"

# STEP 1: Generate email with Content Library
echo "STEP 1: Generating email with Content Library..."
python3 "$WORKSPACE/N5/scripts/n5_follow_up_email_generator.py" \
  --meeting-folder "$MEETING_DIR" \
  --use-content-library \
  --output-dir "$TEST_DIR/generated" \
  --dry-run 2>&1 | tee "$TEST_DIR/step1_generate.log"

# Check if email was generated
if [ ! -f "$TEST_DIR/generated/draft_email.txt" ]; then
  echo "✗ Email generation failed"
  exit 1
fi
echo "✓ Email generated"
echo ""

# STEP 2: Check registry
echo "STEP 2: Checking email registry..."
python3 "$WORKSPACE/N5/scripts/email_registry.py" list 2>&1 | \
  python3 -m json.tool > "$TEST_DIR/step2_registry.json"
echo "✓ Registry check complete"
echo ""

# STEP 3: Simulate sent email (with edits)
echo "STEP 3: Creating simulated sent email with edits..."
cat > "$TEST_DIR/sent_email.txt" << 'EOF'
Hey Brinleigh,

Really enjoyed walking through the Zo setup with you today. Your line about being too busy to hire a Chief of Staff really resonated—that's exactly the paradox this system solves.

Quick recap:

**What we covered:**
- Meeting intelligence pipeline (the $100 one-time setup)
- How it captures context without you lifting a finger
- Why Superhuman teaches better UX than any course

**Next steps:**
- I'll send you an unedited sample output by end of week
- Attaching the Howie trigger words guide
- Once you review, we can finalize and get you set up

**Resources:**

Zo signup with my referral code: https://www.zo.computer/?promo=VATT50

Happy to answer any questions as you dig in. Logan and I are both excited to see what you build with this.

Best,
Vrijen

Vrijen Attawar
CEO & Co-Founder, Careerspan
vrijen@mycareerspan.com
EOF
echo "✓ Sent email created"
echo ""

# STEP 4: Extract corrections
echo "STEP 4: Extracting factual corrections..."
python3 "$WORKSPACE/N5/scripts/email_corrections.py" extract \
  --draft "$TEST_DIR/generated/draft_email.txt" \
  --sent "$TEST_DIR/sent_email.txt" \
  --output "$TEST_DIR/step4_corrections.json" 2>&1 | \
  tee "$TEST_DIR/step4_extract.log"

if [ ! -f "$TEST_DIR/step4_corrections.json" ]; then
  echo "✗ Corrections extraction failed"
  exit 1
fi
echo "✓ Corrections extracted"
echo ""

# STEP 5: Show corrections summary
echo "STEP 5: Corrections Summary"
echo "========================================="
python3 -c "
import json
with open('$TEST_DIR/step4_corrections.json') as f:
    data = json.load(f)
    
print(f'Total Corrections: {data[\"summary\"][\"total_corrections\"]}')
print(f'Auto-apply Ready: {data[\"summary\"][\"auto_apply_ready\"]}')
print(f'Require Review: {data[\"summary\"][\"require_review\"]}')
print()
print('Corrections by Category:')
for category, corrections in data['corrections'].items():
    if corrections:
        print(f'  {category}: {len(corrections)}')
        for c in corrections[:2]:
            print(f'    - {c[\"field\"]}: {c.get(\"description\", \"N/A\")[:60]}...')
" 2>&1 | tee "$TEST_DIR/step5_summary.txt"

echo ""
echo "========================================="
echo "✓ Complete flow test successful"
echo "========================================="
echo ""
echo "Artifacts:"
echo "  - Generated email: $TEST_DIR/generated/draft_email.txt"
echo "  - Sent email: $TEST_DIR/sent_email.txt"
echo "  - Corrections: $TEST_DIR/step4_corrections.json"
echo "  - Full logs: $TEST_DIR/"
