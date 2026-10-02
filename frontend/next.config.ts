import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  output: "standalone",
  // Bind mounts on Colima do not deliver file events, so the dev server polls.
  watchOptions: {
    pollIntervalMs: 1000,
  },
  // Production builds use Turbopack and skip the webpack hook below, which only sets up polling
  // for the dev server (that runs with --webpack). Without this, Next 16 refuses to build.
  turbopack: {},
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        poll: 1000,
        aggregateTimeout: 300,
      }
    }

    return config
  },
  // In `pnpm dev` there is no gateway in front of Next, so proxy the API to it.
  async rewrites() {
    if (!process.env.API_URL) {
      return []
    }

    return [
      {
        source: "/api/:path*",
        destination: `${process.env.API_URL}/api/:path*`,
      },
    ]
  },
}

export default nextConfig
