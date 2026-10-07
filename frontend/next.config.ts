import { withSentryConfig } from "@sentry/nextjs/config"
import type { NextConfig } from "next"
import createNextIntlPlugin from "next-intl/plugin"

const nextConfig: NextConfig = {
  output: "standalone",
  // The preview pictures' font files, read at request time, go into the standalone server.
  outputFileTracingIncludes: {
    "/preview": ["./assets/fonts/**"],
    "/opengraph-image": ["./assets/fonts/**"],
  },
  // Titles, canonical addresses and hreflang always go in the <head>, for every visitor and
  // crawler: Next.js would otherwise stream a slow page's metadata into the body, which only
  // crawlers that run JavaScript read.
  htmlLimitedBots: /.*/,
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
  // Companies' pages moved from /company to /companies; links in emails and notifications sent
  // before still work.
  async redirects() {
    return [
      { source: "/company", destination: "/companies", permanent: true },
      {
        source: "/company/:path*",
        destination: "/companies/:path*",
        permanent: true,
      },
    ]
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

// Errors reach Sentry through /monitoring on our own domain, so ad blockers don't drop them and
// the Content-Security-Policy needs no new origin. Source maps upload only with SENTRY_AUTH_TOKEN.
// next-intl reads the interface language per request in i18n/request.ts.
const withNextIntl = createNextIntlPlugin()

export default withSentryConfig(withNextIntl(nextConfig), {
  tunnelRoute: "/monitoring",
  silent: true,
  telemetry: false,
})
