const { execSync, existsSync, statSync, basename, extname } = require('child_process');
const fs = require('fs');
const path = require('path');

const TYPE_MAPPINGS = [
  {
    extension: ".db",
    possibleTypes: ["sqlite", "duckdb"],
    typeSignatures: {
      sqlite: ["SQLite", "sqlite"],
      duckdb: ["DuckDB", "DUCK"]
    },
    tools: {
      sqlite: { use: ["sqlite3", "python3+sqlite3"], avoid: ["duckdb"] },
      duckdb: { use: ["duckdb", "python3+duckdb"], avoid: ["sqlite3"] }
    }
  },
  {
    extension: ".json",
    possibleTypes: ["json", "jsonl", "ndjson"],
    typeSignatures: {
      json: ["starts with {", "starts with ["],
      jsonl: ["one JSON object per line", "newline-delimited"],
      ndjson: ["one JSON object per line", "newline-delimited"]
    },
    tools: {
      json: { use: ["jq", "python3+json"], avoid: [] },
      jsonl: { use: ["jq -c", "python3 line-by-line"], avoid: ["python3 json.load()"] },
      ndjson: { use: ["jq -c", "python3 line-by-line"], avoid: ["python3 json.load()"] }
    }
  },
  {
    extension: ".yaml",
    possibleTypes: ["yaml", "json-as-yaml"],
    typeSignatures: {
      yaml: ["starts with ---", "starts with key:", "not JSON syntax"],
      "json-as-yaml": ["starts with {", "starts with ["]
    },
    tools: {
      yaml: { use: ["python3+yaml", "yq"], avoid: ["jq"] },
      "json-as-yaml": { use: ["jq", "python3+json"], avoid: ["python3+yaml (may work but misleading)"] }
    }
  },
  {
    extension: ".csv",
    possibleTypes: ["csv", "tsv"],
    typeSignatures: {
      csv: ["comma delimiter"],
      tsv: ["tab delimiter"]
    },
    tools: {
      csv: { use: ["python3+csv", "duckdb", "miller (mlr)"], avoid: [] },
      tsv: { use: ["python3+csv (dialect=excel-tab)", "duckdb (auto-detect)"], avoid: ["default csv parsers"] }
    }
  },
  {
    extension: ".parquet",
    possibleTypes: ["parquet"],
    typeSignatures: {
      parquet: ["Parquet", "Apache Parquet"]
    },
    tools: {
      parquet: { use: ["duckdb", "python3+pyarrow", "python3+pandas"], avoid: ["sqlite3", "jq", "text editors"] }
    }
  }
];

function detectType(filepath) {
  const ext = path.extname(filepath).toLowerCase();
  const mapping = TYPE_MAPPINGS.find(m => m.extension === ext);
  
  if (!mapping) {
    // Unknown extension - use file command
    const fileType = execSync(`file -b "${filepath}"`, { encoding: "utf8" }).trim();
    return {
      detectedType: fileType,
      recommendedTools: ["file command for details"],
      avoidTools: [],
      confidence: "low"
    };
  }
  
  // Use file command for detection
  const fileOutput = execSync(`file -b "${filepath}"`, { encoding: "utf8" }).trim();
  let headOutput = "";
  try {
    if (fs.existsSync(filepath) && fs.statSync(filepath).size > 0) {
      headOutput = execSync(`head -c 200 "${filepath}" 2>/dev/null | head -1`, { encoding: "utf8", stdio: ['pipe', 'pipe', 'pipe'] });
    }
  } catch (e) {
    // head may fail on binary files
  }
  
  // Match against signatures
  for (const [typeName, signatures] of Object.entries(mapping.typeSignatures)) {
    const combinedOutput = (fileOutput + " " + headOutput).toLowerCase();
    const fileLower = fileOutput.toLowerCase();
    
    for (const sig of signatures) {
      if (fileLower.includes(sig.toLowerCase())) {
        const toolInfo = mapping.tools[typeName];
        return {
          detectedType: typeName.toUpperCase(),
          recommendedTools: toolInfo.use,
          avoidTools: toolInfo.avoid,
          confidence: "high"
        };
      }
    }
  }
  
  // Ambiguous - couldn't determine exact type
  return {
    detectedType: `AMBIGUOUS (${mapping.possibleTypes.join(" OR ")})`,
    recommendedTools: ["Verify manually first"],
    avoidTools: mapping.possibleTypes.flatMap(t => mapping.tools[t]?.avoid || []),
    confidence: "medium"
  };
}

function formatResult(filepath, info) {
  const lines = [
    `FILE: ${filepath}`,
    `TYPE: ${info.detectedType} (confidence: ${info.confidence})`,
    `TOOLS: ${info.recommendedTools.join(", ") || "verify first"}`
  ];
  
  if (info.avoidTools.length > 0) {
    lines.push(`AVOID: ${info.avoidTools.join(", ")}`);
  }
  
  return lines.join("\n");
}

function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (!command || command === "--help" || command === "-h") {
    console.log(`
file-preflight - Verify file types before using format-specific tools

Usage:
  file-preflight check <path>     Check single file
  file-preflight batch <dir>      Scan directory for ambiguous files

Examples:
  bun preflight.js check /home/workspace/Zoffice/data/office.db
  bun preflight.js batch /home/workspace/data
`);
    process.exit(0);
  }
  
  if (command === "check") {
    const filepath = args[1];
    if (!filepath || !fs.existsSync(filepath)) {
      console.error(`Error: File not found: ${filepath}`);
      process.exit(1);
    }
    
    const info = detectType(filepath);
    console.log(formatResult(filepath, info));
    return;
  }
  
  if (command === "batch") {
    const dir = args[1];
    if (!dir || !fs.existsSync(dir)) {
      console.error(`Error: Directory not found: ${dir}`);
      process.exit(1);
    }
    
    const ambiguousExtensions = [".db", ".json", ".yaml", ".yml", ".csv"];
    const extPattern = ambiguousExtensions.map(e => `-name "*${e}"`).join(" -o ");
    let files = [];
    try {
      files = execSync(`find "${dir}" -type f \\( ${extPattern} \\)`, {
        encoding: "utf8"
      }).trim().split("\n").filter(Boolean);
    } catch (e) {
      console.error("Error scanning directory");
      process.exit(1);
    }
    
    console.log(`\nScanning ${files.length} files with ambiguous extensions in ${dir}\n`);
    
    for (const file of files) {
      const info = detectType(file);
      if (info.confidence !== "high") {
        console.log(`[${info.confidence.toUpperCase()}] ${path.basename(file)}: ${info.detectedType}`);
      }
    }
    
    console.log("\nBatch complete. Use 'check' command for details on specific files.");
    return;
  }
  
  console.error(`Unknown command: ${command}`);
  process.exit(1);
}

main();