import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  serverExternalPackages: ["turndown", "cheerio"],
};

export default nextConfig;
