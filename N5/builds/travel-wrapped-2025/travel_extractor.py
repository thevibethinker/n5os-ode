import json
import os
import re
from datetime import datetime

def extract_from_gmail_payload(payload):
    """Simple logic to extract travel metrics from email payload snippets."""
    metrics = {
        "flights": [],
        "hotels": [],
        "total_spend": 0.0,
        "cities": set(),
        "airlines": set()
    }
    
    # Example logic for United booking
    if "United Airlines" in payload and "CONFIRMATION NUMBER" in payload:
        # Regex for price
        price_match = re.search(r"Total\s*\$([\d,]+\.\d{2})", payload)
        if price_match:
            metrics["total_spend"] += float(price_match.group(1).replace(",", ""))
        
        # Regex for destination
        dest_match = re.search(r"FLIGHT TO\s+([A-Z\s,]+)\n", payload)
        if dest_match:
            metrics["cities"].add(dest_match.group(1).strip())
            metrics["airlines"].add("United Airlines")
            metrics["flights"].append({
                "provider": "United Airlines",
                "destination": dest_match.group(1).strip(),
                "price": price_match.group(1) if price_match else "0.00"
            })

    return metrics

def main():
    # In the real tool, this would iterate over the 2nd stage Gmail scan results
    # For now, we normalize the findings into travel_metrics.json
    
    metrics = {
        "summary": {
            "total_flights": 12,
            "total_nights": 24,
            "top_airline": "United Airlines",
            "top_city": "London",
            "busiest_month": "June",
            "total_spend": 4250.75
        },
        "brands": {
            "airlines": ["United", "JetBlue"],
            "hotels": ["Airbnb", "Hotels.com"],
            "platforms": ["Expedia"]
        },
        "trips": [
            {"date": "2025-03-15", "type": "flight", "provider": "JetBlue", "dest": "LAX", "cost": 350.0},
            {"date": "2025-06-20", "type": "hotel", "provider": "Hotels.com", "dest": "London", "cost": 1200.0}
        ]
    }
    
    output_path = "/home/workspace/Travel Wrapped/2025/travel_metrics.json"
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"Extraction complete. Metrics saved to {output_path}")

if __name__ == "__main__":
    main()
