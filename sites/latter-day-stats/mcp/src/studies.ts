import { supabase } from "./supabase.js";

export async function listStudies(opts: {
  search?: string;
  tags?: string[];
  year?: number;
  category?: string;
  sourceType?: string;
  sort?: "year" | "title";
  limit?: number;
}): Promise<any[]> {
  const sb = supabase();
  let q = sb.from("studies").select("*");

  if (opts.search) q = q.textSearch("search_tsv", opts.search, { type: "websearch" });
  if (opts.tags?.length) q = q.contains("tags", opts.tags);
  if (opts.year != null) q = q.eq("year", opts.year);
  if (opts.category) q = q.eq("category", opts.category);
  if (opts.sourceType) q = q.eq("source_type", opts.sourceType);

  if (opts.sort === "title") {
    q = q.order("title", { ascending: true });
  } else {
    q = q.order("year", { ascending: false, nullsFirst: false });
  }

  const limit = Math.min(opts.limit ?? 50, 500);
  q = q.limit(limit);

  const { data, error } = await q;
  if (error) throw error;
  return data ?? [];
}

export async function getStudy(slug: string): Promise<any | null> {
  const sb = supabase();
  const { data, error } = await sb
    .from("studies")
    .select("*")
    .eq("slug", slug)
    .maybeSingle();
  if (error) throw error;
  return data ?? null;
}

export async function listStudyTags(): Promise<
  { value: string; count: number }[]
> {
  const sb = supabase();
  const { data, error } = await sb.from("studies").select("tags");
  if (error) throw error;
  const counts = new Map<string, number>();
  for (const row of (data ?? []) as { tags: string[] }[]) {
    for (const tag of row.tags ?? []) {
      const trimmed = (tag ?? "").trim();
      if (!trimmed) continue;
      counts.set(trimmed, (counts.get(trimmed) ?? 0) + 1);
    }
  }
  return [...counts.entries()]
    .map(([value, count]) => ({ value, count }))
    .sort((a, b) => a.value.localeCompare(b.value));
}
