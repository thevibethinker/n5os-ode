#!/bin/bash
cd /home/workspace

# List of files to update
files=(
  "Lists/README.md"
  "N5/config/README.md"
  "N5/scripts/README.md"
  "N5/scripts/README_git_check_v2.md"
  "N5/IMPLEMENTATION_SUMMARY.md"
  "Recipes/Add Digest.md"
  "Recipes/Docgen.md"
  "Recipes/File Protector.md"
  "Recipes/Function Import System.md"
  "Recipes/Git Check.md"
  "Recipes/Prompt Import.md"
  "Recipes/Search Commands.md"
  "Knowledge/architectural/principles/core.md"
  "Knowledge/architectural/principles/safety.md"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    sed -i 's|N5/config/commands\.jsonl|Recipes/recipes.jsonl (index only)|g' "$file"
    sed -i "s|file 'N5/config/commands\.jsonl'|file 'N5/prefs/operations/recipe-execution-guide.md'|g" "$file"
    echo "✓ Updated: $file"
  else
    echo "✗ Not found: $file"
  fi
done

echo ""
echo "=== Cleanup Complete ==="
