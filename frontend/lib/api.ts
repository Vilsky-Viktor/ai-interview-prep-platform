import { DEFAULT_LOCALE } from "@/constants/i18n"
import { firebaseAuth } from "@/lib/firebase"

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message)
  }
}

/** The message in an error response: a string for errors the services raise, the first of a
list when input fails validation. */
export function errorDetail(body: unknown): string | null {
  const detail = (body as { detail?: unknown } | null)?.detail

  if (typeof detail === "string") {
    return detail
  }

  const first = Array.isArray(detail) ? detail[0]?.msg : null

  return typeof first === "string" ? first.replace(/^Value error, /, "") : null
}

/** The signed-in user's token, and the interface language for the services' messages. */
export async function authHeaders(): Promise<Record<string, string>> {
  // Right after page load Firebase may still be restoring the signed-in user.
  const auth = await firebaseAuth()
  await auth.authStateReady()
  const token = await auth.currentUser?.getIdToken()
  // The page's own language: a first visit has no cookie yet.
  const language = {
    "Accept-Language": document.documentElement.lang || DEFAULT_LOCALE,
  }

  return token ? { ...language, Authorization: `Bearer ${token}` } : language
}

export async function apiFetch<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(await authHeaders()) },
  })

  if (!response.ok) {
    const detail = errorDetail(await response.json().catch(() => null))

    throw new ApiError(
      response.status,
      detail ?? `Request failed with status ${response.status}`
    )
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json()
}

/** The service's own message for nothing left to use (402), rate limits (429), invalid
input (422) and a temporary pause (503), whose rules live in the backend; the fallback for
anything else. */
export function apiErrorMessage(error: unknown, fallback: string): string {
  if (
    error instanceof ApiError &&
    [402, 422, 429, 503].includes(error.status)
  ) {
    return error.message
  }

  return fallback
}
