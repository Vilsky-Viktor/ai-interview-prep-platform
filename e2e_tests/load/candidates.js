// Many candidates taking interviews at once. Setup makes throwaway owners, each with a company
// and a test from a local template, its shareable link on; each iteration is a new candidate who
// signs in, opens the link, starts, and answers until the interview is done. e2e_tests/load.sh
// deletes every throwaway account (and so the companies) afterwards, with clean.js.
import exec from "k6/execution"
import { Rate } from "k6/metrics"

import { candidateEmail, signUp } from "./lib/accounts.js"
import {
  API_P95,
  CANDIDATES_PER_COMPANY,
  ERROR_RATE,
  ITERATIONS,
  VUS,
} from "./lib/config.js"
import { createCompany, takeInterview } from "./lib/interviews.js"

const finished = new Rate("interviews_finished")

export const options = {
  scenarios: {
    candidates: { executor: "per-vu-iterations", vus: VUS, iterations: ITERATIONS, maxDuration: "15m" },
  },
  setupTimeout: "10m",
  thresholds: {
    "http_req_duration{endpoint:link}": [API_P95],
    "http_req_duration{endpoint:start}": [API_P95],
    "http_req_duration{endpoint:step}": [API_P95],
    "http_req_duration{endpoint:answer}": [API_P95],
    "http_req_failed{phase:load}": [ERROR_RATE],
    interviews_finished: ["rate>0.99"],
  },
}

export function setup() {
  const run = Date.now().toString(36)
  const count = Math.ceil((VUS * ITERATIONS) / CANDIDATES_PER_COMPANY)
  const companies = []

  for (let index = 0; index < count; index++) {
    companies.push(createCompany(run, index))
  }

  return { run, companies }
}

export default function (data) {
  const index = exec.scenario.iterationInTest
  const company = data.companies[Math.floor(index / CANDIDATES_PER_COMPANY)]
  const token = signUp(candidateEmail(data.run, index))
  finished.add(takeInterview(token, company.link))
}
