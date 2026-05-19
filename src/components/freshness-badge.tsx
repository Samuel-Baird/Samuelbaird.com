import { fmtDateTime, fmtRelative } from "@/lib/format";

type Props = {
  iso: string | null | undefined;
  size?: "sm" | "md";
  prefix?: string;
};

export function FreshnessBadge({ iso, size = "sm", prefix = "Updated" }: Props) {
  const { fresh } = fmtRelative(iso);
  const text = fmtDateTime(iso);
  const pad =
    size === "md" ? "px-3 py-1 text-xs" : "px-2 py-0.5 text-[10px]";
  const tone = fresh
    ? "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-100"
    : "bg-[color:var(--muted-soft)] text-[color:var(--muted)]";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-medium uppercase tracking-wider ${pad} ${tone}`}
      title={iso ?? undefined}
    >
      <span
        aria-hidden="true"
        className={
          "inline-block h-1.5 w-1.5 rounded-full " +
          (fresh ? "bg-emerald-500" : "bg-[color:var(--muted)]")
        }
      />
      {prefix} {text}
    </span>
  );
}
