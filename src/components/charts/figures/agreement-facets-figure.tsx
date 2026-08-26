import { ChartFrame } from "../chart-frame";
import { FacetGrid } from "../facet-grid";
import { MiniBars, type MiniBarRow } from "../mini-bars";
import { fiveColumnPct, groupBreakdownRows, QUIZ_DATA } from "@/lib/evangelical-quiz";

/**
 * One facet per State of Theology item: agreement share by tradition, with
 * Evangelical highlighted against the rest in gray and a dashed "All U.S.
 * adults" reference line — the same numbers stateOfTheologyGraphics() in
 * src/lib/data-explorer.ts uses for its PNG alt text, so this browsable
 * index and the PNG gallery below it can never disagree.
 */
export function AgreementFacetsFigure() {
  const facets = QUIZ_DATA.items.map((item) => {
    const breakdownRows = groupBreakdownRows(item);
    const agreeByGroup = new Map<string, number>();
    for (const row of breakdownRows) {
      const pcts = fiveColumnPct(item, row.group);
      if (!pcts) continue;
      agreeByGroup.set(row.group, pcts[3] + pcts[4]); // somewhat + strongly agree
    }

    const allAdults = agreeByGroup.get("All U.S. adults");
    const rows: MiniBarRow[] = ["Evangelical", "Black Protestant", "Mainline", "Roman Catholic"]
      .filter((g) => agreeByGroup.has(g))
      .map((g) => ({
        label: g,
        value: agreeByGroup.get(g)!,
        highlight: g === "Evangelical",
      }));

    return {
      label: item.statement,
      children: (
        <MiniBars
          rows={rows}
          reference={allAdults != null ? { value: allAdults, label: "All U.S. adults" } : undefined}
        />
      ),
    };
  });

  return (
    <ChartFrame
      eyebrow="Interactive"
      title="Agreement by tradition, every statement"
      subtitle="Share who agree (somewhat or strongly), by tradition. Evangelical is highlighted; the dashed mark is the all-U.S.-adults average."
      caption={`Data: State of Theology Survey (${QUIZ_DATA.years.join("–")}) · latterdaystats.com`}
    >
      <FacetGrid facets={facets} />
    </ChartFrame>
  );
}
