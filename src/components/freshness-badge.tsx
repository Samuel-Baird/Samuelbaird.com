import { fmtDateTime, fmtRelative } from "@/lib/format";
import { Tag } from "@/components/tag";

type Props = {
  iso: string | null | undefined;
  size?: "sm" | "md";
  prefix?: string;
};

export function FreshnessBadge({ iso, size = "sm", prefix = "Updated" }: Props) {
  const { fresh } = fmtRelative(iso);
  const text = fmtDateTime(iso);
  const pad = size === "md" ? "px-3 py-1 text-xs" : "px-2 py-0.5 text-[10px]";
  return (
    <Tag ink={fresh ? "honey" : "muted"} title={iso ?? undefined} className={pad}>
      <span
        aria-hidden="true"
        className={
          "mr-1.5 inline-block h-1.5 w-1.5 rounded-full " +
          (fresh ? "bg-[color:var(--honey)]" : "bg-[color:var(--muted)]")
        }
      />
      {prefix} {text}
    </Tag>
  );
}
