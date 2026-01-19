---
created: 2026-01-15
last_edited: 2026-01-15
version: 1.0
---

# n5os-ode-release-fix

Bring n5os-ode export to release quality - fix broken references, missing files, placeholder values

## Objective

A fresh Zo user can run BOOTLOADER without errors, all workflows work, no broken references

## Workers

| ID | Component | Status | Dependencies | Est. Hours |
|----|-----------|--------|--------------|------------|
| W1_placeholders | placeholder_fixes | pending | - | 0.5h |
| W2_init_build_script | init_build_script | pending | - | 0.5h |
| W3_context_files | missing_context_files | pending | - | 1.0h |
| W4_prompts_fix | prompt_references_fix | pending | W2_init_build_script | 0.75h |
| W5_docs_and_links | documentation_and_links | pending | - | 0.75h |
| W6_validation | final_validation | completed | W1_placeholders, W2_init_build_script, W3_context_files, W4_prompts_fix, W5_docs_and_links | 0.5h |

## Key Decisions

- Local path: N5/export/n5os-ode/
- Repo URL: https://github.com/vrijenattawar/n5os-ode
- Workers opened in separate threads, results committed to git
- Each worker is self-contained and can be executed in any order once dependencies met

## Relevant Files

- `N5/export/n5os-ode/PLAN.md`
- `N5/export/n5os-ode/README.md`
- `N5/export/n5os-ode/BOOTLOADER.prompt.md`
