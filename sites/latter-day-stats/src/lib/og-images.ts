import type { Metadata } from "next";
import { SITE_URL } from "@/lib/site";

// Open Graph / Twitter card images are static PNGs under public/og/, rendered
// before `next build` by scripts/build-og-images.tsx (designs in
// src/lib/og.tsx). They used to be generated per request with next/og, whose
// satori/resvg wasm made the Worker too big for the Workers free plan.
//
// Files: og/<section>.png for the fixed pages, og/channels/<slug>.png and
// og/studies/<slug>.png per channel and study. A channel or study added after
// the last build has no file yet; worker.ts answers those misses with the
// section image (og/channels.png, og/studies.png).

export type OgSection =
  | "home"
  | "about"
  | "channels"
  | "contact"
  | "donate"
  | "methodology"
  | "studies";

const SIZE = { width: 1200, height: 630 };

function imageMetadata(path: string, alt: string): Pick<Metadata, "openGraph" | "twitter"> {
  const url = `${SITE_URL}/og/${path}`;
  return {
    openGraph: { images: [{ url, ...SIZE, alt, type: "image/png" }] },
    twitter: { card: "summary_large_image", images: [{ url, alt }] },
  };
}

export function sectionOgImage(section: OgSection, alt: string) {
  return imageMetadata(`${section}.png`, alt);
}

/** Per-channel card. Pass the channel's canonical slug, not the URL param. */
export function channelOgImage(slug: string) {
  return imageMetadata(`channels/${encodeURIComponent(slug)}.png`, "Latter-day Stats — Channel");
}

export function studyOgImage(slug: string) {
  return imageMetadata(`studies/${encodeURIComponent(slug)}.png`, "Latter-day Stats — Study");
}
