import type { NextConfig } from "next";

// Peepstone is served at https://samuelbaird.com/peepstone (proxied from samuelbaird.com's vercel.json).
// The old host keeps its MCP endpoint (/mcp) for existing connectors: vercel.json rewrites it, since Next
// only allows external rewrites outside the base path. Every page on the old host 301s to the new path.
const LEGACY = [{ type: "host" as const, value: "peepstone.vercel.app" }];

const nextConfig: NextConfig = {
  basePath: "/peepstone",
  // turndown and cheerio are bundled (no serverExternalPackages): OpenNext's Cloudflare build copies external packages
  // as symlinks, which fails on Windows without Developer Mode, and bundling works on Vercel and Workers alike.
  turbopack: {
    resolveAlias: {
      // The MCP SDK picks its default JSON Schema validator by export condition. Next bundles the Node one (Ajv), which
      // compiles schemas with `new Function`, and Cloudflare Workers forbid that; mcp-handler compiles schemas at import,
      // so /mcp would 500 on Workers. The browser/workerd shim uses @cfworker/json-schema, which runs everywhere.
      "@modelcontextprotocol/server/_shims": "./node_modules/@modelcontextprotocol/server/dist/shimsBrowser.mjs",
    },
  },
  async redirects() {
    return [
      { source: "/", has: LEGACY, destination: "https://samuelbaird.com/peepstone", permanent: true, basePath: false },
      { source: "/:path((?!peepstone(?:/|$)|mcp$|_next/).+)", has: LEGACY, destination: "https://samuelbaird.com/peepstone/:path", permanent: true, basePath: false },
    ];
  },
};

export default nextConfig;
