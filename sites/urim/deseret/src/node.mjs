// Node loader: reads the package's data files and returns a ready transliterator.
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createTransliterator, parseWords } from "./index.mjs";

const DATA = join(dirname(fileURLToPath(import.meta.url)), "..", "data");

/** @param {{ confidentOnly?: boolean }} [opts] */
export function loadTransliterator(opts = {}) {
  const words = parseWords(readFileSync(join(DATA, "words.tsv"), "utf8"));
  const heteronyms = JSON.parse(readFileSync(join(DATA, "heteronyms.json"), "utf8"));
  const overrides = JSON.parse(readFileSync(join(DATA, "overrides.json"), "utf8"));
  return createTransliterator({ words, heteronyms, overrides, ...opts });
}
