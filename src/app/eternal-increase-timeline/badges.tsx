import { Tag } from "@/components/tag";
import { HEARSAY_META, INK_VARS, REFERENT_META } from "./constants";
import type { HearsayGrade, Referent } from "./schema";

// Shared by the filter panel and the entry cards. They live here rather than
// in either consumer so the panel can be extracted for the mobile drawer
// without the two files importing each other.

export function HearsayBadge({ grade }: { grade: HearsayGrade }) {
  const meta = HEARSAY_META[grade];
  const c = INK_VARS[meta.ink];
  return (
    <span
      title={`Hearsay ${grade}: ${meta.description} Example: ${meta.example}`}
      aria-label={`Hearsay rating ${grade}: ${meta.description}`}
      className={`inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-[var(--radius)] text-xs font-semibold ring-1 ${c.bg} ${c.text} ${c.ring}`}
    >
      {grade}
    </span>
  );
}

export function ReferentChip({ referent }: { referent: Referent }) {
  const meta = REFERENT_META[referent];
  return (
    <Tag ink={meta.ink} title={`${meta.label} — ${meta.definition}`}>
      {meta.short}
    </Tag>
  );
}
