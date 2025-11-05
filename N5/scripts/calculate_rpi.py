#!/usr/bin/env python3
import sqlite3
import json
from datetime import datetime
from pathlib import Path

def calculate_rpi():
    """
    Calculate Relational Productivity Index (RPI) based on:
    - Outreach volume (prospect_outreach + partner_communication)
    - Response rates (estimated from internal/client communication)
    - Relationship development activities
    """
    
    db_path = Path("/home/workspace/N5/data/productivity_tracker.db")
    
    if not db_path.exists():
        print("Error: Database not found")
        return None
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Query today's emails by category
    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM emails 
        WHERE DATE(date) = ?
        GROUP BY category
    """, (today,))
    
    categories = dict(cursor.fetchall())
    
    # Calculate RPI components
    prospect_outreach = categories.get("prospect_outreach", 0)
    partner_communication = categories.get("partner_communication", 0)
    client_communication = categories.get("client_communication", 0)
    internal_communication = categories.get("internal", 0)
    other = categories.get("other", 0)
    
    total_emails = sum(categories.values())
    
    # RPI Scoring Algorithm
    # Outreach volume: 30 points max (prospect + partner)
    outreach_score = min((prospect_outreach + partner_communication) * 2.5, 30)
    
    # Response engagement: 25 points max (client + internal communication)
    response_score = min((client_communication + internal_communication) * 2, 25)
    
    # Relationship quality: 20 points (partner communication as % of total)
    relationship_ratio = partner_communication / total_emails if total_emails > 0 else 0
    relationship_score = relationship_ratio * 20
    
    # Consistency: 25 points (base score for any activity)
    consistency_score = 25 if total_emails > 0 else 0
    
    # Calculate total RPI (0-100 scale)
    rpi_score = outreach_score + response_score + relationship_score + consistency_score
    rpi_score = min(rpi_score, 100)  # Cap at 100
    
    conn.close()
    
    return {
        "date": today,
        "emails_sent": total_emails,
        "rpi_score": round(rpi_score, 2),
        "categories": {
            "prospect_outreach": prospect_outreach,
            "client_communication": client_communication,
            "partner_communication": partner_communication,
            "internal": internal_communication,
            "other": other
        },
        "breakdown": {
            "outreach_score": round(outreach_score, 2),
            "response_score": round(response_score, 2),
            "relationship_score": round(relationship_score, 2),
            "consistency_score": round(consistency_score, 2)
        }
    }

if __name__ == "__main__":
    result = calculate_rpi()
    if result:
        print(json.dumps(result, indent=2))
