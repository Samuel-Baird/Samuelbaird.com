// Generate a preview image for a study.
//
// Usage:  node scripts/generate-study-preview.mjs <slug> [--skip-existing] [--force-source=url_scrape|ai_dataviz]
//
// Cascade (each step short-circuits on success):
//   1. URL scrape  — fetch external_url, look for og:image / twitter:image. Sets preview_image_source='url_scrape'.
//   2. AI data-viz — render an SVG findings card from the study's `findings` array.
//                    Sets preview_image_source='ai_dataviz', preview_image_is_ai=true.
//
// PDF figure extraction is not yet implemented (would require pdfjs-dist + image
// classification). The agent flow can still upload a manual preview through the
// admin form when a real figure is needed.

import { createClient } from "@supabase/supabase-js";
import { readFileSync } from "node:fs";

const env = Object.fromEntries(
  readFileSync(new URL("../.env.local", import.meta.url), "utf8")
    .split("\n")
    .filter((l) => l.includes("="))
    .map((l) => {
      const i = l.indexOf("=");
      return [l.slice(0, i).trim(), l.slice(i + 1).trim()];
    }),
);

const supabase = createClient(
  env.NEXT_PUBLIC_SUPABASE_URL,
  env.SUPABASE_SERVICE_ROLE_KEY,
);

const args = process.argv.slice(2);
const slug = args.find((a) => !a.startsWith("--"));
const skipExisting = args.includes("--skip-existing");
const forceSource = args
  .find((a) => a.startsWith("--force-source="))
  ?.split("=")[1];

if (!slug) {
  console.error("Usage: node scripts/generate-study-preview.mjs <slug>");
  process.exit(1);
}

const { data: study, error: studyErr } = await supabase
  .from("studies")
  .select("*")
  .eq("slug", slug)
  .maybeSingle();
if (studyErr) throw studyErr;
if (!study) {
  console.error(`No study with slug "${slug}"`);
  process.exit(1);
}

if (study.preview_image_path && skipExisting) {
  console.log(`Skipping ${slug} — already has preview at ${study.preview_image_path}`);
  process.exit(0);
}

async function tryUrlScrape() {
  if (forceSource && forceSource !== "url_scrape") return null;
  if (!study.external_url) return null;
  try {
    const res = await fetch(study.external_url, {
      headers: { "user-agent": "Mozilla/5.0 LatterDayStatsBot" },
      redirect: "follow",
    });
    if (!res.ok) return null;
    const html = await res.text();
    const match =
      html.match(/<meta[^>]+property=["']og:image["'][^>]+content=["']([^"']+)["']/i) ||
      html.match(/<meta[^>]+name=["']twitter:image["'][^>]+content=["']([^"']+)["']/i) ||
      html.match(/<meta[^>]+content=["']([^"']+)["'][^>]+property=["']og:image["']/i);
    if (!match) return null;
    const imgUrl = new URL(match[1], study.external_url).toString();
    const imgRes = await fetch(imgUrl);
    if (!imgRes.ok) return null;
    const ct = imgRes.headers.get("content-type") || "image/jpeg";
    const ext = ct.includes("png") ? "png" : ct.includes("webp") ? "webp" : "jpg";
    const buf = Buffer.from(await imgRes.arrayBuffer());
    const altMatch =
      html.match(/<meta[^>]+property=["']og:image:alt["'][^>]+content=["']([^"']+)["']/i);
    return {
      buf,
      ext,
      contentType: ct,
      source: "url_scrape",
      isAi: false,
      caption: altMatch ? altMatch[1] : "Preview image from the publisher",
    };
  } catch (e) {
    console.warn("URL scrape failed:", e.message);
    return null;
  }
}

function escapeXml(s) {
  return String(s).replace(/[<>&"']/g, (c) =>
    ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", '"': "&quot;", "'": "&apos;" }[c]),
  );
}

function wrapText(text, maxChars) {
  const words = text.split(/\s+/);
  const lines = [];
  let line = "";
  for (const w of words) {
    if ((line + " " + w).trim().length > maxChars) {
      if (line) lines.push(line);
      line = w;
    } else {
      line = (line + " " + w).trim();
    }
  }
  if (line) lines.push(line);
  return lines;
}

function tryDataviz() {
  if (forceSource && forceSource !== "ai_dataviz") return null;
  const findings = (study.findings ?? []).filter(Boolean);
  if (findings.length === 0) return null;

  const width = 1200;
  const height = 675; // 16:9
  const accent = "#9c4221";
  const ink = "#1f1b16";
  const muted = "#6b6157";
  const bg = "#fbf7f1";

  const top = findings.slice(0, 3);
  const cardY = 180;
  const cardHeight = 360;
  const gap = 30;
  const cardWidth = (width - 80 - gap * (top.length - 1)) / top.length;

  const cards = top
    .map((finding, i) => {
      const x = 40 + i * (cardWidth + gap);
      const numMatch = finding.match(/(\d[\d.,]*\s*%?)/);
      const stat = numMatch ? numMatch[1].trim() : `#${i + 1}`;
      const rest = numMatch ? finding.replace(numMatch[1], "").trim() : finding;
      const lines = wrapText(rest, 32).slice(0, 6);
      return `
    <g>
      <rect x="${x}" y="${cardY}" width="${cardWidth}" height="${cardHeight}" rx="20" fill="white" stroke="#e8dfd1" />
      <text x="${x + 30}" y="${cardY + 90}" font-family="Georgia, serif" font-size="68" font-weight="700" fill="${accent}">${escapeXml(stat)}</text>
      ${lines
        .map(
          (line, li) =>
            `<text x="${x + 30}" y="${cardY + 150 + li * 28}" font-family="-apple-system, system-ui, sans-serif" font-size="20" fill="${ink}">${escapeXml(line)}</text>`,
        )
        .join("")}
    </g>`;
    })
    .join("");

  const titleLines = wrapText(study.title, 60).slice(0, 2);
  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}">
  <rect width="${width}" height="${height}" fill="${bg}" />
  <text x="40" y="60" font-family="-apple-system, system-ui, sans-serif" font-size="14" font-weight="600" fill="${accent}" letter-spacing="2">KEY FINDINGS</text>
  ${titleLines
    .map(
      (l, i) =>
        `<text x="40" y="${100 + i * 38}" font-family="Georgia, serif" font-size="32" font-weight="700" fill="${ink}">${escapeXml(l)}</text>`,
    )
    .join("")}
  ${cards}
  <text x="40" y="${height - 30}" font-family="-apple-system, system-ui, sans-serif" font-size="14" fill="${muted}">Generated from this study's findings — not an original figure. latter-day-stats</text>
</svg>`;

  return {
    buf: Buffer.from(svg, "utf8"),
    ext: "svg",
    contentType: "image/svg+xml",
    source: "ai_dataviz",
    isAi: true,
    caption: "Generated from this study's findings — not an original figure.",
  };
}

const result = (await tryUrlScrape()) ?? tryDataviz();

if (!result) {
  console.error(
    `No preview could be generated for ${slug}. Need external_url with og:image, or non-empty findings array.`,
  );
  process.exit(2);
}

const path = `${slug}/preview.${result.ext}`;
const { error: uploadErr } = await supabase.storage
  .from("studies")
  .upload(path, result.buf, {
    contentType: result.contentType,
    upsert: true,
  });
if (uploadErr) throw uploadErr;

const { error: updateErr } = await supabase
  .from("studies")
  .update({
    preview_image_path: path,
    preview_image_source: result.source,
    preview_image_caption: result.caption,
    preview_image_is_ai: result.isAi,
  })
  .eq("id", study.id);
if (updateErr) throw updateErr;

console.log(
  `✓ ${slug} — ${result.source}${result.isAi ? " (AI)" : ""} → ${path}`,
);
