import { CollapsibleSection } from "@/components/collapsible-section";
import { QUIZ_DATA } from "@/lib/evangelical-quiz";

/**
 * Plain-language explanation of the log-likelihood method, per the honesty
 * requirements: this is a similarity measure against survey response
 * patterns, not a judgment about anyone's belief or salvation.
 */
export function HowItWorks() {
  const { EVANGELICAL_SHARE, SHRINKAGE } = QUIZ_DATA.constants;
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
          because that number wouldn&apos;t mean anything reliable. Instead we compare
          your score to a simulated population of 20,000 respondents built from the
          same survey data, and tell you what percentage of them you outscored. That
          percentile is the headline number.
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
