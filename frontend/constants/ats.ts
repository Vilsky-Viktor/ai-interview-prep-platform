// Where a Workable admin makes the API access token prepza needs, as Workable's menus name it,
// and the scopes it needs: reading jobs and candidates, and writing results to candidates.
export const WORKABLE_TOKEN_PATH = [
  "Settings",
  "Integrations",
  "Apps",
  "API access tokens",
]
export const WORKABLE_SCOPES = ["r_jobs", "r_candidates", "w_candidates"]
