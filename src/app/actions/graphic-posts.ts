"use server";

import { revalidatePath, revalidateTag } from "next/cache";
import { requireAdmin } from "@/lib/auth";
import { graphicExists } from "@/lib/graphic-posts";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { firstZodMessage, graphicPostSchema, graphicPublishSchema } from "@/lib/validation";

// RLS on graphic_posts is deny-all (supabase/migrations/0049_graphic_posts.sql,
// 0051_graphic_published.sql); the gate is requireAdmin() and all access
// goes through the service client, matching src/app/actions/hub-status.ts.
// `posted`/`posted_dates` and `published` are written by two separate
// actions below, each upserting only its own columns, so one control can
// never clobber the other's state.

type SetGraphicPostStatusInput = {
  datasetSlug: string;
  graphicId: string;
  posted: boolean;
  postedDates: string;
  /** Site-relative path of the page the control lives on, so a toggle on a
   * public page (not just /admin/graphics) revalidates itself. */
  currentPath?: string;
};

export async function setGraphicPostStatus(input: SetGraphicPostStatusInput) {
  const auth = await requireAdmin();

  const parsed = graphicPostSchema.safeParse(input);
  if (!parsed.success) throw new Error(firstZodMessage(parsed.error));

  // The DB key must always correspond to a real graphic in the registry —
  // a Data Explorer dataset or a study, both keyed by slug.
  if (!graphicExists(parsed.data.datasetSlug, parsed.data.graphicId)) {
    throw new Error("Unknown graphic.");
  }

  const { error } = await createSupabaseServiceClient()
    .from("graphic_posts")
    .upsert(
      {
        dataset_slug: parsed.data.datasetSlug,
        graphic_id: parsed.data.graphicId,
        posted: parsed.data.posted,
        posted_dates: parsed.data.postedDates,
        created_by: auth.user.id,
        updated_at: new Date().toISOString(),
      },
      { onConflict: "dataset_slug,graphic_id" },
    );
  if (error) throw error;

  revalidateTag("graphic-posts", { expire: 0 });
  revalidatePath("/admin/graphics");
  if (parsed.data.currentPath) revalidatePath(parsed.data.currentPath);
  return parsed.data;
}

type SetGraphicPublishedInput = {
  datasetSlug: string;
  graphicId: string;
  published: boolean;
  currentPath?: string;
};

export async function setGraphicPublished(input: SetGraphicPublishedInput) {
  const auth = await requireAdmin();

  const parsed = graphicPublishSchema.safeParse(input);
  if (!parsed.success) throw new Error(firstZodMessage(parsed.error));

  if (!graphicExists(parsed.data.datasetSlug, parsed.data.graphicId)) {
    throw new Error("Unknown graphic.");
  }

  const { error } = await createSupabaseServiceClient()
    .from("graphic_posts")
    .upsert(
      {
        dataset_slug: parsed.data.datasetSlug,
        graphic_id: parsed.data.graphicId,
        published: parsed.data.published,
        created_by: auth.user.id,
        updated_at: new Date().toISOString(),
      },
      { onConflict: "dataset_slug,graphic_id" },
    );
  if (error) throw error;

  revalidateTag("graphic-posts", { expire: 0 });
  revalidatePath("/admin/graphics");
  if (parsed.data.currentPath) revalidatePath(parsed.data.currentPath);
  return parsed.data;
}
