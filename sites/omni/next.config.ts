import type { NextConfig } from "next";

// Omni is served at https://samuelbaird.com/omni (proxied from samuelbaird.com's vercel.json).
// The old host keeps its MCP endpoint (/api/mcp) for existing connectors: vercel.json rewrites it, since Next
// only allows external rewrites outside the base path. Every page on the old host 301s to the new path.
const LEGACY = [{ type: "host" as const, value: "omni.samuelbaird.com" }];

const nextConfig: NextConfig = {
  basePath: "/omni",
  async redirects() {
    return [
      { source: "/", has: LEGACY, destination: "https://samuelbaird.com/omni", permanent: true, basePath: false },
      { source: "/:path((?!omni(?:/|$)|api/|_next/).+)", has: LEGACY, destination: "https://samuelbaird.com/omni/:path", permanent: true, basePath: false },
    ];
  },
};

export default nextConfig;
