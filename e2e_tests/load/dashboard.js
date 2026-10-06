// Company owners on their dashboard. Setup makes throwaway companies, each with a test from a
// local template that three candidates (what a company's welcome credits pay for) have taken;
// each iteration an owner opens the tests list, a test, its candidates (best grade first, then
// filtered), a scorecard and the candidates report. e2e_tests/load.sh deletes every throwaway
// account (and so the companies) afterwards, with clean.js.
import { sleep } from "k6"

import { candidateEmail, signUp } from "./lib/accounts.js"
import {
  API_P95,
  CANDIDATES_PER_COMPANY,
  DASHBOARD_COMPANIES,
  DURATION,
  ERROR_RATE,
  THINK_SECONDS,
  VUS,
} from "./lib/config.js"
import { api, must } from "./lib/http.js"
import { createCompany, takeInterview } from "./lib/interviews.js"

const ENDPOINTS = ["companies", "interviews", "interview", "candidates", "filtered", "scorecard", "report"]

export const options = {
  scenarios: { owners: { executor: "constant-vus", vus: VUS, duration: DURATION } },
  setupTimeout: "10m",
  thresholds: {
    ...Object.fromEntries(ENDPOINTS.map((name) => [`http_req_duration{endpoint:${name}}`, [API_P95]])),
    "http_req_failed{phase:load}": [ERROR_RATE],
  },
}

export function setup() {
  const run = Date.now().toString(36)
  const companies = []

  for (let index = 0; index < DASHBOARD_COMPANIES; index++) {
    const company = createCompany(run, index)

    for (let seat = 0; seat < CANDIDATES_PER_COMPANY; seat++) {
      const candidate = signUp(candidateEmail(run, index * CANDIDATES_PER_COMPANY + seat))

      if (!takeInterview(candidate, company.link, 0)) {
        throw new Error("setup failed: a candidate couldn't finish")
      }
    }

    const listed = must("GET", `/companies/interviews/${company.interview}/candidates`, company.owner)
    companies.push({ ...company, candidates: listed.map((item) => item.id) })
  }

  const filters = must("GET", "/companies/interviews/candidates/filters").filters

  return { companies, filters }
}

export default function (data) {
  const company = data.companies[(__VU - 1) % data.companies.length]
  const { owner, interview } = company
  const test = `/companies/interviews/${interview}`
  const filter = data.filters[__ITER % data.filters.length]
  const candidate = company.candidates[__ITER % company.candidates.length]

  api("GET", "/companies/companies", owner, undefined, "companies")
  api("GET", `/companies/interviews?company_id=${company.company}`, owner, undefined, "interviews")
  sleep(THINK_SECONDS)
  api("GET", test, owner, undefined, "interview")
  api("GET", `${test}/candidates?sort=grade`, owner, undefined, "candidates")
  sleep(THINK_SECONDS)
  api("GET", `${test}/candidates?sort=date&status=${filter}`, owner, undefined, "filtered")
  sleep(THINK_SECONDS)
  api("GET", `${test}/candidates/${candidate}`, owner, undefined, "scorecard")
  sleep(THINK_SECONDS)
  api("GET", `${test}/report`, owner, undefined, "report")
  sleep(THINK_SECONDS)
}
