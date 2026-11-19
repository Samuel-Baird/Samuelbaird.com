import type { NextConfig } from "next";

// Omni is served at https://samuelbaird.com/omni (forwarded by the samuelbaird-com Worker over a service binding).
// The old host keeps its MCP endpoints (/api/mcp, /mcp) for existing connectors: worker.ts rewrites them, since Next
// only allows external rewrites outside the base path. Every page on the old host 301s to the new path.
const LEGACY = [{ type: "host" as const, value: "omni.samuelbaird.com" }];

const nextConfig: NextConfig = {
  basePath: "/omni",
  // Canonical MCP URL is /omni/mcp (same as every other MCP: <base>/mcp); /omni/api/mcp stays as an alias.
  async rewrites() {
    return [{ source: "/mcp", destination: "/api/mcp" }];
  },
  async redirects() {
    return [
      { source: "/", has: LEGACY, destination: "https://samuelbaird.com/omni", permanent: true, basePath: false },
      { source: "/:path((?!omni(?:/|$)|api/|_next/).+)", has: LEGACY, destination: "https://samuelbaird.com/omni/:path", permanent: true, basePath: false },
    ];
  },
};

export default nextConfig;
