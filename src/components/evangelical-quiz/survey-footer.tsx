import { QUIZ_DATA } from "@/lib/evangelical-quiz";
import { waveMeta } from "@/lib/evangelical-quiz/survey-meta";

/**
 * Sourcing disclosure: sponsor, fielder, wave year(s), sample size, margin
 * of error, and what "group" means here. Rendered once in the page's
 * marginalia aside so it stays visible through every quiz screen without
 * repeating itself — this is due diligence, not a selling point, and should
 * never compete with the question or the result for attention.
 */
export function SurveyFooter() {
  const waves = QUIZ_DATA.years.map(waveMeta);
  const primary = waves.find((w) => w.year !== 2022) ?? waves[0];

  return (
    <section className="space-y-4 text-xs leading-relaxed text-[color:var(--muted)]">
      <h2 className="small-caps text-xs font-medium text-[color:var(--muted)]">
        About this data
      </h2>
      <p>
        {primary?.sponsor ?? "Ligonier Ministries"} / {primary?.fielder ?? "Lifeway Research"},
        &ldquo;State of Theology&rdquo;
        {waves.length > 1 ? (
          <> ({waves.map((w) => w.year).join(" & ")} waves — years are noted per question)</>
        ) : (
          <> ({primary?.year} wave)</>
        )}
        .{" "}
        {primary?.sampleSize ? (
          <>
            Sample size {primary.sampleSize.toLocaleString()} U.S. adults, margin of error{" "}
            {primary.marginOfError ?? "not on file"}.
          </>
        ) : (
          <>Sample size and margin of error for this wave are not yet on file.</>
        )}
      </p>
      <p>
        &ldquo;Group&rdquo; means religious tradition — a denomination or church
        association a respondent named — not a doctrinal test. Someone can belong to a
        tradition and still disagree with what most of that tradition says here.
      </p>
    </section>
  );
}
