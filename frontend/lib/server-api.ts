import { cookies } from "next/headers"

import { TOKEN_COOKIE } from "@/constants/auth"
import { REFERRAL_COOKIE } from "@/constants/referral"

// Signed out, not allowed, missing, or a malformed id in the URL: the page shows
// "not found" or a sign-in prompt.
const EXPECTED_MISSES = [401, 403, 404, 422]

/**
 * Server-side API call, with the user's token when signed in. Null when the resource is
 * missing or not visible to the user; other failures throw so the error page shows.
 */
export async function serverFetch<T>(path: string): Promise<T | null> {
  const jar = await cookies()
  const token = jar.get(TOKEN_COOKIE)?.value
  const referral = jar.get(REFERRAL_COOKIE)?.value
  const headers: Record<string, string> = {}

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  // As the browser's own calls do: the first visit after sign-up may happen here.
  if (referral) {
    headers.Cookie = `${REFERRAL_COOKIE}=${referral}`
  }

  const response = await fetch(`${process.env.API_URL}/api${path}`, {
    headers,
    cache: "no-store",
  })

  if (EXPECTED_MISSES.includes(response.status)) {
    return null
  }

  if (!response.ok) {
    throw new Error(`API request ${path} failed with status ${response.status}`)
  }

  return response.json()
}
