// The pages with an info button; each has its text under "pageHelp.<key>" in the messages.
export const PAGE_HELP_KEYS = [
  "landing",
  "companies",
  "pickCompany",
  "interviews",
  "newInterview",
  "reviewTopics",
  "generating",
  "interviewTopics",
  "interviewCandidates",
  "interviewSettings",
  "tryInterview",
  "candidate",
  "templates",
  "template",
  "team",
  "integrations",
  "ats",
  "slack",
  "api",
  "referrals",
  "billing",
] as const

// A company's tabs and an interview's tabs, each with its own text.
export const COMPANY_TAB_HELP = {
  interviews: "interviews",
  templates: "templates",
  members: "team",
  integrations: "integrations",
  referrals: "referrals",
  billing: "billing",
} as const

export const INTERVIEW_TAB_HELP = {
  topics: "interviewTopics",
  candidates: "interviewCandidates",
  settings: "interviewSettings",
} as const
