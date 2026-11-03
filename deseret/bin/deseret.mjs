#!/usr/bin/env node
// Usage:
//   echo "The priesthood is the power of God." | node deseret/bin/deseret.mjs
//   node deseret/bin/deseret.mjs --html page.html > page.dsrt.html
//   node deseret/bin/deseret.mjs --coverage text.txt       # words left in Latin script
//   options: --confident-only  leave G2P-guessed words in Latin
import { readFileSync } from "node:fs";
import { loadTransliterator } from "../src/node.mjs";

const args = process.argv.slice(2);
const flag = (f) => args.includes(f);
const file = args.find((a) => !a.startsWith("--"));
const input = file ? readFileSync(file, "utf8") : readFileSync(0, "utf8");
const t = loadTransliterator({ confidentOnly: flag("--confident-only") });

if (flag("--coverage")) {
  console.log(JSON.stringify(t.coverage(input), null, 2));
} else {
  process.stdout.write(flag("--html") ? t.html(input) : t.text(input));
}
