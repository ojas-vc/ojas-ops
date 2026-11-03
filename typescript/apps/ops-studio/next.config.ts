import type { NextConfig } from "next";

const backendUrl = process.env.NEXT_PUBLIC_OJAS_OPS_API_URL || "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  transpilePackages: ["@ojas-ops/sdk", "@ojas-ops/ui"],
  async rewrites() {
    return [
      {
        source: "/api/ojas/:path*",
        destination: `${backendUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
