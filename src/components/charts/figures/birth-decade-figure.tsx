import { ChartCaption, ChartFrame } from "../chart-frame";
import { StackedBars, type StackedBarsRow } from "../stacked-bars";
import { ACCENT_ORDINAL_RAMP } from "../palette";
import birthDecadeData from "../../../../docs/datasets/pew-rls-2023-24/birth-decade-distribution.json";

const GROUP_ORDER = [
  "Latter-day Saint",
  "Catholic",
  "Protestant",
  "Orthodox Christian",
  "Jehovah's Witness",
  "Other Christian",
  "Christian average",
] as const;

export function BirthDecadeFigure() {
  const { distribution, decade_order: decadeOrder } = birthDecadeData;

  const rows: StackedBarsRow[] = GROUP_ORDER.map((group) => {
    const g = distribution[group as keyof typeof distribution];
    return {
      label: group,
      segments: decadeOrder.map((d) => g.shares_pct[d as keyof typeof g.shares_pct]),
    };
  });

  return (
    <ChartFrame
      eyebrow="Interactive"
      title="Birth-decade makeup, by tradition"
      subtitle="Share of each tradition's current members born in each decade — the finest age measure the public-use file offers."
      caption={<ChartCaption source="Pew Religious Landscape Study (2023-24)" />}
    >
      <StackedBars
        rows={rows}
        segmentLabels={[...decadeOrder]}
        paints={[...ACCENT_ORDINAL_RAMP]}
      />
    </ChartFrame>
  );
}
