/**
 * Apologetics Hub — step 2: fetch a video's caption transcript with no
 * external dependencies (no yt-dlp required). Scrapes the caption track list
 * out of the watch page's ytInitialPlayerResponse, then downloads the
 * preferred track as json3.
 *
 * This is fragile by nature — YouTube changes these internal payloads
 * without notice. If it breaks, don't block ingestion on it: fall back to
 * `yt-dlp --write-auto-sub --sub-lang en --skip-download <url>` if installed,
 * or paste a transcript manually into the output file's "transcript" field
 * and set "source" to "manual". See APOLOGETICS_HUB_INGEST.md.
 *
 * Usage:
 *   npx tsx scripts/hub-fetch-transcript.ts --video <youtubeVideoId> [--out file.json]
 */
import { writeFileSync } from "node:fs";

const USER_AGENT =
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36";

type CaptionTrack = {
  baseUrl: string;
  languageCode: string;
  kind?: string; // "asr" = auto-generated
  vssId?: string;
};

function parseArgs() {
  const argv = process.argv.slice(2);
  const get = (flag: string) => {
    const i = argv.indexOf(flag);
    return i >= 0 ? argv[i + 1] : undefined;
  };
  const video = get("--video");
  if (!video) throw new Error("Missing --video <youtubeVideoId>");
  return { video, out: get("--out") ?? `${video}.transcript.json` };
}

// Extracts a balanced bracketed substring (e.g. a JSON array) starting at the
// given open-bracket index — a non-greedy regex would cut off at the first
// nested "]", which caption-track objects frequently contain.
function extractBalanced(
  text: string,
  startIdx: number,
  open: string,
  close: string,
): string | null {
  let depth = 0;
  for (let i = startIdx; i < text.length; i++) {
    if (text[i] === open) depth++;
    else if (text[i] === close) {
      depth--;
      if (depth === 0) return text.slice(startIdx, i + 1);
    }
  }
  return null;
}

function pickTrack(tracks: CaptionTrack[]): CaptionTrack {
  const manualEn = tracks.find(
    (t) => t.languageCode === "en" && t.kind !== "asr",
  );
  if (manualEn) return manualEn;
  const anyEn = tracks.find((t) => t.languageCode === "en");
  if (anyEn) return anyEn;
  const asrEn = tracks.find((t) => t.vssId?.startsWith("a.en"));
  if (asrEn) return asrEn;
  return tracks[0];
}

type Json3Event = {
  tStartMs?: number;
  segs?: { utf8?: string }[];
};

async function main() {
  const args = parseArgs();

  const watchRes = await fetch(
    `https://www.youtube.com/watch?v=${args.video}`,
    { headers: { "user-agent": USER_AGENT, "accept-language": "en-US" } },
  );
  if (!watchRes.ok) {
    throw new Error(`Failed to fetch watch page: ${watchRes.status}`);
  }
  const html = await watchRes.text();

  const marker = '"captionTracks":';
  const markerIdx = html.indexOf(marker);
  if (markerIdx === -1) {
    throw new Error(
      "No captionTracks found — this video may have no captions, or YouTube changed its page payload. See the fallback ladder in APOLOGETICS_HUB_INGEST.md.",
    );
  }
  const arrStart = html.indexOf("[", markerIdx);
  const arrText = extractBalanced(html, arrStart, "[", "]");
  if (!arrText) throw new Error("Could not parse captionTracks array.");
  const tracks = JSON.parse(arrText) as CaptionTrack[];
  if (tracks.length === 0) throw new Error("captionTracks array was empty.");

  const track = pickTrack(tracks);
  const isAsr = track.kind === "asr" || track.vssId?.startsWith("a.") === true;
  console.log(
    `Using track: ${track.languageCode}${isAsr ? " (auto-generated)" : ""}`,
  );

  const captionsRes = await fetch(`${track.baseUrl}&fmt=json3`, {
    headers: { "user-agent": USER_AGENT },
  });
  if (!captionsRes.ok) {
    throw new Error(`Failed to fetch captions: ${captionsRes.status}`);
  }
  const captionsJson = (await captionsRes.json()) as { events?: Json3Event[] };

  const segments = (captionsJson.events ?? [])
    .filter((e) => e.segs && e.tStartMs != null)
    .map((e) => ({
      start: Math.round((e.tStartMs ?? 0) / 1000),
      text: (e.segs ?? []).map((s) => s.utf8 ?? "").join(""),
    }))
    .filter((s) => s.text.trim() && s.text.trim() !== "\n");

  const transcript = segments.map((s) => s.text.trim()).join(" ").replace(/\s+/g, " ").trim();

  const output = {
    youtube_video_id: args.video,
    source: "timedtext" as const,
    language: track.languageCode,
    auto_generated: isAsr,
    transcript,
    segments,
  };

  writeFileSync(args.out, JSON.stringify(output, null, 2), "utf8");
  console.log(`Wrote ${args.out} (${segments.length} segments, ${transcript.length} chars).`);
}

main().catch((err) => {
  console.error("\nFailed:", err);
  process.exit(1);
});
