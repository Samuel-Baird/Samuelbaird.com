import { ChartCaption, ChartFrame } from "../chart-frame";
import { DotPlot, type DotPlotRow } from "../dot-plot";
import { INK_PAINT } from "../palette";
import switchingRatesData from "../../../../docs/datasets/pew-rls-2023-24/switching-rates.json";

/** Same order as SWITCHING_GROUP_ORDER in src/lib/data-explorer.ts, so this
 * figure and the PNG twin on the same page read consistently. */
const GROUP_ORDER = [
  "Catholic",
  "Jehovah's Witness",
  "Latter-day Saint",
  "Protestant",
  "Other Christian",
  "Orthodox Christian",
] as const;

export function NetChangeFigure() {
  const { switching } = switchingRatesData;

  const rows: DotPlotRow[] = GROUP_ORDER.map((group) => {
    const g = switching[group as keyof typeof switching];
    const lo = g.net_change_pct - 1.96 * g.net_change_se;
    const hi = g.net_change_pct + 1.96 * g.net_change_se;
    return {
      label: group,
      value: g.net_change_pct,
      lo,
      hi,
      paint: group === "Latter-day Saint" ? INK_PAINT.honey : INK_PAINT.oxblood,
      deEmphasized: hi >= 0, // CI includes zero
    };
  });

  return (
    <ChartFrame
      eyebrow="Interactive"
      title="Net change since childhood, by tradition"
      subtitle="Percent change from the share of U.S. adults raised in each tradition to the share currently in it. Hover a row for the exact interval."
      caption={
        <ChartCaption
          source="Pew Religious Landscape Study (2023-24)"
          note="Faded rows (Other Christian, Orthodox Christian): the 95% interval includes zero."
        />
      }
    >
      <DotPlot
        rows={rows}
        reference={{ value: 0, label: "No change" }}
        format="signedPercent"
      />
    </ChartFrame>
  );
}
