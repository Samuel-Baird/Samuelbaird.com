import {
  groupBreakdownRows,
  responseLabel,
  type QuizItem,
  type Response,
} from "@/lib/evangelical-quiz";

/**
 * Diverging color per response, reusing the site's two ink families rather
 * than introducing new hex values: oxblood for disagreement, accent for
 * agreement, muted-soft for the neutral middle. Opacity modifiers (already
 * an established pattern - see globals.css) give the "light" variants
 * without a second set of tokens.
 */
const SEGMENT_CLASS: Record<Response, string> = {
  strongly_disagree: "bg-[color:var(--oxblood)]",
  somewhat_disagree: "bg-[color:var(--oxblood)]/45",
  not_sure: "bg-[color:var(--muted-soft)]",
  somewhat_agree: "bg-[color:var(--accent)]/45",
  strongly_agree: "bg-[color:var(--accent)]",
};

const GROUP_LABEL: Record<string, string> = {
  Evangelical: "Evangelical",
  "Black Protestant": "Black Protestant",
  Mainline: "Mainline",
  "Roman Catholic": "Roman Catholic",
  "All U.S. adults": "All U.S. adults",
};

/**
 * Per-question breakdown: one 100%-stacked bar per group that has data for
 * this item, colored strongly-disagree-red through strongly-agree-blue. A
 * small marker under each bar shows where the reader's own answer falls in
 * that group's distribution, so "how does my answer compare" is a glance,
 * not a table read.
 */
export function GroupBreakdownChart({
  item,
  chosenIndex,
}: {
  item: QuizItem;
  chosenIndex: number;
}) {
  const rows = groupBreakdownRows(item);
  if (rows.length === 0) return null;

  return (
    <div className="mt-6 space-y-4">
      <p className="small-caps text-[11px] text-[color:var(--muted)]">
        How each group answered
      </p>
      {rows.map((row) => (
        <GroupRow
          key={row.group}
          label={GROUP_LABEL[row.group] ?? row.group}
          scale={item.scale}
          pcts={row.pcts}
          chosenIndex={chosenIndex}
        />
      ))}
      <Legend scale={item.scale} />
    </div>
  );
}

function GroupRow({
  label,
  scale,
  pcts,
  chosenIndex,
}: {
  label: string;
  scale: Response[];
  pcts: number[];
  chosenIndex: number;
}) {
  const offsets = pcts.reduce<number[]>((acc, p, i) => {
    acc.push(i === 0 ? 0 : acc[i - 1] + pcts[i - 1]);
    return acc;
  }, []);
  const markerLeft = offsets[chosenIndex] + pcts[chosenIndex] / 2;

  return (
    <div>
      <div className="flex items-baseline justify-between text-xs">
        <span className="font-medium text-[color:var(--foreground)]">{label}</span>
        <span className="tabular-nums text-[color:var(--muted)]">
          {pcts[chosenIndex]}% answered like you
        </span>
      </div>
      <div className="relative mt-1.5">
        <div className="flex h-5 w-full overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)]">
          {scale.map((r, i) => (
            <div
              key={r}
              className={SEGMENT_CLASS[r]}
              style={{ width: `${pcts[i]}%` }}
              title={`${responseLabel(r)}: ${pcts[i]}%`}
            />
          ))}
        </div>
        <div
          aria-hidden="true"
          className="absolute -bottom-3.5 flex -translate-x-1/2 flex-col items-center text-[color:var(--foreground)]"
          style={{ left: `${markerLeft}%` }}
        >
          <span className="text-[9px] leading-none">▲</span>
        </div>
      </div>
    </div>
  );
}

function Legend({ scale }: { scale: Response[] }) {
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1.5 pt-1 text-[10px] text-[color:var(--muted)]">
      {scale.map((r) => (
        <span key={r} className="inline-flex items-center gap-1.5">
          <span className={`h-2.5 w-2.5 rounded-[2px] ${SEGMENT_CLASS[r]}`} aria-hidden="true" />
          {responseLabel(r)}
        </span>
      ))}
      <span className="inline-flex items-center gap-1.5">
        <span className="text-[9px]">▲</span>
        your answer
      </span>
    </div>
  );
}
