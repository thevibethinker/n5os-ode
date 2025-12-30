#!/usr/bin/env python3
"""
Ingest script for 23andMe genome data.
Run with: python ingest.py

This script transforms raw 23andMe genotype exports into a queryable DuckDB database.
"""

import zipfile
from pathlib import Path

import duckdb


# Configuration - paths relative to this script
SCRIPT_DIR = Path(__file__).parent
SOURCE_DIR = SCRIPT_DIR.parent / "source"
DB_PATH = SCRIPT_DIR.parent / "data.duckdb"


def find_genome_file():
    """Find the genome data file, extracting from zip if needed."""
    extracted_dir = SOURCE_DIR / "extracted"

    # Look for txt files directly in source/ first
    txt_files = list(SOURCE_DIR.glob("genome_*.txt"))
    if txt_files:
        return txt_files[0]

    # Look for already extracted txt files
    txt_files = list(extracted_dir.glob("genome_*.txt")) if extracted_dir.exists() else []
    if txt_files:
        return txt_files[0]

    # Look for zip files to extract
    zip_files = list(SOURCE_DIR.glob("genome_*.zip"))
    if not zip_files:
        raise FileNotFoundError(
            f"No 23andMe genome data found in {SOURCE_DIR}. Expected a file like 'genome_*_Full_*.zip'"
        )

    # Extract the first zip file
    zip_path = zip_files[0]
    print(f"Extracting {zip_path.name}...")
    extracted_dir.mkdir(exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extracted_dir)

    txt_files = list(extracted_dir.glob("genome_*.txt"))
    if not txt_files:
        raise FileNotFoundError(f"No genome txt file found after extracting {zip_path}")

    return txt_files[0]


def main():
    print("Starting 23andMe ingestion...")

    # Find the genome file
    genome_file = find_genome_file()
    print(f"Found genome file: {genome_file.name}")

    # Delete existing DB for clean rebuild
    DB_PATH.unlink(missing_ok=True)

    con = duckdb.connect(str(DB_PATH))

    # Create the main SNPs table
    # The file is tab-separated with columns: rsid, chromosome, position, genotype
    # Lines starting with # are comments (header lines)
    print("Creating SNPs table...")
    con.execute(f"""
        CREATE TABLE snps AS
        SELECT
            column0 AS rsid,
            column1 AS chromosome,
            CAST(column2 AS INTEGER) AS position,
            column3 AS genotype,
            -- Derived columns for analysis
            CASE
                WHEN column3 = '--' THEN 'no_call'
                WHEN LENGTH(column3) = 1 THEN 'haploid'
                WHEN column3 IN ('AA', 'TT', 'CC', 'GG') THEN 'homozygous'
                WHEN column3 IN ('II', 'DD') THEN 'indel_homozygous'
                WHEN column3 = 'DI' THEN 'indel_heterozygous'
                WHEN column3 LIKE 'I%' OR column3 LIKE 'D%' THEN 'indel'
                ELSE 'heterozygous'
            END AS zygosity,
            -- Flag for rsid vs internal 23andMe ID
            CASE WHEN column0 LIKE 'rs%' THEN TRUE ELSE FALSE END AS is_dbsnp
        FROM read_csv(
            '{genome_file}',
            delim='\t',
            header=false,
            skip=24,
            auto_detect=false,
            columns={{'column0': 'VARCHAR', 'column1': 'VARCHAR', 'column2': 'VARCHAR', 'column3': 'VARCHAR'}}
        )
    """)

    # Create summary views for common analyses
    print("Creating chromosome statistics table...")
    con.execute("""
        CREATE TABLE chromosome_stats AS
        SELECT
            chromosome,
            COUNT(*) AS snp_count,
            SUM(CASE WHEN zygosity = 'heterozygous' THEN 1 ELSE 0 END) AS heterozygous_count,
            SUM(CASE WHEN zygosity = 'homozygous' THEN 1 ELSE 0 END) AS homozygous_count,
            SUM(CASE WHEN zygosity = 'no_call' THEN 1 ELSE 0 END) AS no_call_count,
            MIN(position) AS min_position,
            MAX(position) AS max_position
        FROM snps
        GROUP BY chromosome
        ORDER BY
            CASE
                WHEN chromosome = 'MT' THEN 25
                WHEN chromosome = 'X' THEN 23
                WHEN chromosome = 'Y' THEN 24
                ELSE CAST(chromosome AS INTEGER)
            END
    """)

    # Create genotype distribution table
    print("Creating genotype distribution table...")
    con.execute("""
        CREATE TABLE genotype_distribution AS
        SELECT
            genotype,
            zygosity,
            COUNT(*) AS count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage
        FROM snps
        GROUP BY genotype, zygosity
        ORDER BY count DESC
    """)

    # Add table and column comments for schema documentation
    print("Adding schema comments...")
    
    # snps table
    con.execute("COMMENT ON TABLE snps IS 'Raw genotype data — one row per SNP tested'")
    con.execute("COMMENT ON COLUMN snps.rsid IS 'Variant identifier (rs# for dbSNP, i# for 23andMe internal)'")
    con.execute("COMMENT ON COLUMN snps.chromosome IS 'Chromosome: 1-22, X, Y, or MT'")
    con.execute("COMMENT ON COLUMN snps.position IS 'Base pair position on GRCh37 reference genome'")
    con.execute("COMMENT ON COLUMN snps.genotype IS 'Two-letter genotype call (e.g., AA, AG, TT) or -- for no-call'")
    con.execute("COMMENT ON COLUMN snps.zygosity IS 'Classification: homozygous, heterozygous, no_call, haploid, indel_homozygous, indel_heterozygous'")
    con.execute("COMMENT ON COLUMN snps.is_dbsnp IS 'TRUE if rsid starts with rs (standard dbSNP ID)'")
    
    # chromosome_stats table
    con.execute("COMMENT ON TABLE chromosome_stats IS 'Pre-computed summary statistics per chromosome'")
    con.execute("COMMENT ON COLUMN chromosome_stats.chromosome IS 'Chromosome: 1-22, X, Y, or MT'")
    con.execute("COMMENT ON COLUMN chromosome_stats.snp_count IS 'Total SNPs on this chromosome'")
    con.execute("COMMENT ON COLUMN chromosome_stats.heterozygous_count IS 'Number of heterozygous calls'")
    con.execute("COMMENT ON COLUMN chromosome_stats.homozygous_count IS 'Number of homozygous calls'")
    con.execute("COMMENT ON COLUMN chromosome_stats.no_call_count IS 'Number of no-call positions'")
    con.execute("COMMENT ON COLUMN chromosome_stats.min_position IS 'Smallest base pair position'")
    con.execute("COMMENT ON COLUMN chromosome_stats.max_position IS 'Largest base pair position'")
    
    # genotype_distribution table
    con.execute("COMMENT ON TABLE genotype_distribution IS 'Frequency distribution of genotype patterns'")
    con.execute("COMMENT ON COLUMN genotype_distribution.genotype IS 'The genotype pattern (AA, AG, CC, --, etc.)'")
    con.execute("COMMENT ON COLUMN genotype_distribution.zygosity IS 'Classification of this genotype'")
    con.execute("COMMENT ON COLUMN genotype_distribution.count IS 'Number of occurrences'")
    con.execute("COMMENT ON COLUMN genotype_distribution.percentage IS 'Percentage of total SNPs'")

    # Get and print summary stats
    total_snps = con.execute("SELECT COUNT(*) FROM snps").fetchone()[0]
    total_chromosomes = con.execute("SELECT COUNT(DISTINCT chromosome) FROM snps").fetchone()[0]
    heterozygosity = con.execute("""
        SELECT ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM snps WHERE zygosity NOT IN ('no_call', 'haploid')), 2)
        FROM snps WHERE zygosity = 'heterozygous'
    """).fetchone()[0]

    print("\n=== Ingestion Complete ===")
    print(f"Database: {DB_PATH}")
    print(f"Total SNPs: {total_snps:,}")
    print(f"Chromosomes: {total_chromosomes}")
    print(f"Heterozygosity rate: {heterozygosity}%")

    con.close()
    print(f"\nCreated {DB_PATH}")


if __name__ == "__main__":
    main()


