import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    serverActions: {
      // Default is 1MB, which rejects the 25MB study PDF uploads that
      // createStudy accepts.
      bodySizeLimit: "30mb",
    },
  },
};

export default nextConfig;
