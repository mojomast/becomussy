import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Proxy API calls to the backend during development
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://app:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
