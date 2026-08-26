import { ChartCaption, ChartFrame } from "../chart-frame";
import { StackedBars, type StackedBarsRow } from "../stacked-bars";
import { INK_PAINT } from "../palette";
import switchingGeneralizedData from "../../../../docs/datasets/pew-rls-2023-24/switching-generalized.json";

/** Same order BirthDecadeFigure uses, so the three Pew RLS "Interactive"
 * figures on this page read as one consistent group. */
const GROUP_ORDER = [
  "Latter-day Saint",
  "Catholic",
  "Protestant",
  "Orthodox Christian",
  "Jehovah's Witness",
  "Other Christian",
  "Christian average",
] as const;

/**
 * "Of today's members, raised in it or converted in?" — one half of
 * GRAPHICS_TODO.md's "Switching, generalized" item. The companion
 * SwitchingRaisedCohortFigure covers the other half (of those raised in a
 * tradition, stayed or left?) — two separate 100%-stacked figures rather
 * than one merged bar, because the two questions have different
 * denominators (current members here; the raised cohort there). The
 * "raised in it" segment shares --accent with that figure's "stayed"
 * segment, since it's the same weighted headcount read against a
 * different base.
 */
export function SwitchingCurrentCompositionFigure() {
  const { switching_generalized: switching } = switchingGeneralizedData;

  const rows: StackedBarsRow[] = GROUP_ORDER.map((group) => {
    const g = switching[group as keyof typeof switching];
    return {
      label: group,
      segments: [g.retained_in_pct, g.converted_in_pct],
    };
  });

  return (
    <ChartFrame
      eyebrow="Interactive"
      title="Of today's members: raised in it, or converted in?"
      subtitle="Each tradition's current membership, split by whether they were raised in it or joined from elsewhere."
      caption={<ChartCaption source="Pew Religious Landscape Study (2023-24)" />}
    >
      <StackedBars
        rows={rows}
        segmentLabels={["Raised in it", "Converted in"]}
        paints={[INK_PAINT.accent, INK_PAINT.honey]}
      />
    </ChartFrame>
  );
}
