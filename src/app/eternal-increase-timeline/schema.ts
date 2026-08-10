import { z } from "zod";

export const CATEGORY_IDS = [
  "BACKWARD-EXPLICIT",
  "BACKWARD-MORTALITY",
  "BACKWARD-AGNOSTIC",
  "FORWARD-EXPLICIT",
  "FORWARD-EUPHEMISM",
  "SPIRIT-BIRTH-VIVIPAROUS",
  "SPIRIT-BIRTH-TRIPARTITE",
  "SPIRIT-BIRTH-ADOPTION",
  "HEAVENLY-MOTHER",
  "INFINITE-CHAIN",
  "RETREAT-REFRAME",
] as const;

export const HEARSAY_GRADES = ["A", "B", "C", "D", "E"] as const;

export const CORRELATION_STATUSES = [
  "current-correlated",
  "historical-official",
  "discontinued",
  "never-official",
] as const;

const sourceEntrySchema = z.object({
  id: z.string().min(1),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "date must be YYYY-MM-DD"),
  dateDisplay: z.string().min(1),
  datePrecision: z.enum(["day", "month", "year"]),
  title: z.string().min(1),
  speaker: z.string().min(1),
  office: z.string().min(1),
  venue: z.string().min(1),
  url: z.url(),
  categories: z.array(z.enum(CATEGORY_IDS)).min(1),
  hearsay: z.enum(HEARSAY_GRADES),
  correlationStatus: z.enum(CORRELATION_STATUSES),
  summary: z.string().min(1),
  transcription: z.string().min(1),
  notes: z.string().min(1),
  needsVerification: z.boolean().optional(),
});

const sourcesSchema = z.array(sourceEntrySchema);

export type SourceEntry = z.infer<typeof sourceEntrySchema>;
export type CategoryId = (typeof CATEGORY_IDS)[number];
export type HearsayGrade = (typeof HEARSAY_GRADES)[number];
export type CorrelationStatus = (typeof CORRELATION_STATUSES)[number];

// Runs at module scope of a statically prerendered page, so a hand-edit typo
// in sources.json fails `next build` rather than surfacing at runtime.
export function parseSources(raw: unknown): SourceEntry[] {
  const result = sourcesSchema.safeParse(raw);
  if (!result.success) {
    throw new Error(
      `eternal-increase-timeline/sources.json is invalid:\n${z.prettifyError(result.error)}`,
    );
  }
  return result.data;
}
