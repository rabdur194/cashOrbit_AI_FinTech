import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Standalone output is useful for Docker; Vercel ignores it and works fine.
  output: "standalone",

  // Prevent accidental exposure of server-only env vars
  experimental: {
    // Keep default settings; safe for Vercel
  },
};

export default nextConfig;
