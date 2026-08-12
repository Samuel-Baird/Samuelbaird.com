import { requireApologist } from "@/lib/permissions";

export default async function ApologeticsHubLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Hidden-404 gate, repeated in every hub page and action below (cheap:
  // getCurrentUser is React-cache()d and the allowlist lookup is
  // unstable_cache()d) — a skipped layout render must not be a hole in the
  // gate.
  await requireApologist();

  return (
    <div className="mx-auto max-w-6xl px-5 py-10 sm:px-8">{children}</div>
  );
}
