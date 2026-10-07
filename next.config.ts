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

const nextConfig: NextConfig = {
  async headers() {
    return [{ source: "/:path*", headers: securityHeaders }];
  },
  experimental: {
    serverActions: {
      // Default is 1MB, which rejects the 25MB study PDF uploads that
      // createStudy accepts.
      bodySizeLimit: "30mb",
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
