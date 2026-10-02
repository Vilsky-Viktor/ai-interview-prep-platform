import { auth } from "@/lib/firebase"

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

export async function authHeaders(): Promise<Record<string, string>> {
  // Right after page load Firebase may still be restoring the signed-in user.
  await auth.authStateReady()
  const token = await auth.currentUser?.getIdToken()

  return token ? { Authorization: `Bearer ${token}` } : {}
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

/** The service's own message for nothing left to use (402), rate limits (429) and invalid
input (422), whose rules live in the backend; the fallback for anything else. */
export function apiErrorMessage(error: unknown, fallback: string): string {
  if (
    error instanceof ApiError &&
    (error.status === 402 || error.status === 429 || error.status === 422)
  ) {
    return error.message
  }

  return fallback
}
