import type { NextConfig } from "next";

// Peepstone is served at https://samuelbaird.com/peepstone (forwarded by the samuelbaird-com Worker over a service binding).

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
};

export default nextConfig;
