// The company's API keys and web hooks, as the api service's /manage routes return them (they
// aren't in its public OpenAPI, so they're written here).
export type ApiKey = {
  id: string
  name: string
  // The key's first characters, to tell keys apart.
  shown: string
  created_at: string
  // Null: it never expires.
  expires_at: string | null
  expired: boolean
  last_used_at: string | null
}

export type ApiWebhook = {
  id: string
  url: string
  created_at: string
  // Events stopped reaching it after days of retries; the next one it takes clears this.
  failing: boolean
  // The member who added it is no longer an owner or admin: it gets no events.
  stopped: boolean
}

// A send in a web hook's delivery log; `result` is "delivered", "skipped", the status the
// endpoint answered, or the error on the way.
export type WebhookAttempt = {
  event_type: string
  ok: boolean
  result: string
  at: string
}

export type ApiSettings = {
  keys: ApiKey[]
  webhooks: ApiWebhook[]
  // When a new key can expire: in "1", "3", "6" or "12" months, or "never".
  expiries: string[]
}
