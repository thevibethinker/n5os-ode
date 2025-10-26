#!/bin/bash
# Productivity Tracker Auto-Scan
# Chains email scan → meeting scan → RPI calculation
# Runs every 30 minutes to keep tracker current

LOG_FILE="/home/workspace/logs/productivity_auto_scan.log"
mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date -Iseconds)] Starting auto scan" >> "$LOG_FILE"

# Scan emails (today only)
echo "[$(date -Iseconds)] Scanning emails..." >> "$LOG_FILE"
python3 /home/workspace/N5/scripts/productivity/email_scanner.py 2>&1 | tee -a "$LOG_FILE"
EMAIL_EXIT=$?

# Scan meetings (today only)
echo "[$(date -Iseconds)] Scanning meetings..." >> "$LOG_FILE"
python3 /home/workspace/N5/scripts/productivity/meeting_scanner.py --date "$(date +%Y-%m-%d)" 2>&1 | tee -a "$LOG_FILE"
MEETING_EXIT=$?

# Recalculate RPI
echo "[$(date -Iseconds)] Recalculating RPI..." >> "$LOG_FILE"
python3 /home/workspace/N5/scripts/productivity/rpi_calculator.py 2>&1 | tee -a "$LOG_FILE"
RPI_EXIT=$?

# Summary
echo "[$(date -Iseconds)] Auto scan complete (Email: $EMAIL_EXIT, Meeting: $MEETING_EXIT, RPI: $RPI_EXIT)" >> "$LOG_FILE"

# Exit with failure if any component failed
if [ $EMAIL_EXIT -ne 0 ] || [ $MEETING_EXIT -ne 0 ] || [ $RPI_EXIT -ne 0 ]; then
    echo "[$(date -Iseconds)] ERROR: One or more components failed" >> "$LOG_FILE"
    exit 1
fi

exit 0
