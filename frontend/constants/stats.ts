// The admin zone's stats tab: each card in order, the service whose stats it comes from (its
// API path) and the metric there. Paid is in cents, in the currency billing gives.
export const STATS_CARDS = [
  { source: "companies", metric: "companies" },
  { source: "companies", metric: "verified" },
  { source: "companies", metric: "interviews" },
  { source: "companies", metric: "invited" },
  { source: "companies", metric: "finished" },
  { source: "rounds", metric: "practice" },
  { source: "billing", metric: "top_ups" },
  { source: "billing", metric: "paid" },
  { source: "billing", metric: "credits_spent" },
] as const

export const STATS_SOURCES = ["companies", "rounds", "billing"] as const

// Months the stats tab's menu offers, this one included.
export const STATS_MONTHS = 12

// All time is on in the address: `?month=2026-10&all=1`; the month stays for turning it off.
export const ALL_TIME = "1"

// A month in the address and the API: "2026-10".
export const MONTH_PATTERN = /^\d{4}-(0[1-9]|1[0-2])$/
