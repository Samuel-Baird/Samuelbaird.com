import type { NextConfig } from "next";

// Allowlist for next/image's optimizer. Covers the three external image
// sources actually used: YouTube channel avatars, Google account photos
// (auth avatar), and this project's own Supabase storage bucket (study
// preview images). Derived from NEXT_PUBLIC_SUPABASE_URL rather than
// hardcoding the project ref, so it still works if the project ever moves.
const supabaseHostname = process.env.NEXT_PUBLIC_SUPABASE_URL
  ? new URL(process.env.NEXT_PUBLIC_SUPABASE_URL).hostname
  : undefined;

// Baseline hardening headers. No CSP yet: Next's inline scripts need a
// nonce setup first. The site embeds no iframes, so framing is denied.
const securityHeaders = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  {
    key: "Permissions-Policy",
    value: "camera=(), microphone=(), geolocation=()",
  },
];

// Served at https://samuelbaird.com/latter-day-stats (forwarded by the samuelbaird-com Worker over a service binding).
// The old host 301s every page there; its /api, /auth and /mcp paths keep working (rewritten by
// worker.ts) so
// webhooks, crons, the MCP endpoint and in-flight sign-ins are not broken.
const LEGACY = [{ type: "host" as const, value: "latterdaystats.samuelbaird.com" }];

const nextConfig: NextConfig = {
  basePath: "/latter-day-stats",
  async redirects() {
    return [
      // Compare was removed; keep old links and bookmarks working.
      { source: "/compare", destination: "/channels", permanent: true },
      // The contact form (and its thank-you page) was replaced by an email address.
      { source: "/contact/thank-you", destination: "/contact", permanent: true },
      { source: "/", has: LEGACY, destination: "https://samuelbaird.com/latter-day-stats", permanent: true, basePath: false },
      { source: "/:path((?!latter-day-stats(?:/|$)|api/|auth/|mcp(?:/|$)|_next/).+)", has: LEGACY, destination: "https://samuelbaird.com/latter-day-stats/:path", permanent: true, basePath: false },
    ];
  },
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }];
  },
  experimental: {
    serverActions: {
      // Default is 1MB, which rejects the 25MB study PDF uploads that
      // createStudy accepts.
      bodySizeLimit: "30mb",
      // Pages are proxied from samuelbaird.com, so the browser Origin differs from the deployment host.
      allowedOrigins: ["samuelbaird.com", "latterdaystats.samuelbaird.com"],
    },
  },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "*.ggpht.com" },
      { protocol: "https", hostname: "*.googleusercontent.com" },
      { protocol: "https", hostname: "i.ytimg.com" },
      ...(supabaseHostname
        ? [{ protocol: "https" as const, hostname: supabaseHostname }]
        : []),
    ],
  },
};

export default nextConfig;
