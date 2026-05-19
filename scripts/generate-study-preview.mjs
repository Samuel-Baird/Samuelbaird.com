// Generate a preview image for a study.
//
// Usage:  node scripts/generate-study-preview.mjs <slug> [--skip-existing] [--force-source=pdf_figure|url_scrape|ai_dataviz]
//
// Cascade (each step short-circuits on success):
//   1. PDF figure  — extract every embedded image on a page with a
//                    "Figure N" / "Fig. N" / "Chart N" caption from the uploaded
//                    PDF, then ask Claude Haiku 4.5 (if ANTHROPIC_API_KEY is set)
//                    which figure best illustrates the study's key finding.
//                    Falls back to the largest candidate when no key is set,
//                    only one candidate exists, or `--no-llm` is passed.
//   2. URL scrape  — fetch external_url, look for og:image / twitter:image.
//   3. AI data-viz — render an SVG findings card from the study's `findings` array.
//                    AI-sourced previews set preview_image_is_ai=true.

import { createClient } from "@supabase/supabase-js";
import { readFileSync } from "node:fs";
import { PNG } from "pngjs";

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

async function tryPdfFigure() {
  if (forceSource && forceSource !== "pdf_figure") return null;
  if (!study.pdf_path) return null;
  try {
    const { data: dl, error } = await supabase.storage
      .from("studies")
      .download(study.pdf_path);
    if (error || !dl) return null;
    const ab = await dl.arrayBuffer();

    // pdfjs-dist legacy build runs in Node without a worker. Suppress its
    // warning about deprecated APIs we don't use.
    const pdfjs = await import("pdfjs-dist/legacy/build/pdf.mjs");
    const doc = await pdfjs.getDocument({
      data: new Uint8Array(ab),
      disableFontFace: true,
      isEvalSupported: false,
      useSystemFonts: false,
      useWorkerFetch: false,
      disableWorker: true,
    }).promise;

    const CAPTION_RE = /\b(Figure|Fig\.|Chart|Table)\s*\d+/gi;
    const candidates = []; // { img, area, caption, page }
    const maxPages = Math.min(doc.numPages, 40);
    const debug = args.includes("--debug");

    for (let p = 1; p <= maxPages; p++) {
      const page = await doc.getPage(p);
      const text = await page.getTextContent();
      const joined = text.items.map((it) => it.str ?? "").join(" ");
      const matches = [...joined.matchAll(CAPTION_RE)];
      if (matches.length === 0) continue;
      // First caption on the page is usually the figure label; pull a longer
      // snippet for context (used in the Claude prompt and as the final caption).
      const idx = matches[0].index ?? joined.indexOf(matches[0][0]);
      const captionLine = joined.slice(idx, idx + 220).split(/(?<=\.)\s|\n/)[0].trim();

      const ops = await page.getOperatorList();
      const { OPS } = pdfjs;
      const imageOpNames = [
        OPS.paintImageXObject,
        OPS.paintImageXObjectRepeat,
        OPS.paintJpegXObject,
        OPS.paintInlineImageXObject,
      ];
      for (let i = 0; i < ops.fnArray.length; i++) {
        if (!imageOpNames.includes(ops.fnArray[i])) continue;
        const arg = ops.argsArray[i];
        const objId = Array.isArray(arg) ? arg[0] : arg;
        if (typeof objId !== "string") continue;
        let img = null;
        try {
          img = await new Promise((resolve) => {
            let settled = false;
            const done = (v) => {
              if (settled) return;
              settled = true;
              resolve(v);
            };
            try {
              page.objs.get(objId, done);
            } catch {
              done(null);
            }
            setTimeout(() => done(null), 2000);
          });
        } catch {
          img = null;
        }
        if (!img || !img.data || !img.width || !img.height) continue;
        if (img.width < 200 || img.height < 150) continue;
        candidates.push({
          img,
          area: img.width * img.height,
          caption: captionLine,
          page: p,
        });
      }
    }

    if (debug) {
      console.warn(
        `PDF debug: ${maxPages} pages scanned, ${candidates.length} candidate figures`,
      );
      for (const c of candidates) {
        console.warn(`  p${c.page} ${c.img.width}x${c.img.height} — ${c.caption.slice(0, 80)}`);
      }
    }
    if (candidates.length === 0) return null;

    const picked = await pickBestFigure(candidates);
    const png = imageToPng(picked.img);
    if (!png) return null;

    return {
      buf: png,
      ext: "png",
      contentType: "image/png",
      source: "pdf_figure",
      isAi: false,
      caption: `${picked.caption} (page ${picked.page})`,
    };
  } catch (e) {
    console.warn("PDF figure extraction failed:", e.message);
    return null;
  }
}

async function pickBestFigure(candidates) {
  const debug = args.includes("--debug");
  const apiKey = process.env.ANTHROPIC_API_KEY ?? env.ANTHROPIC_API_KEY;

  if (!apiKey || candidates.length < 2 || args.includes("--no-llm")) {
    // Largest figure on a captioned page is the fallback heuristic.
    return candidates.slice().sort((a, b) => b.area - a.area)[0];
  }

  const list = candidates
    .map((c, i) => `[${i}] page ${c.page}, ${c.img.width}x${c.img.height} — ${c.caption}`)
    .join("\n");
  const prompt = `You are choosing which figure from a research paper would make the best preview image for a public-facing summary card.

Study title: ${study.title}
Abstract: ${study.abstract ?? "(not available)"}
Key findings:
${(study.findings ?? []).map((f) => `- ${f}`).join("\n") || "(not available)"}

Candidate figures extracted from the PDF (each is an image + nearby caption text):
${list}

Pick the ONE figure that best illustrates the paper's most interesting finding for a general audience. Prefer charts/graphs over tables, and prefer figures whose caption clearly maps to a key finding above. Avoid decorative images, author photos, logos, and methodology diagrams.

Respond with ONLY the index number in brackets, e.g. "[2]". No other text.`;

  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-haiku-4-5-20251001",
        max_tokens: 20,
        messages: [{ role: "user", content: prompt }],
      }),
    });
    if (!res.ok) {
      if (debug) console.warn(`Claude pick failed: ${res.status} ${await res.text()}`);
      return candidates.slice().sort((a, b) => b.area - a.area)[0];
    }
    const json = await res.json();
    const text = json.content?.[0]?.text ?? "";
    const m = text.match(/\[(\d+)\]/) ?? text.match(/(\d+)/);
    const idx = m ? Number(m[1]) : NaN;
    if (Number.isInteger(idx) && idx >= 0 && idx < candidates.length) {
      if (debug) console.warn(`Claude picked candidate [${idx}]`);
      return candidates[idx];
    }
    if (debug) console.warn(`Claude returned unparseable response: ${text}`);
  } catch (e) {
    if (debug) console.warn("Claude pick errored:", e.message);
  }
  return candidates.slice().sort((a, b) => b.area - a.area)[0];
}

// pdfjs image buffer kinds: 1=GRAYSCALE_1BPP, 2=RGB_24BPP, 3=RGBA_32BPP
function imageToPng(img) {
  const { data, width, height, kind } = img;
  const png = new PNG({ width, height });
  const out = png.data;
  if (kind === 3 || data.length === width * height * 4) {
    out.set(data);
  } else if (kind === 2 || data.length === width * height * 3) {
    for (let i = 0, j = 0; i < width * height; i++) {
      out[j++] = data[i * 3];
      out[j++] = data[i * 3 + 1];
      out[j++] = data[i * 3 + 2];
      out[j++] = 255;
    }
  } else if (data.length === width * height) {
    for (let i = 0, j = 0; i < width * height; i++) {
      out[j++] = data[i];
      out[j++] = data[i];
      out[j++] = data[i];
      out[j++] = 255;
    }
  } else {
    return null;
  }
  return PNG.sync.write(png);
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

const result = (await tryPdfFigure()) ?? (await tryUrlScrape()) ?? tryDataviz();

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
