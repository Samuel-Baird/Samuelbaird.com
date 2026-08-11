import type { NextConfig } from "next";

// Allowlist for next/image's optimizer. Covers the three external image
// sources actually used: YouTube channel avatars, Google account photos
// (auth avatar), and this project's own Supabase storage bucket (study
// preview images). Derived from NEXT_PUBLIC_SUPABASE_URL rather than
// hardcoding the project ref, so it still works if the project ever moves.
const supabaseHostname = process.env.NEXT_PUBLIC_SUPABASE_URL
  ? new URL(process.env.NEXT_PUBLIC_SUPABASE_URL).hostname
  : undefined;

const nextConfig: NextConfig = {
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
      ...(supabaseHostname
        ? [{ protocol: "https" as const, hostname: supabaseHostname }]
        : []),
    ],
  },
};

export default nextConfig;
