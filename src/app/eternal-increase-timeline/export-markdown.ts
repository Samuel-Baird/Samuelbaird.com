import { CATEGORY_META, ERAS, HEARSAY_META, STATUS_META, eraFor } from "./constants";
import type {
  CategoryId,
  CorrelationStatus,
  HearsayGrade,
  SourceEntry,
} from "./schema";

export type FilterState = {
  categories: Set<CategoryId>;
  grades: Set<HearsayGrade>;
  statuses: Set<CorrelationStatus>;
  query: string;
};

function filterSummary(filters: FilterState): string {
  const parts: string[] = [];
  if (filters.categories.size > 0) {
    parts.push(
      `categories: ${[...filters.categories].map((c) => CATEGORY_META[c].label).join(", ")}`,
    );
  }
  if (filters.grades.size > 0) {
    parts.push(`hearsay: ${[...filters.grades].join(", ")}`);
  }
  if (filters.statuses.size > 0) {
    parts.push(
      `status: ${[...filters.statuses].map((s) => STATUS_META[s].label).join(", ")}`,
    );
  }
  if (filters.query.trim()) {
    parts.push(`search: "${filters.query.trim()}"`);
  }
  return parts.length > 0 ? parts.join("; ") : "none";
}

export function buildMarkdown(
  entries: SourceEntry[],
  total: number,
  filters: FilterState,
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
        `**Hearsay:** ${entry.hearsay} — ${HEARSAY_META[entry.hearsay].description} · **Status:** ${STATUS_META[entry.correlationStatus].label}${entry.needsVerification ? " · ⚠ needs verification" : ""}`,
      );
      lines.push(
        `**Categories:** ${entry.categories.map((c) => CATEGORY_META[c].label).join(", ")}`,
      );
      lines.push("");
      lines.push(entry.summary);
      lines.push("");
      for (const line of entry.transcription.split("\n")) {
        lines.push(`> ${line}`);
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
