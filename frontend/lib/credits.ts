import { ApiError } from "@/lib/api"

// Fired when the user's credits may have changed, so the header's balance reloads.
const CREDITS_CHANGED = "prepza:credits-changed"

export function announceCreditsChanged() {
  window.dispatchEvent(new Event(CREDITS_CHANGED))
}

export function onCreditsChanged(listener: () => void) {
  window.addEventListener(CREDITS_CHANGED, listener)

  return () => window.removeEventListener(CREDITS_CHANGED, listener)
}

/** A "Top up" button for the toast when the error is a lack of credits (402). */
export function topUpAction(
  error: unknown,
  label: string,
  onClick: () => void
) {
  return error instanceof ApiError && error.status === 402
    ? { action: { label, onClick } }
    : undefined
}
