import { CollapsibleSection } from "@/components/collapsible-section";
import { QUIZ_DATA } from "@/lib/evangelical-quiz";

/**
 * Plain-language explanation of the log-likelihood method, per the honesty
 * requirements: this is a similarity measure against survey response
 * patterns, not a judgment about anyone's belief or salvation.
 */
export function HowItWorks() {
  const { EVANGELICAL_SHARE, SHRINKAGE } = QUIZ_DATA.constants;
  const reference = QUIZ_DATA.reference;
  return (
    <CollapsibleSection
      title="How this works"
      closedLabel="How this works"
      openLabel="Hide"
    >
      <div className="max-w-2xl space-y-4 text-sm leading-relaxed text-[color:var(--muted)]">
        <p>
          Each statement was put to real survey respondents who identified as
          Evangelical, and separately to respondents overall. For every answer you
          can give, we compare how common that answer is among evangelicals to how
          common it is among everyone else, and take the ratio. Answering the way
          evangelicals answer more often than other people do pushes your score up;
          answering the way they answer less often pushes it down. Your total score
          is just those ratios added together across every question you answer.
        </p>
        <p>
          &ldquo;Everyone else&rdquo; is not simply the general public, because the
          general public includes evangelicals — that would bias every comparison
          toward the middle. We estimate evangelicals are about{" "}
          <span className="tabular-nums">{Math.round(EVANGELICAL_SHARE * 100)}%</span> of
          U.S. adults and subtract that share back out of the general-public numbers
          before comparing.
        </p>
        <p>
          These statements are correlated — someone who calls one thing a sin
          tends to call a related thing a sin too — so adding up raw ratios would
          overstate how confident we should be. We divide the total by a fixed
          factor (currently {SHRINKAGE}) to correct for that.
        </p>
        <p>
          We don&apos;t report this as a probability (&ldquo;87% evangelical&rdquo;)
          because that number wouldn&apos;t mean anything reliable. Instead we score
          the actual{" "}
          {reference && <span className="tabular-nums">{reference.n.toLocaleString()}</span>}
          {" "}real people who took the 2025 State of Theology survey, using their own
          survey weights, and tell you what percentage of them you outscored. That
          percentile is the headline number, and it&apos;s a literal comparison — no
          simulation involved.
        </p>
        {reference && (
          <p>
            We do the same thing separately for each religious tradition in the
            survey (Evangelical, Black Protestant, Mainline, Roman Catholic, and
            everyone else), so you can see how you compare to each group on its own,
            not just to the country as a whole. Smaller groups mean a less precise
            comparison — Black Protestant respondents in this survey number only{" "}
            <span className="tabular-nums">
              {reference.groups.black_protestant?.n ?? 103}
            </span>
            , so read a close finish there as roughly right rather than exact.
          </p>
        )}
        <p>
          One statement — the &ldquo;first and greatest being created&rdquo; question
          about Christ&apos;s nature — comes from an earlier (2022) wave of the
          survey and was dropped from the 2025 instrument. We kept it because it&apos;s
          theologically interesting, but since the 2025 respondents you&apos;re
          compared against were never asked it, it doesn&apos;t count toward your
          percentile.
        </p>
        <p className="font-medium text-[color:var(--foreground)]">
          This is a similarity measure against survey response patterns, not a
          doctrinal test, not a judgment about your faith, and not a measure of
          whether any position here is true.
        </p>
      </div>
    </CollapsibleSection>
  );
}
