import { auth } from "@/lib/firebase"

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message)
  }
}

export async function authHeaders(): Promise<Record<string, string>> {
  // Right after page load Firebase may still be restoring the signed-in user.
  await auth.authStateReady()
  const token = await auth.currentUser?.getIdToken()

  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...(await authHeaders()) },
  })

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const detail = typeof body?.detail === "string" ? body.detail : null

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

export function apiErrorMessage(error: unknown, fallback: string): string {
  if (error instanceof ApiError && error.status === 429) {
    return error.message
  }

  return fallback
}
