import { Tag } from "@/components/tag";
import {
  CATEGORY_META,
  HEARSAY_META,
  INK_VARS,
  REFERENT_META,
  SOURCE_TYPE_META,
  QUESTIONS,
  STATUS_META,
} from "./constants";
import {
  CATEGORY_IDS,
  CORRELATION_STATUSES,
  HEARSAY_GRADES,
  REFERENTS,
  SOURCE_TYPES,
} from "./schema";

/**
 * Compact reference for every scale the dataset uses. Rendered inside the
 * filter panel's "About the scales" accordion so the definitions stay one
 * click away without pushing the timeline below the fold.
 */
export function ScalesLegend() {
  return (
    <div className="space-y-5 px-2 py-2">
      <LegendBlock
        title="Referent"
        intro="Who the “God” of a backward-direction claim actually is. Several load-bearing “God was once a man” texts ground themselves in Christ's mortality — a being who was mortal, is now God, and has a Father above him fits the Son perfectly and requires no theogony for the Father."
      >
        <dl className="mt-2 space-y-2">
          {REFERENTS.map((r) => (
            <div key={r} className="flex gap-2">
              <dt>
                <Tag ink={REFERENT_META[r].ink}>{REFERENT_META[r].short}</Tag>
              </dt>
              <dd className="flex-1 text-xs leading-relaxed text-[color:var(--muted)]">
                {REFERENT_META[r].definition}
              </dd>
            </div>
          ))}
        </dl>
      </LegendBlock>

      <LegendBlock
        title="Questions and answers"
        intro="Each question owns its own scale, so an answer means something only on the question that asked it. A quote is asked a question when it carries one of that question's categories; what it answers is read off the excerpt, and a passage that turns out not to speak to the question is recorded as answering exactly that rather than being quietly dropped."
      >
        <dl className="mt-2 space-y-4">
          {QUESTIONS.map((q) => (
            <div key={q.id}>
              <dt className="text-xs font-medium text-[color:var(--foreground)]">
                {q.question}
              </dt>
              <dd className="mt-1 space-y-1">
                {q.bands.map((b) => (
                  <p
                    key={b.id}
                    className="text-xs leading-relaxed text-[color:var(--muted)]"
                  >
                    <span className="small-caps text-[color:var(--foreground)]">
                      {b.label}
                      {b.offScale && " (off the scale)"}
                    </span>{" "}
                    — {b.criteria}
                  </p>
                ))}
              </dd>
            </div>
          ))}
          <div className="flex gap-2">
            <dt className="w-16 shrink-0 pt-1">
              <span
                aria-hidden="true"
                className="inline-block h-3 w-3 rounded-full border border-dashed border-[color:var(--muted)]"
              />
            </dt>
            <dd className="flex-1 text-xs leading-relaxed text-[color:var(--muted)]">
              A dashed ring marks a placement the author has not yet confirmed.
              These are shown rather than withheld: dropping them would quietly
              thin whichever band they belong to.
            </dd>
          </div>
        </dl>
      </LegendBlock>

      <LegendBlock title="Original vs. citation">
        <dl className="mt-2 space-y-2">
          {SOURCE_TYPES.map((t) => (
            <div key={t} className="flex gap-2">
              <dt>
                <Tag ink={SOURCE_TYPE_META[t].ink}>{SOURCE_TYPE_META[t].label}</Tag>
              </dt>
              <dd className="flex-1 text-xs leading-relaxed text-[color:var(--muted)]">
                {SOURCE_TYPE_META[t].definition}
              </dd>
            </div>
          ))}
        </dl>
      </LegendBlock>

      <LegendBlock
        title="Hearsay & reliability"
        intro="How directly the text traces to the speaker. A sourcing axis only — a low grade does not mean a teaching is unimportant, and a high grade does not mean it is currently taught. Where a source's quotes do not share a provenance, individual excerpts carry their own grade."
      >
        <dl className="mt-2 space-y-2">
          {HEARSAY_GRADES.map((g) => (
            <div key={g} className="flex gap-2">
              <dt
                className={`inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-[var(--radius)] text-xs font-semibold ring-1 ${INK_VARS[HEARSAY_META[g].ink].bg} ${INK_VARS[HEARSAY_META[g].ink].text} ${INK_VARS[HEARSAY_META[g].ink].ring}`}
              >
                {g}
              </dt>
              <dd className="text-xs leading-relaxed">
                {HEARSAY_META[g].description}{" "}
                <span className="text-[color:var(--muted)]">
                  e.g. {HEARSAY_META[g].example}
                </span>
              </dd>
            </div>
          ))}
        </dl>
      </LegendBlock>

      <LegendBlock
        title="Correlation status"
        intro="A separate axis from hearsay: whether the Church currently publishes or republishes the source. A King Follett excerpt in a 1971 Ensign is high-correlation despite B-tier hearsay."
      >
        <ul className="mt-2 space-y-1.5">
          {CORRELATION_STATUSES.map((s) => (
            <li key={s} className="flex items-center gap-2 text-xs">
              <span
                aria-hidden="true"
                className={`inline-block h-1.5 w-1.5 rounded-full ${STATUS_META[s].dot}`}
              />
              <span className="small-caps">{STATUS_META[s].label}</span>
            </li>
          ))}
        </ul>
      </LegendBlock>

      <LegendBlock title="Categories">
        <dl className="mt-2 space-y-2">
          {CATEGORY_IDS.map((id) => (
            <div key={id}>
              <dt>
                <Tag ink={CATEGORY_META[id].ink}>{CATEGORY_META[id].label}</Tag>
              </dt>
              <dd className="mt-0.5 text-xs leading-relaxed text-[color:var(--muted)]">
                {CATEGORY_META[id].definition}
              </dd>
            </div>
          ))}
        </dl>
      </LegendBlock>
    </div>
  );
}

function LegendBlock({
  title,
  intro,
  children,
}: {
  title: string;
  intro?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wider text-[color:var(--muted)]">
        {title}
      </p>
      {intro && (
        <p className="mt-1 text-xs leading-relaxed text-[color:var(--muted)]">
          {intro}
        </p>
      )}
      {children}
    </div>
  );
}
