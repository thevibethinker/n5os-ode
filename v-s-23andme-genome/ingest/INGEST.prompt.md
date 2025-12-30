# 23andMe Genome Data Ingestion

This document describes how to ingest 23andMe raw genotype data exports.

## Source Files

- `source/genome_*_Full_*.txt` - Raw 23andMe genome export (text file)
- `source/genome_*_Full_*.zip` - Or zipped export (auto-extracted to `source/extracted/`)

The raw file contains:
- 24 header lines (comments starting with `#`) including file metadata and column descriptions
- Tab-separated data with columns: `rsid`, `chromosome`, `position`, `genotype`

## Tables Created

| Table | Description | Row Count |
|-------|-------------|-----------|
| `snps` | Raw genotype data with derived analysis columns | ~631,000 |
| `chromosome_stats` | Per-chromosome summary statistics | 25 |
| `genotype_distribution` | Frequency of each genotype pattern | ~20 |

## Transformations

### snps table
- Parses the 4-column tab-separated format
- Adds `zygosity` column classifying each SNP:
  - `homozygous`: AA, TT, CC, GG
  - `heterozygous`: AG, CT, AC, GT, AT, CG
  - `no_call`: -- (failed genotyping)
  - `haploid`: A, T, C, G (sex chromosomes, MT)
  - `indel_homozygous`: II, DD
  - `indel_heterozygous`: DI
- Adds `is_dbsnp` boolean flag (true if rsid starts with "rs")

### chromosome_stats table
- Aggregates counts by chromosome
- Includes heterozygous/homozygous/no_call breakdowns
- Reports position ranges per chromosome

### genotype_distribution table
- Counts occurrences of each genotype
- Calculates percentage distribution

## Running

Assume duckdb is available in your environment:
```bash
python ingest/ingest.py
```

## Extending

To re-process updated exports:
1. Place the new `genome_*.zip` in `source/`
2. Delete `source/extracted/` to force re-extraction (optional)
3. Re-run `python ingest/ingest.py`

The script is idempotent—it deletes and recreates `data.duckdb` on each run.

## File Format Reference

23andMe raw data format (build 37/GRCh37):
```
# rsid	chromosome	position	genotype
rs548049170	1	69869	TT
rs9283150	1	565508	AA
```

- **rsid**: dbSNP reference ID (rs#) or 23andMe internal ID (i#)
- **chromosome**: 1-22, X, Y, or MT
- **position**: Base pair position on reference genome (GRCh37)
- **genotype**: Two-letter allele calls (or single for haploid regions)


