# 23andMe Genome Data

This dataset contains your personal genotype data exported from 23andMe—a comprehensive map of your genetic variants.

## How to Get Your Data

1. Log in to [23andme.com](https://www.23andme.com)
2. Go to Settings > 23andMe Data (or search for "Download Raw Data")
3. Click "Download" under Raw Data
4. Verify your identity (may require re-entering password)
5. Download the `.txt` file containing your genotype data
6. Place in `source/`

## Coverage

- **Source**: 23andMe Raw Data Export (Download from 23andme.com)
- **Reference Genome**: GRCh37 (Build 37)
- **Tables**: `snps`, `chromosome_stats`, `genotype_distribution`

## What's Included

### Genotype Data (`snps`)
Every SNP (single nucleotide polymorphism) tested on your 23andMe chip. Each record includes:
- The variant identifier (rsid)
- Chromosomal location
- Your genotype (the two alleles you carry)
- Derived analysis fields (zygosity, dbSNP flag)

### Chromosome Statistics (`chromosome_stats`)
Pre-computed summary of SNP counts and heterozygosity by chromosome. Useful for quick overviews without scanning the full table.

### Genotype Distribution (`genotype_distribution`)
Frequency breakdown of all genotype patterns (AA, AG, CC, etc.). Reveals the overall composition of your genetic data.

## Business Rules & Semantics

### Genotypes
- **Homozygous** (AA, TT, CC, GG): You inherited the same allele from both parents
- **Heterozygous** (AG, CT, AC, GT, etc.): You carry one copy of each allele
- **No-call** (`--`): The genotyping assay couldn't determine your genotype at this position
- **Haploid** (single letter): For sex chromosomes (X in males, Y, MT) where you only have one copy

### rsid vs Internal IDs
- **rs###### IDs**: Standard dbSNP identifiers, widely used in research databases
- **i###### IDs**: 23andMe internal identifiers for proprietary or less-characterized variants

### Heterozygosity Rate
Your heterozygosity rate (~15-16% is typical) reflects genetic diversity. Higher rates indicate more variation in your genome compared to the reference.

### Chromosome Coverage
- Chromosomes 1-22: Autosomal (diploid)
- X: Sex chromosome (diploid in females, haploid in males)
- Y: Sex chromosome (haploid, males only)
- MT: Mitochondrial DNA (haploid, maternally inherited)

## Example Queries

### How many SNPs do I have data for?
```sql
SELECT COUNT(*) AS total_snps FROM snps;
```

### What is my heterozygosity rate?
```sql
SELECT 
    ROUND(100.0 * SUM(CASE WHEN zygosity = 'heterozygous' THEN 1 ELSE 0 END) 
          / SUM(CASE WHEN zygosity IN ('heterozygous', 'homozygous') THEN 1 ELSE 0 END), 2) 
    AS heterozygosity_pct
FROM snps;
```

### Which chromosome has the most variants?
```sql
SELECT chromosome, snp_count 
FROM chromosome_stats 
ORDER BY snp_count DESC 
LIMIT 5;
```

### What is my genotype for a specific rsid?
```sql
SELECT rsid, chromosome, position, genotype 
FROM snps 
WHERE rsid = 'rs7412';  -- APOE gene variant
```

### Find all heterozygous positions on chromosome 1
```sql
SELECT rsid, position, genotype 
FROM snps 
WHERE chromosome = '1' AND zygosity = 'heterozygous'
LIMIT 20;
```

### How many no-call positions do I have per chromosome?
```sql
SELECT chromosome, no_call_count, 
       ROUND(100.0 * no_call_count / snp_count, 2) AS no_call_pct
FROM chromosome_stats
ORDER BY no_call_pct DESC;
```

### Distribution of genotype patterns
```sql
SELECT genotype, zygosity, count, percentage
FROM genotype_distribution
ORDER BY count DESC;
```

## Notes

- Raw genotype data is **not** the same as a full genome sequence. 23andMe tests specific known variants, not every base pair.
- The reference genome is GRCh37 (2009). Position coordinates may differ from newer GRCh38 databases.
- 23andMe's internal IDs (i######) may not match external databases like dbSNP or ClinVar.
- This data is suitable for research/educational purposes. For medical decisions, consult a genetic counselor.
