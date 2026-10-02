import type { ErrorEvent } from "@sentry/nextjs"

import { SENTRY_TRACES_SAMPLE_RATE } from "@/constants/security"

const EMAIL = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g

/** Replaces every email address in an event, however deep it sits. */
function scrub<T>(value: T): T {
  if (typeof value === "string") {
    return value.replace(EMAIL, "[email]") as T
  }

  if (Array.isArray(value)) {
    return value.map(scrub) as T
  }

  if (value && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, scrub(item)])
    ) as T
  }

  return value
}

/**
 * Options shared by the browser and the server. Without NEXT_PUBLIC_SENTRY_DSN nothing is sent,
 * so local development and builds report nothing. No personal data: users are known by id only.
 */
export function sentryOptions() {
  const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN

  return {
    dsn,
    enabled: Boolean(dsn),
    environment: process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT ?? "production",
    tracesSampleRate: SENTRY_TRACES_SAMPLE_RATE,
    sendDefaultPii: false,
    beforeSend: (event: ErrorEvent) => scrub(event),
  }
}
