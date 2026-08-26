import { ChartCaption, ChartFrame } from "../chart-frame";
import { StackedBars, type StackedBarsRow } from "../stacked-bars";
import { INK_PAINT } from "../palette";
import switchingGeneralizedData from "../../../../docs/datasets/pew-rls-2023-24/switching-generalized.json";

/** Same order as the companion SwitchingCurrentCompositionFigure. */
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
 * "Of those raised in it, stayed or left?" — the other half of
 * GRAPHICS_TODO.md's "Switching, generalized" item; see
 * SwitchingCurrentCompositionFigure for why this is a separate figure
 * rather than one merged bar. "Left" takes --oxblood, the site's
 * decline/negative token, since leaving a tradition one was raised in is
 * exactly the signal that token is reserved for.
 */
export function SwitchingRaisedCohortFigure() {
  const { switching_generalized: switching } = switchingGeneralizedData;

  const rows: StackedBarsRow[] = GROUP_ORDER.map((group) => {
    const g = switching[group as keyof typeof switching];
    return {
      label: group,
      segments: [g.stayed_pct, g.left_pct],
    };
  });

  return (
    <ChartFrame
      eyebrow="Interactive"
      title="Of those raised in it: still in it, or left?"
      subtitle="People raised in each tradition, split by whether they're still in it today."
      caption={<ChartCaption source="Pew Religious Landscape Study (2023-24)" />}
    >
      <StackedBars
        rows={rows}
        segmentLabels={["Stayed", "Left"]}
        paints={[INK_PAINT.accent, INK_PAINT.oxblood]}
      />
    </ChartFrame>
  );
}
