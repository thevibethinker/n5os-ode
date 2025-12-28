import sqlite3
import os
import re
from datetime import datetime, timedelta

DB_PATH = "/home/workspace/N5/data/performance.db"
WORKOUTS_DB = "/home/workspace/Personal/Health/workouts.db"

def get_db():
    return sqlite3.connect(DB_PATH)

def extract_metadata_llm(b27_text):
    wpm = 0
    energy = 0
    stress = "Unknown"
    
    wpm_match = re.search(r"(\d+)\s*WPM", b27_text, re.IGNORECASE)
    if not wpm_match:
        wpm_match = re.search(r"Speech Density.*:\s*(\d+)", b27_text, re.IGNORECASE)
    if wpm_match: wpm = float(wpm_match.group(1))
    
    energy_match = re.search(r"Energy Rating.*:\s*([\d\.]+)/10", b27_text, re.IGNORECASE)
    if not energy_match:
        energy_match = re.search(r"Overall Wellness Score.*:\s*([\d\.]+)/10", b27_text, re.IGNORECASE)
    if energy_match: energy = float(energy_match.group(1))
    
    stress_match = re.search(r"Stress Level.*:\s*(.*)", b27_text, re.IGNORECASE)
    if stress_match: stress = stress_match.group(1).strip().split('\n')[0]
    
    return wpm, energy, stress

def auto_ingest_wellness():
    base_dir = "/home/workspace/Personal/Meetings"
    conn = get_db()
    cursor = conn.cursor()
    
    found_files = []
    for root, dirs, files in os.walk(base_dir):
        if "B27_WELLNESS_INDICATORS.md" in files:
            found_files.append(os.path.join(root, "B27_WELLNESS_INDICATORS.md"))
            
    for b27_path in found_files:
        folder_name = os.path.basename(os.path.dirname(b27_path))
        with open(b27_path, 'r') as f:
            content = f.read()
            
        wpm, energy, stress = extract_metadata_llm(content)
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", folder_name)
        meeting_date = date_match.group(1) if date_match else datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("""
            INSERT OR REPLACE INTO meeting_wellness 
            (meeting_date, meeting_folder, b27_path, wpm, energy_rating, stress_level)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (meeting_date, folder_name, os.path.relpath(b27_path, "/home/workspace"), wpm, energy, stress))
        
    conn.commit()
    conn.close()

def generate_weekly_report():
    # First, sync any new B27 files found in meeting folders
    auto_ingest_wellness()
    
    conn = get_db()
    cursor = conn.cursor()
    
    output = []
    output.append("================================================================================")
    output.append("WEEKLY PERFORMANCE INTELLIGENCE DASHBOARD")
    output.append("================================================================================")
    
    # 1. Biometric Overview
    cursor.execute("SELECT AVG(hr_during_avg), MAX(hr_during_max) FROM meeting_hr_correlation")
    avg_hr, max_hr = cursor.fetchone()
    output.append("BIOMETRIC OVERVIEW")
    if avg_hr:
        output.append(f"- Avg Meeting HR: {avg_hr:.1f} bpm")
        output.append(f"- Peak HR (Meetings): {max_hr:.1f} bpm")
    else:
        output.append("- No biometric data synced yet.")

    # 2. Cognitive & Wellness (B27)
    cursor.execute("SELECT AVG(wpm), AVG(energy_rating) FROM meeting_wellness WHERE wpm > 0")
    avg_wpm, avg_energy = cursor.fetchone()
    output.append("\nCOGNITIVE & WELLNESS (B27)")
    if avg_wpm:
        output.append(f"- Avg Speech Density: {avg_wpm:.1f} WPM")
        output.append(f"- Avg Energy Rating: {avg_energy:.1f}/10")
    else:
        output.append("- No wellness data yet.")
        
    # 3. Correlation Insights
    output.append("\nCORRELATION INSIGHTS")
    cursor.execute("""
        SELECT m.event_title, m.activation_level, w.energy_rating, w.stress_level
        FROM meeting_hr_correlation m
        JOIN meeting_wellness w ON 
            REPLACE(m.event_date || '_' || m.event_title, ' ', '-') LIKE '%' || w.meeting_folder || '%'
            OR w.meeting_folder LIKE '%' || REPLACE(m.event_title, ' ', '-') || '%'
    """)
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            title, delta, energy, stress = row
            output.append(f"- [{title}]")
            output.append(f"  Activation: {delta} | Energy: {energy}/10 | Stress: {stress}")
    else:
        output.append("- No correlated insights yet.")

    # 4. Schedule Optimization
    output.append("\nSCHEDULE OPTIMIZATION (PREDICTIVE)")
    try:
        from predictive_scheduler import recommend_slots
        recs_ext = recommend_slots(12) # For High Intensity
        output.append("- High Intensity Window (Top Slot): " + f"{recs_ext[0]['hour']:02d}:00 (Score: {recs_ext[0]['score']}/10)")
        
        recs_solo = recommend_slots(2) # For Low Intensity
        waking_solo = [r for r in recs_solo if 8 <= r['hour'] <= 22]
        output.append("- Deep Work/Solo Window (Top Slot): " + f"{waking_solo[0]['hour']:02d}:00 (Score: {waking_solo[0]['score']}/10)")
    except Exception as e:
        output.append(f"- Recommendation engine error: {e}")

    final_text = "\n".join(output)
    print(final_text)
    
    # Save to file
    report_path = f"/home/workspace/Personal/Health/Reports/Performance_Dashboard_{datetime.now().strftime('%Y-%m-%d')}.md"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(final_text)
    
    conn.close()
    return report_path

if __name__ == "__main__":
    generate_weekly_report()
