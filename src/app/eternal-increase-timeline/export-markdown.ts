import {
  CATEGORY_META,
  ERAS,
  HEARSAY_META,
  REFERENT_META,
  SOURCE_TYPE_META,
  STATUS_META,
  eraFor,
  hearsayForQuote,
} from "./constants";
import type {
  CategoryId,
  CorrelationStatus,
  HearsayGrade,
  Referent,
  SourceEntry,
  SourceType,
} from "./schema";

export type FilterState = {
  categories: Set<CategoryId>;
  grades: Set<HearsayGrade>;
  statuses: Set<CorrelationStatus>;
  referents: Set<Referent>;
  sourceTypes: Set<SourceType>;
  query: string;
  collapseCitations: boolean;
};

function filterSummary(filters: FilterState): string {
  const parts: string[] = [];
  if (filters.categories.size > 0) {
    parts.push(
      `categories: ${[...filters.categories].map((c) => CATEGORY_META[c].label).join(", ")}`,
    );
  }
  if (filters.grades.size > 0) parts.push(`hearsay: ${[...filters.grades].join(", ")}`);
  if (filters.statuses.size > 0) {
    parts.push(
      `status: ${[...filters.statuses].map((s) => STATUS_META[s].label).join(", ")}`,
    );
  }
  if (filters.referents.size > 0) {
    parts.push(
      `referent: ${[...filters.referents].map((r) => REFERENT_META[r].short).join(", ")}`,
    );
  }
  if (filters.sourceTypes.size > 0) {
    parts.push(
      `type: ${[...filters.sourceTypes].map((t) => SOURCE_TYPE_META[t].label).join(", ")}`,
    );
  }
  if (filters.query.trim()) parts.push(`search: "${filters.query.trim()}"`);
  if (filters.collapseCitations) parts.push("citations collapsed into originals");
  return parts.length > 0 ? parts.join("; ") : "none";
}

export function buildMarkdown(
  entries: SourceEntry[],
  total: number,
  filters: FilterState,
  byId: Map<string, SourceEntry>,
): string {
  const lines: string[] = [];
  lines.push("# Eternal Increase — Source Timeline (filtered export)");
  lines.push("");
  lines.push(
    `_Exported ${new Date().toISOString().slice(0, 10)} · ${entries.length} of ${total} sources · Filters: ${filterSummary(filters)}_`,
  );
  lines.push("");
  lines.push(
    "_Working research document. Categorizations are the author's analysis, not official characterizations._",
  );

  for (const era of ERAS) {
    const inEra = entries.filter((e) => eraFor(e).id === era.id);
    if (inEra.length === 0) continue;
    lines.push("");
    lines.push(`## ${era.range} · ${era.label}`);
    for (const entry of inEra) {
      lines.push("");
      lines.push(`### ${entry.dateDisplay} — [${entry.title}](${entry.url})`);
      lines.push("");
      lines.push(
        `**Speaker:** ${entry.speaker} · **Office:** ${entry.office} · **Venue:** ${entry.venue}`,
      );
      lines.push(
        `**Type:** ${SOURCE_TYPE_META[entry.sourceType].label} · **Hearsay:** ${entry.hearsay} — ${HEARSAY_META[entry.hearsay].description} · **Status:** ${STATUS_META[entry.correlationStatus].label} · **Referent:** ${REFERENT_META[entry.referent].short}${entry.needsVerification ? " · ⚠ needs verification" : ""}`,
      );
      if (entry.citesId?.length) {
        const named = entry.citesId
          .map((id) => byId.get(id)?.title ?? id)
          .join("; ");
        lines.push(`**Cites:** ${named}`);
      }
      if (entry.witnesses?.length) {
        lines.push(
          `**Witnesses:** ${entry.witnesses.map((w) => w.scribe).join(", ")}`,
        );
      }

      for (const quote of entry.quotes) {
        lines.push("");
        const cats =
          quote.categories.length > 0
            ? quote.categories.map((c) => CATEGORY_META[c].label).join(", ")
            : "context (uncategorized)";
        const grade = hearsayForQuote(entry, quote.quoteId);
        const bits = [cats];
        if (quote.implied) bits.push("implied");
        if (quote.referent) bits.push(`referent: ${REFERENT_META[quote.referent].short}`);
        if (grade !== entry.hearsay) bits.push(`hearsay: ${grade}`);
        lines.push(`**${bits.join(" · ")}**`);
        lines.push("");
        for (const line of quote.excerpt.split("\n")) lines.push(`> ${line}`);
        if (quote.note) {
          lines.push("");
          lines.push(`*${quote.note}*`);
        }
      }

      lines.push("");
      lines.push(`*Notes:* ${entry.notes}`);
    }
  }
  lines.push("");
  return lines.join("\n");
}

export function downloadMarkdown(markdown: string): void {
  const blob = new Blob([markdown], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `eternal-increase-timeline-${new Date().toISOString().slice(0, 10)}.md`;
  a.click();
  URL.revokeObjectURL(url);
}
