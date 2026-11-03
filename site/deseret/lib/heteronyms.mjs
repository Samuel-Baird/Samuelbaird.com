// Vendored from pulpit-vault scripts/deseret/heteronyms.mjs @ f57f3ff446.
// Do not edit here: regenerate with `python -m pipeline.deseret_data`. See deseret/README.md.
// Resolves sense-dependent ("heteronym") word pronunciations using
// schema/deseret/heteronyms.yaml: local high-precision rules first, then an
// optional POS tag (from wink-nlp, supplied by the caller -- this module
// has no NLP dependency itself), then the corpus-tuned default. See that
// file's header for the design rationale and the resolution order.
//
// Fast path: createHeteronymResolver() precomputes a Set of the handful of
// heteronym words so every non-heteronym word (99.9%+ of the corpus) is a
// single Set.has() check, not a rule evaluation.

function evalCondition(cond, ctx) {
  // Two condition shapes: "prev in [a, b, c]" for trailing triggers ("we
  // have read"), "next in [a, b, c]" for leading ones ("blessed are the
  // poor", where the trigger follows the ambiguous word).
  const m = /^(prev|next) in \[(.+)\]$/.exec(cond.trim());
  if (!m) throw new Error(`Unsupported heteronym rule condition: "${cond}"`);
  const [, side, list] = m;
  const words = list.split(",").map((w) => w.trim().toLowerCase());
  const value = ctx[side];
  return typeof value === "string" && words.includes(value.toLowerCase());
}

/**
 * @param {Record<string, any>} spec parsed schema/deseret/heteronyms.yaml
 * @returns {{
 *   isHeteronym(word: string): boolean,
 *   resolve(word: string, ctx?: { prev?: string, next?: string, tag?: string }): string[] | null,
 * }}
 */
export function createHeteronymResolver(spec) {
  const entries = new Map(
    Object.entries(spec ?? {}).filter(([, v]) => v && typeof v === "object" && v.senses),
  );

  function isHeteronym(word) {
    return entries.has(word.toLowerCase());
  }

  function resolve(word, ctx = {}) {
    const entry = entries.get(word.toLowerCase());
    if (!entry) return null;

    for (const rule of entry.rules ?? []) {
      if (evalCondition(rule.when, ctx)) {
        const sense = entry.senses[rule.sense];
        if (sense) return sense;
      }
    }

    if (ctx.tag && entry.pos_map && entry.pos_map[ctx.tag]) {
      const senseKey = entry.pos_map[ctx.tag];
      const sense = entry.senses[senseKey];
      if (sense) return sense;
    }

    const defaultSense = entry.senses[entry.default];
    if (!defaultSense) {
      throw new Error(`schema/deseret/heteronyms.yaml entry "${word}" has no senses.${entry.default}`);
    }
    return defaultSense;
  }

  return { isHeteronym, resolve };
}
