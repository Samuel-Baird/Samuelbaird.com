import { ChartCaption, ChartFrame } from "../chart-frame";
import { WaveLineChart, type WaveSeries } from "../wave-line-chart";
import pidOverTimeData from "../../../../docs/datasets/ryan-burge/pid-over-time.json";

/** Ryan Burge's flagship chart form — a line over survey waves. This is the
 * "Party ID (pid7) over time, by religious tradition" item from
 * docs/datasets/ryan-burge/GRAPHICS_TODO.md, resolved per that file's
 * NEEDS DESIGN DECISION note: a hand-picked group set rather than a
 * RELTRAD rollup, since RELTRAD would erase LDS entirely. */
export function PidOverTimeFigure() {
  const { waves, series } = pidOverTimeData;

  const chartSeries: WaveSeries[] = Object.entries(series).map(([label, s]) => ({
    label,
    values: s.values,
    highlight: label === "Latter-day Saint",
  }));

  return (
    <ChartFrame
      eyebrow="Interactive"
      title="Party ID over time, by tradition"
      subtitle="Mean 7-point party ID (-3 = strong Democrat, +3 = strong Republican) across seven federal election cycles."
      caption={
        <ChartCaption
          source="CCES/CES common content, 2006–2018"
          via="Ryan Burge"
          note="Unweighted — this extract carries no survey weight column."
        />
      }
    >
      <WaveLineChart waves={waves} series={chartSeries} yDomain={[-3, 3]} format="twoDecimal" />
    </ChartFrame>
  );
}
