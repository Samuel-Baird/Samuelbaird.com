import type { NextConfig } from "next";

// Peepstone is served at https://samuelbaird.com/peepstone (proxied from samuelbaird.com's vercel.json).
// The old host keeps its MCP endpoint (/mcp) for existing connectors: vercel.json rewrites it, since Next
// only allows external rewrites outside the base path. Every page on the old host 301s to the new path.
const LEGACY = [{ type: "host" as const, value: "peepstone.vercel.app" }];

const nextConfig: NextConfig = {
  basePath: "/peepstone",
  serverExternalPackages: ["turndown", "cheerio"],
  async redirects() {
    return [
      { source: "/", has: LEGACY, destination: "https://samuelbaird.com/peepstone", permanent: true, basePath: false },
      { source: "/:path((?!peepstone(?:/|$)|mcp$|_next/).+)", has: LEGACY, destination: "https://samuelbaird.com/peepstone/:path", permanent: true, basePath: false },
    ];
  },
};

export default nextConfig;
