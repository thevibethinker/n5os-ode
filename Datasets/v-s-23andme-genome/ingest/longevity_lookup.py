import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data.duckdb"

# Master list of validated high-signal SNPs for longevity, cognitive focus, and metabolic health
# Derived from Scientific Reports (2025), Nature Communications (2017), and npj Aging (2024)
TARGET_SNPS = [
    # --- LONGEVITY MASTER SWITCHES ---
    {"rsid": "rs7412", "gene": "APOE", "trait": "Longevity Limit", "risk_allele": "C", "benefit": "T is protective; C limits extreme lifespan"},
    {"rsid": "rs429358", "gene": "APOE", "trait": "Alzheimer's/Lifespan", "risk_allele": "C", "benefit": "T is ancestral/protective; C increases risk"},
    {"rsid": "rs2802292", "gene": "FOXO3", "trait": "Cellular Resilience", "risk_allele": "T", "benefit": "G is the 'longevity' allele; slower telomere aging"},
    {"rsid": "rs12206094", "gene": "FOXO3", "trait": "Stress Response", "risk_allele": "C", "benefit": "T is associated with survival >95 years"},
    
    # --- COGNITIVE & BRAIN HEALTH ---
    {"rsid": "rs6265", "gene": "BDNF", "trait": "Neuroplasticity", "risk_allele": "A", "benefit": "G (Val) is standard; A (Met) may affect brain-derived neurotrophic factor"},
    {"rsid": "rs4680", "gene": "COMT", "trait": "Executive Function", "risk_allele": "G", "benefit": "A (Met) = higher dopamine/focus; G (Val) = faster clearance/stress resilience"},
    {"rsid": "rs1800497", "gene": "DRD2", "trait": "Dopamine Receptor", "risk_allele": "A", "benefit": "T is common; A (Ankk1) may reduce D2 density"},
    
    # --- METABOLIC & LIFESTYLE ---
    {"rsid": "rs762551", "gene": "CYP1A2", "trait": "Caffeine Metabolism", "risk_allele": "C", "benefit": "A is fast metabolizer; C is slow"},
    {"rsid": "rs497849", "gene": "SIRT1", "trait": "Sirtuin Activation", "risk_allele": "A", "benefit": "T often linked to improved metabolic response to fasting"},
    {"rsid": "rs1801282", "gene": "PPARG", "trait": "Insulin Sensitivity", "risk_allele": "C", "benefit": "G (Ala) associated with higher insulin sensitivity"},
    {"rsid": "rs9939609", "gene": "FTO", "trait": "Adiposity/Appetite", "risk_allele": "A", "benefit": "T is protective; A linked to higher BMI/hunger"},
]

def analyze():
    con = duckdb.connect(str(DB_PATH))
    
    # Extract just the RSIDs for the query
    rsids = [s["rsid"] for s in TARGET_SNPS]
    
    # Query database
    query = f"SELECT rsid, genotype FROM snps WHERE rsid IN ({str(rsids)[1:-1]})"
    results = con.execute(query).df()
    
    # Merge with target info
    df_targets = pd.DataFrame(TARGET_SNPS)
    merged = pd.merge(df_targets, results, on="rsid", how="left")
    
    # Characterize result
    def characterize(row):
        if pd.isna(row['genotype']):
            return "Not found in dataset"
        
        # Simple allele check
        has_risk = row['risk_allele'] in row['genotype']
        is_homozygous_risk = row['genotype'] == row['risk_allele'] * 2
        
        if is_homozygous_risk:
            return "Homozygous Risk"
        elif has_risk:
            return "Heterozygous (Carrier)"
        else:
            return "Protective/Standard"

    merged['status'] = merged.apply(characterize, axis=1)
    
    print(merged[['gene', 'rsid', 'trait', 'genotype', 'status', 'benefit']].to_markdown(index=False))
    
    con.close()

if __name__ == "__main__":
    analyze()
