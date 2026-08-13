"use server";

import { revalidatePath, revalidateTag } from "next/cache";
import { requireApologist } from "@/lib/permissions";
import { createSupabaseServiceClient } from "@/lib/supabase/server";
import { uuidSchema } from "@/lib/validation";
import type { ClaimSource, HubClaim } from "@/lib/types";

// Promoting a hub claim into the public library is always an explicit
// curation step — ingest never publishes on its own. Reads and writes go
// through the service client (claim_occurrences is deny-all, and drafts are
// invisible to the anon policy on claims); the gate is requireApologist(),
// matching every other hub write path.

function slugify(value: string): string {
  return value
    .toLowerCase()
    // NFKD splits accented letters into base + combining mark; the
    // non-alphanumeric collapse below then drops the marks, so "José" becomes
    // "jose" rather than "jos-".
    .normalize("NFKD")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80)
    .replace(/-+$/g, "");
}

async function uniqueSlug(base: string): Promise<string> {
  const supabase = createSupabaseServiceClient();
  const root = base || "claim";
  for (let attempt = 0; attempt < 50; attempt++) {
    const candidate = attempt === 0 ? root : `${root}-${attempt + 1}`;
    const { data, error } = await supabase
      .from("claims")
      .select("id")
      .eq("slug", candidate)
      .maybeSingle();
    if (error) throw error;
    if (!data) return candidate;
  }
  throw new Error("Could not generate a unique slug for this claim.");
}

function invalidate(currentPath?: string) {
  revalidateTag("claims", { expire: 0 });
  if (currentPath) revalidatePath(currentPath);
}

// ============================================================================
// Promote: create a new canonical claim from a hub claim, or attach the hub
// claim to one that already exists.
// ============================================================================

type PromoteToNewClaimInput = {
  hubClaimId: string;
  title: string;
  claimText: string;
  response: string;
  topicTags: string[];
  sources: ClaimSource[];
  currentPath?: string;
};

export async function promoteToNewClaim(input: PromoteToNewClaimInput) {
  const auth = await requireApologist();

  if (!uuidSchema.safeParse(input.hubClaimId).success) {
    throw new Error("Invalid claim id.");
  }
  const title = input.title.trim();
  const claimText = input.claimText.trim();
  const response = input.response.trim();
  if (!title) throw new Error("Give the claim a title.");
  if (!claimText) throw new Error("State the claim before promoting it.");
  if (!response) throw new Error("Write a response before promoting it.");

  const supabase = createSupabaseServiceClient();
  const hubClaim = await loadHubClaim(input.hubClaimId);

  const slug = await uniqueSlug(slugify(title));
  const { data: created, error: insertError } = await supabase
    .from("claims")
    .insert({
      slug,
      title,
      claim_text: claimText,
      response,
      // New claims always start as drafts — publishing is a separate,
      // deliberate action with its own source check.
      status: "draft",
      topic_tags: input.topicTags.map((t) => t.trim()).filter(Boolean),
      sources: input.sources.length ? input.sources : hubClaim.sources,
      created_by: auth.user.id,
    })
    .select("id, slug")
    .single();
  if (insertError) throw insertError;

  await linkHubClaim(hubClaim, created.id);
  invalidate(input.currentPath);
  return { id: created.id as string, slug: created.slug as string };
}

type AttachToClaimInput = {
  hubClaimId: string;
  claimId: string;
  currentPath?: string;
};

export async function attachHubClaimToClaim(input: AttachToClaimInput) {
  await requireApologist();

  if (
    !uuidSchema.safeParse(input.hubClaimId).success ||
    !uuidSchema.safeParse(input.claimId).success
  ) {
    throw new Error("Invalid id.");
  }

  const hubClaim = await loadHubClaim(input.hubClaimId);
  await linkHubClaim(hubClaim, input.claimId);
  invalidate(input.currentPath);
}

export async function detachHubClaim(input: {
  hubClaimId: string;
  currentPath?: string;
}) {
  await requireApologist();

  if (!uuidSchema.safeParse(input.hubClaimId).success) {
    throw new Error("Invalid claim id.");
  }

  const supabase = createSupabaseServiceClient();
  const hubClaim = await loadHubClaim(input.hubClaimId);
  if (!hubClaim.claim_id) return;

  const { error: occurrenceError } = await supabase
    .from("claim_occurrences")
    .delete()
    .eq("claim_id", hubClaim.claim_id)
    .eq("hub_claim_id", hubClaim.id);
  if (occurrenceError) throw occurrenceError;

  const { error } = await supabase
    .from("hub_claims")
    .update({ claim_id: null })
    .eq("id", hubClaim.id);
  if (error) throw error;

  invalidate(input.currentPath);
}

// ============================================================================
// Publish / unpublish
// ============================================================================

export async function setClaimStatus(input: {
  claimId: string;
  status: "draft" | "published";
  currentPath?: string;
}) {
  await requireApologist();

  if (!uuidSchema.safeParse(input.claimId).success) {
    throw new Error("Invalid claim id.");
  }

  const supabase = createSupabaseServiceClient();

  if (input.status === "published") {
    // The database enforces this too (claims_published_needs_sources), but
    // checking here turns a constraint violation into a readable message.
    const { data, error } = await supabase
      .from("claims")
      .select("sources")
      .eq("id", input.claimId)
      .maybeSingle();
    if (error) throw error;
    if (!data) throw new Error("Claim not found.");
    const sources = (data.sources ?? []) as ClaimSource[];
    if (sources.length === 0) {
      throw new Error("A claim needs at least one source before it can be published.");
    }
  }

  const { error } = await supabase
    .from("claims")
    .update({
      status: input.status,
      published_at: input.status === "published" ? new Date().toISOString() : null,
    })
    .eq("id", input.claimId);
  if (error) throw error;

  invalidate(input.currentPath);
}

// ============================================================================
// Internals
// ============================================================================

async function loadHubClaim(hubClaimId: string): Promise<HubClaim & { claim_id: string | null }> {
  const { data, error } = await createSupabaseServiceClient()
    .from("hub_claims")
    .select(
      "id, video_id, position, timestamp_seconds, excerpt, claim_summary, response, sources, claim_id, created_at, updated_at",
    )
    .eq("id", hubClaimId)
    .maybeSingle();
  if (error) throw error;
  if (!data) throw new Error("Hub claim not found.");
  return data as HubClaim & { claim_id: string | null };
}

// Records both halves of the mapping: the hub claim points at its canonical
// claim, and an occurrence row records that this video made it. The
// occurrence is upserted on (claim_id, video_id) so re-promoting a second
// claim from the same video doesn't double-count reach.
async function linkHubClaim(
  hubClaim: HubClaim & { claim_id: string | null },
  claimId: string,
) {
  const supabase = createSupabaseServiceClient();

  const { error: occurrenceError } = await supabase
    .from("claim_occurrences")
    .upsert(
      {
        claim_id: claimId,
        video_id: hubClaim.video_id,
        hub_claim_id: hubClaim.id,
        timestamp_seconds: hubClaim.timestamp_seconds,
      },
      { onConflict: "claim_id,video_id" },
    );
  if (occurrenceError) throw occurrenceError;

  const { error } = await supabase
    .from("hub_claims")
    .update({ claim_id: claimId })
    .eq("id", hubClaim.id);
  if (error) throw error;
}
