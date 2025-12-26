from example_enrichment import enrich_stakeholder_profile
import os

if __name__ == "__main__":
    email = "ari@rewiringamerica.org"
    print(f"Enriching {email}...")
    result = enrich_stakeholder_profile(email=email)
    if result:
        print("Enrichment successful.")
    else:
        print("Enrichment failed.")

