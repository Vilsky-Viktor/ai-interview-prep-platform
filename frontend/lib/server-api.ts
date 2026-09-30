import { cookies } from "next/headers"

import { TOKEN_COOKIE } from "@/constants/auth"

// Signed out, not allowed, missing, or a malformed id in the URL: the page shows
// "not found" or a sign-in prompt.
const EXPECTED_MISSES = [401, 403, 404, 422]

/**
 * Server-side API call, with the user's token when signed in. Null when the resource is
 * missing or not visible to the user; other failures throw so the error page shows.
 */
export async function serverFetch<T>(path: string): Promise<T | null> {
  const token = (await cookies()).get(TOKEN_COOKIE)?.value
  const response = await fetch(`${process.env.API_URL}/api${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
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
