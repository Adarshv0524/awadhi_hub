import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const ROOT = process.cwd();
const TARGET_DIR = join(ROOT, "src");

const DEPRECATED_PATTERNS = [
  /\/analytics\/top\b/g,
  /\/analytics\/growth\b/g,
  /\/analytics\/demand\b/g,
  /\/admin\/analytics\/contributor-trends\b/g,
  /\/admin\/analytics\/content-performance\b/g,
];

const ALLOWED_EXT = new Set([".ts", ".svelte", ".astro", ".tsx", ".js", ".mjs"]);

function walk(dir, files = []) {
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    const st = statSync(full);
    if (st.isDirectory()) {
      walk(full, files);
      continue;
    }
    const ext = full.slice(full.lastIndexOf("."));
    if (ALLOWED_EXT.has(ext)) files.push(full);
  }
  return files;
}

const files = walk(TARGET_DIR);
const violations = [];

for (const file of files) {
  const src = readFileSync(file, "utf8");
  for (const pattern of DEPRECATED_PATTERNS) {
    for (const match of src.matchAll(pattern)) {
      const idx = match.index ?? 0;
      const line = src.slice(0, idx).split("\n").length;
      violations.push(`${file.replace(ROOT + "/", "")}:${line} -> ${match[0]}`);
    }
  }
}

if (violations.length) {
  console.error("Deprecated analytics path usage detected:");
  for (const v of violations) console.error(` - ${v}`);
  process.exit(1);
}

console.log("Deprecated analytics path lint: 0 violations");
