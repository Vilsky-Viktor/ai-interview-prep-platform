export const SITE_NAME = "prepza."

// Private areas search engines shouldn't crawl; they need sign-in or a personal link anyway.
export const PRIVATE_PATHS = [
  "/api/",
  "/apply",
  "/company",
  "/generate",
  "/invite",
  "/join",
  "/monitoring",
  "/practice/history",
  "/practice/rounds",
  "/practice/*/start",
  "/sessions",
  "/settings",
  "/superadmin",
  "/top-up",
]

// Public pages listed in the sitemap.
export const PUBLIC_PATHS = [
  "/",
  "/pricing",
  "/privacy",
  "/terms",
  "/dpa",
  "/documents",
  "/faq",
  "/about",
  "/contact",
  "/practice",
]
