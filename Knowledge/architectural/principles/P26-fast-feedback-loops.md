# P26: Fast Feedback Loops

**Category:** Operations  
**Priority:** High  
**Related:** P7 (Dry-Run), P18 (Verify State), P19 (Error Handling)

---

## Principle

**Design systems for immediate feedback. The faster you see results, the faster you can iterate.**

Optimize for the speed between "action" and "outcome." Fast feedback maintains flow state, enables rapid iteration, and catches errors early. Slow feedback kills momentum and compounds mistakes.

---

## The Problem

**Slow feedback destroys productivity:**

**Example 1: Deploy-to-test cycle**
- Make change
- Commit to git
- Push to server
- Wait for deploy (5 min)
- Test in production
- Discover bug
- **15 minutes per iteration**
- 4 iterations to fix = **1 hour**

**Example 2: Fast local testing**
- Make change
- Run locally (5 seconds)
- See result immediately
- Fix bug
- **30 seconds per iteration**
- 4 iterations to fix = **2 minutes**

**30x speed difference** from feedback loop design alone.

---

## Recognition

**Slow feedback indicators:**
- Waiting >30 seconds between action and result
- Manual steps required to test changes
- Can't test locally (requires deployment)
- Long-running operations without progress updates
- Errors discovered late in process

**Fast feedback indicators:**
- See results in <10 seconds
- One command to test (`python script.py`)
- Local testing possible
- Progress bars for long operations
- Errors caught immediately

---

## Application

### Script Design for Fast Feedback

**Bad: Slow feedback**
```python
# Takes 5 minutes to run, no output until end
def process_all_records():
    records = load_records()  # 1000+ records
    for record in records:
        process(record)
    save_results()
    print("Done!")  # First output after 5 minutes
```

**Good: Fast feedback**
```python
def process_all_records():
    records = load_records()
    total = len(records)
    
    for i, record in enumerate(records, 1):
        logger.info(f"Processing {i}/{total}: {record['name']}")
        process(record)
        
        # Incremental saving
        if i % 100 == 0:
            save_checkpoint()
            logger.info(f"✓ Checkpoint: {i}/{total} complete")
    
    save_results()
    logger.info("✓ Complete!")
```

**Benefits:**
- See progress immediately
- Know it's working (not hung)
- Can estimate time remaining
- Early error detection

---

### Development Workflow for Fast Feedback

**Slow workflow:**
```bash
# Edit code
vim script.py

# Commit
git add script.py
git commit -m "test"

# Deploy
git push
ssh server "cd /app && git pull && systemctl restart service"

# Wait 5 minutes

# Check logs
ssh server "tail -f /var/log/app.log"

# Discover error, repeat
# Total: 15+ minutes per iteration
```

**Fast workflow:**
```bash
# Edit code
vim script.py

# Test locally immediately
python3 script.py --dry-run

# See result in 5 seconds
# Fix errors, iterate rapidly
# Total: 30 seconds per iteration

# Only deploy when locally validated
git add script.py && git commit -m "tested locally" && git push
```

---

### Testing for Fast Feedback

**Principle: Test smallest unit possible**

```python
# Bad: Test entire system
def test_full_pipeline():
    # Loads 1000 records, processes all, checks output
    # Takes 2 minutes to run
    result = run_full_pipeline()
    assert result.success
```

**Good: Test isolated functions**
```python
# Test one function with one input
def test_parse_record():
    # Takes 0.01 seconds
    input_data = {"name": "test", "value": 42}
    result = parse_record(input_data)
    assert result["name"] == "test"
    assert result["value"] == 42

# Run 100 tests in 1 second
# Immediate feedback on what broke
```

---

### User-Facing Operations

**For long-running tasks:**

```python
import logging
from tqdm import tqdm

def process_large_dataset(records):
    logger.info(f"Processing {len(records)} records...")
    
    # Progress bar for user feedback
    for record in tqdm(records, desc="Processing"):
        process(record)
    
    logger.info("✓ Complete")
```

**Output:**
```
2025-10-26 19:15:00Z INFO Processing 1000 records...
Processing: 100%|███████████| 1000/1000 [00:42<00:00, 23.8 records/s]
2025-10-26 19:15:42Z INFO ✓ Complete
```

**User experience:**
- Knows operation started
- Sees real-time progress
- Can estimate completion time
- Immediate confidence vs. anxiety

---

## Hierarchy of Feedback Speed

**Instant (<1s):** Ideal for development iteration
- Syntax checking
- Linting
- Unit tests on single functions
- Local script execution

**Fast (<10s):** Acceptable for testing
- Integration tests
- Local database queries
- File operations on small datasets

**Moderate (<60s):** Tolerable for validation
- Full test suites
- Processing medium datasets
- Building documentation

**Slow (>60s):** Requires justification
- Large data processing (add progress bars)
- Network operations (cache when possible)
- Deployment (minimize frequency)

**Critical: Any operation >60s MUST show progress.**

---

## Integration with Other Principles

**With P7 (Dry-Run):**
- Dry-run enables fast feedback without side effects
- Test logic immediately without waiting for real execution

**With P18 (Verify State):**
- Fast verification enables rapid iteration
- Slow verification delays error detection

**With P19 (Error Handling):**
- Fail fast = faster feedback
- Early errors prevent wasted time on doomed operations

---

## Anti-Patterns

❌ **No output until completion:** User doesn't know if it's working  
❌ **Testing in production:** Deploy-to-test is slowest possible feedback  
❌ **Long-running tests:** >10s tests discourage frequent testing  
❌ **Manual verification steps:** Every manual step slows feedback  

---

## Tools for Fast Feedback

**Development:**
- `--dry-run` flags
- `watch` command for auto-rerun
- Local testing before deployment
- Hot-reload development servers

**Progress visibility:**
- `logging` module (structured output)
- `tqdm` (progress bars)
- Incremental checkpoints
- Real-time status updates

**Testing:**
- `pytest` with selective test runs
- Unit tests (<0.1s each)
- Mock external dependencies
- Fast test data fixtures

---

## Verification

**Before shipping:**
- [ ] Can test locally without deployment
- [ ] Operations >10s show progress
- [ ] Errors appear immediately, not at end
- [ ] Logs show real-time status
- [ ] One command to run and verify

**Quality check:**
- Time from "change code" to "see result" < 30 seconds?
- If yes: good feedback loop ✓
- If no: identify bottleneck, optimize

---

## Source

From Ben Guo's velocity coding talk: "The hierarchy of slowdowns—immediate feedback is critical for flow state and rapid iteration."

---

**Created:** 2025-10-26  
**Version:** 1.0
