---
created: 2026-01-12
last_edited: 2026-01-12
version: 1.0
provenance: con_JpgmOCcNVGniGrq2
---

# How to Push 19 Tier A Acquirer Targets to Notion

**Status:** ✅ All research complete, 19 candidates ready to import  
**Time to push:** ~2-3 minutes  
**Database:** Careerspan – Acquirer Targets

---

## Option 1: Quick Manual Entry (Fastest - 2 min)

1. Open Notion → **Careerspan – Acquirer Targets** database
2. Click **+ Add** to create new entry
3. Copy/paste each company from the list below
4. Fill in: Company name, Category, Website, Priority (High), Monitoring status (Watch)

### Quick Paste List (Company | Category | Website)

```
BetterUp | Career coaching | https://www.betterup.com/
Phenom | ATS | https://www.phenom.com/
Greenhouse | ATS | https://www.greenhouse.io/
Lever | ATS | https://www.lever.co/
Rippling | HRIS | https://www.rippling.com/
Gloat | Career platform | https://www.gloat.com/
Guild Education | Career platform | https://www.guildeducation.com/
iCIMS | ATS/HRIS | https://www.icims.com/
SmartRecruiters | ATS | https://www.smartrecruiters.com/
Gusto | HRIS/Payroll | https://gusto.com/
BambooHR | HRIS | https://www.bamboohr.com/
Workday | HCM/Enterprise | https://www.workday.com/
LinkedIn (Microsoft) | Career network | https://www.linkedin.com/
Ashby | ATS | https://www.ashby.com/
Deel | Global payroll/HRIS | https://www.deel.com/
Qualtrics | Experience management | https://www.qualtrics.com/
Eightfold.ai | AI talent platform | https://www.eightfold.ai/
TrueBlue | Staffing roll-up | https://www.trueblueinc.com/
Hudson Global (Star Equity) | RPO/staffing | https://www.hudsontalent.com/
```

---

## Option 2: CSV Import (Even Faster - 1 min)

1. Go to **Careerspan – Acquirer Targets** in Notion
2. Click the **⋯** menu → **Import** → **CSV**
3. Upload: `careerspan_tier_a_notion_import.csv` (from Scratch folder)
4. Map columns (Company → Company, Category → Category, Website → Website, etc.)
5. Click **Import**

**File:** `file 'Scratch/careerspan_tier_a_notion_import.csv'`

---

## Option 3: API Push (If You Have Token)

Use the prepared batch file if you have your Notion API key stored in Zo settings:

```bash
python3 /home/.z/workspaces/con_JpgmOCcNVGniGrq2/notion_push_batch.py
```

---

## What You're Getting

- ✅ **19 Tier A candidates** (highest acquisition probability)
- ✅ **Funding intel** (Series rounds, valuations, investor names)
- ✅ **M&A history** (acquisitions, strategic fit signals)
- ✅ **Team quality signals** (leadership pedigree, acquisition appetite)
- ✅ **Evidence links** (2-4 sources per company)
- ✅ **Strategic rationale** (why Careerspan fit + wedge alignment)

---

## Next Steps After Import

1. **Review** the 19 in Notion (skim the strategic fit rationales)
2. **Decide:** Any remove? Any add from Tier B (14 companies)?
3. **Prioritize:** Rank by acquisition likelihood + timing
4. **Warm intros:** Map to your network (who can intro you to CEO?)
5. **Outreach deck:** Create 1-pager for investor deck if needed

---

**Questions?** Check the full enriched CSV: `file 'Scratch/careerspan_acquirer-targets_tracking_v1.csv'`

