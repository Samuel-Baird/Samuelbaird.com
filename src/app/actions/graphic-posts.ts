"use server";

import { revalidatePath, revalidateTag } from "next/cache";
import { requireAdmin } from "@/lib/auth";
import { graphicExists } from "@/lib/graphic-posts";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { firstZodMessage, graphicPublishSchema } from "@/lib/validation";

// RLS on graphic_posts is deny-all (supabase/migrations/0049_graphic_posts.sql,
// 0051_graphic_published.sql, 0054_graphic_publish_at.sql); the gate is
// requireAdmin() and all access goes through the service client. The
// legacy `posted`/`posted_dates` columns are no longer read or written -
// publish_at is the single record of when a graphic went (or goes) live.

type SetGraphicPublishedInput = {
  datasetSlug: string;
  graphicId: string;
  published: boolean;
  /** ISO instant to go live. Past = "published as of then" (used to record
   * when something was posted), future = scheduled. Omitted with
   * published = true means "now". Ignored when published = false. */
  publishAt?: string;
  /** Site-relative path of the page the control lives on, so a toggle on a
   * public page (not just /admin/graphics) revalidates itself. */
  currentPath?: string;
};

export async function setGraphicPublished(input: SetGraphicPublishedInput) {
  const auth = await requireAdmin();

  const parsed = graphicPublishSchema.safeParse(input);
  if (!parsed.success) throw new Error(firstZodMessage(parsed.error));

  // The DB key must always correspond to a real graphic in the registry —
  // a Data Explorer dataset or a study, both keyed by slug.
  if (!graphicExists(parsed.data.datasetSlug, parsed.data.graphicId)) {
    throw new Error("Unknown graphic.");
  }

  // Hiding leaves publish_at untouched on purpose: it is the record of when
  // the graphic last went live (see 0054_graphic_publish_at.sql).
  const publishAt = parsed.data.published
    ? new Date(parsed.data.publishAt ?? Date.now()).toISOString()
    : undefined;

  const { error } = await createSupabaseServiceClient()
    .from("graphic_posts")
    .upsert(
      {
        dataset_slug: parsed.data.datasetSlug,
        graphic_id: parsed.data.graphicId,
        published: parsed.data.published,
        ...(publishAt !== undefined ? { publish_at: publishAt } : {}),
        created_by: auth.user.id,
        updated_at: new Date().toISOString(),
      },
      { onConflict: "dataset_slug,graphic_id" },
    );
  if (error) throw error;

  revalidateTag("graphic-posts", { expire: 0 });
  revalidatePath("/admin/graphics");
  if (parsed.data.currentPath) revalidatePath(parsed.data.currentPath);
  return { ...parsed.data, publishAt };
}
