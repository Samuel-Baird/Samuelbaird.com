"use server";

import { revalidatePath } from "next/cache";
import { requireAdmin } from "@/lib/auth";
import { getGraphic } from "@/lib/data-explorer";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { firstZodMessage, graphicPostSchema } from "@/lib/validation";

// RLS on graphic_posts is deny-all (supabase/migrations/0049_graphic_posts.sql);
// the gate is requireAdmin() and all access goes through the service client,
// matching src/app/actions/hub-status.ts.

type SetGraphicPostStatusInput = {
  datasetSlug: string;
  graphicId: string;
  posted: boolean;
  postedDates: string;
};

export async function setGraphicPostStatus(input: SetGraphicPostStatusInput) {
  const auth = await requireAdmin();

  const parsed = graphicPostSchema.safeParse(input);
  if (!parsed.success) throw new Error(firstZodMessage(parsed.error));

  // The DB key must always correspond to a real graphic in the registry.
  if (!getGraphic(parsed.data.datasetSlug, parsed.data.graphicId)) {
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

  revalidatePath("/admin/graphics");
  return parsed.data;
}
