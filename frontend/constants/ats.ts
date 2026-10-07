// The ATSs a company can connect, each with its own page at /integrations/<id>.
export const ATS_PROVIDERS = [
  { id: "workable", name: "Workable", logo: "/ats/workable.svg" },
  { id: "greenhouse", name: "Greenhouse", logo: "/ats/greenhouse.png" },
] as const

export type AtsProvider = (typeof ATS_PROVIDERS)[number]

// Where a Workable admin makes the API access token prepza needs, as Workable's menus name it,
// and the scopes it needs: reading jobs and candidates, and writing results to candidates.
export const WORKABLE_TOKEN_PATH = [
  "Settings",
  "Integrations",
  "Apps",
  "API access tokens",
]
export const WORKABLE_SCOPES = ["r_jobs", "r_candidates", "w_candidates"]

// Where a Greenhouse admin makes the API credential, its type, and what it may do: read jobs,
// their posts and stages, and write notes on candidates.
export const GREENHOUSE_CREDENTIAL_PATH = [
  "Configure",
  "Dev Center",
  "API Credential Management",
]
export const GREENHOUSE_CREDENTIAL_TYPE = "Harvest V3 (OAuth)"
export const GREENHOUSE_PERMISSIONS = [
  "Jobs",
  "Job Posts",
  "Job Interview Stages",
  "Notes",
]
// Where the web hook is set up, and the event it sends.
export const GREENHOUSE_WEBHOOK_PATH = ["Configure", "Dev Center", "Web Hooks"]
export const GREENHOUSE_WEBHOOK_EVENT = "Candidate or Prospect Stage Change"
