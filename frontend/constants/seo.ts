export const SITE_NAME = "prepza."

// Private areas search engines shouldn't crawl; they need sign-in or a personal link anyway.
export const PRIVATE_PATHS = [
  "/api/",
  "/company",
  "/generate",
  "/invite",
  "/join",
  "/monitoring",
  "/rounds",
  "/sessions",
  "/settings",
  "/share",
]

// Public pages listed in the sitemap, besides public preparations.
export const PUBLIC_PATHS = ["/", "/library", "/pricing", "/privacy", "/terms"]

// Public preparations in the sitemap, read a page of 100 at a time.
export const SITEMAP_PREPARATIONS = 1000
export const SITEMAP_PAGE = 100
