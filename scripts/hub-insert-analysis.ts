/**
 * Apologetics Hub — step 3: validate an analysis JSON (written by hand
 * during a Claude Code ingest session, per APOLOGETICS_HUB_INGEST.md) and
 * write it to hub_videos / hub_claims / hub_transcripts.
 *
 * Usage:
 *   npx tsx scripts/hub-insert-analysis.ts <analysis.json>
 *
 * Input shape — see APOLOGETICS_HUB_INGEST.md for the full field-by-field
 * spec and a worked example:
 *   {
 *     "channel_id": "<uuid, from hub-list-new-videos.ts output>",
 *     "youtube_video_id": "...", "title": "...", "published_at": "...",
 *     "duration_seconds": 1234, "thumbnail_url": "...",
 *     "view_count": 12345, "expected_views": 6789,
 *     "summary": "...", "debunkability": 1-10,
 *     "lds_relevant": true,  // false hides the video from the public feed —
 *                            // some tracked channels don't address Latter-day
 *                            // Saints/Mormonism in every upload; the row,
 *                            // transcript, and any claims are still retained
 *     "claims": [{ "timestamp_seconds", "excerpt", "claim_summary",
 *                  "response", "sources": [{"title","url","note"}] }, ...],
 *     "transcript": { "source", "transcript", "segments" }  // or "transcript_file": "path.json"
 *   }
 */
import { config as loadEnv } from "dotenv";
loadEnv({ path: ".env.local" });

import { readFileSync } from "node:fs";
import { createClient } from "@supabase/supabase-js";
import { z } from "zod";
import { computePriorityScore } from "./hub-priority";

const sourceSchema = z.object({
  title: z.string().trim().min(1).max(300),
  url: z
    .string()
    .trim()
    .min(1)
    .refine((v) => /^https?:\/\//.test(v), { message: "source.url must be an http(s) link" }),
  note: z.string().trim().min(1).max(1000),
});

const claimSchema = z.object({
  timestamp_seconds: z.number().int().min(0),
  excerpt: z.string().trim().min(1).max(600),
  claim_summary: z.string().trim().min(1).max(500),
  response: z.string().trim().min(1).max(4000),
  sources: z.array(sourceSchema).min(1),
});

const transcriptSchema = z.object({
  source: z.enum(["timedtext", "yt-dlp", "manual"]),
  transcript: z.string().trim().min(1),
  segments: z.array(z.object({ start: z.number(), text: z.string() })).nullable().optional(),
});

const analysisSchema = z.object({
  channel_id: z.uuid(),
  youtube_video_id: z.string().regex(/^[A-Za-z0-9_-]{8,20}$/),
  title: z.string().trim().min(1).max(500),
  published_at: z.iso.datetime({ offset: true }).or(z.iso.date()),
  duration_seconds: z.number().int().min(0).nullable().optional(),
  thumbnail_url: z.string().trim().url().nullable().optional(),
  view_count: z.number().int().min(0).default(0),
  expected_views: z.number().min(0).nullable().optional(),
  summary: z.string().trim().max(2000).default(""),
  debunkability: z.number().int().min(1).max(10).nullable().optional(),
  // Required so every analysis pass makes an explicit call — false hides
  // the video from the public feed (see APOLOGETICS_HUB_INGEST.md Step 3).
  lds_relevant: z.boolean(),
  claims: z.array(claimSchema).default([]),
  transcript: transcriptSchema.nullable().optional(),
  transcript_file: z.string().trim().min(1).nullable().optional(),
});

function supabaseClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) {
    throw new Error(
      "Missing NEXT_PUBLIC_SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env.local",
    );
  }
  return createClient(url, key, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}

async function main() {
  const file = process.argv[2];
  if (!file) {
    throw new Error("Usage: npx tsx scripts/hub-insert-analysis.ts <analysis.json>");
  }

  const raw = JSON.parse(readFileSync(file, "utf8"));
  const parsed = analysisSchema.safeParse(raw);
  if (!parsed.success) {
    console.error("Analysis JSON failed validation:");
    for (const issue of parsed.error.issues) {
      console.error(`  - ${issue.path.join(".")}: ${issue.message}`);
    }
    process.exit(1);
  }
  const analysis = parsed.data;

  let transcript = analysis.transcript ?? null;
  if (!transcript && analysis.transcript_file) {
    const fromFile = JSON.parse(readFileSync(analysis.transcript_file, "utf8"));
    const parsedTranscript = transcriptSchema.safeParse(fromFile);
    if (!parsedTranscript.success) {
      throw new Error(
        `transcript_file "${analysis.transcript_file}" does not match the transcript shape.`,
      );
    }
    transcript = parsedTranscript.data;
  }
  if (!transcript) {
    console.warn(
      "⚠ No transcript provided (neither `transcript` nor `transcript_file`) — proceeding without one. Re-analysis later will need a fresh fetch.",
    );
  }

  const priorityScore = computePriorityScore({
    viewCount: analysis.view_count,
    expectedViews: analysis.expected_views ?? null,
    debunkability: analysis.debunkability ?? null,
    publishedAt: analysis.published_at,
  });

  const supabase = supabaseClient();

  const { data: video, error: videoError } = await supabase
    .from("hub_videos")
    .upsert(
      {
        channel_id: analysis.channel_id,
        youtube_video_id: analysis.youtube_video_id,
        title: analysis.title,
        published_at: analysis.published_at,
        duration_seconds: analysis.duration_seconds ?? null,
        thumbnail_url: analysis.thumbnail_url ?? null,
        summary: analysis.summary,
        view_count: analysis.view_count,
        view_count_updated_at: new Date().toISOString(),
        expected_views: analysis.expected_views ?? null,
        debunkability: analysis.debunkability ?? null,
        lds_relevant: analysis.lds_relevant,
        priority_score: priorityScore,
        analyzed_at: new Date().toISOString(),
      },
      { onConflict: "youtube_video_id" },
    )
    .select("id")
    .single();
  if (videoError) throw videoError;
  const videoId = video.id as string;

  const { error: deleteClaimsError } = await supabase
    .from("hub_claims")
    .delete()
    .eq("video_id", videoId);
  if (deleteClaimsError) throw deleteClaimsError;

  if (analysis.claims.length > 0) {
    const { error: claimsError } = await supabase.from("hub_claims").insert(
      analysis.claims.map((claim, i) => ({
        video_id: videoId,
        position: i + 1,
        timestamp_seconds: claim.timestamp_seconds,
        excerpt: claim.excerpt,
        claim_summary: claim.claim_summary,
        response: claim.response,
        sources: claim.sources,
      })),
    );
    if (claimsError) throw claimsError;
  }

  if (transcript) {
    const { error: transcriptError } = await supabase
      .from("hub_transcripts")
      .upsert(
        {
          video_id: videoId,
          transcript: transcript.transcript,
          segments: transcript.segments ?? null,
          source: transcript.source,
          fetched_at: new Date().toISOString(),
        },
        { onConflict: "video_id" },
      );
    if (transcriptError) throw transcriptError;
  }

  console.log(`✓ ${analysis.title}`);
  console.log(`  ${analysis.claims.length} claim(s), priority_score=${priorityScore ?? "n/a"}`);
  console.log(`  /apologetics-hub/${analysis.youtube_video_id}`);
}

main().catch((err) => {
  console.error("\nFailed:", err);
  process.exit(1);
});
