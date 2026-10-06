import { expect, type Page, test } from "@playwright/test"

import { API_URL, MIN_QUESTION_SECONDS } from "../constants"
import { tokenOf } from "./sign-in"
import { randomId } from "./users"

type Template = { id: string; title: string; topic_count: number }

/** Calls the API as the user signed in on `page`; the response's JSON, if any. The test process
 * isn't the browser, so it reaches the gateway by its name on the stack's network. */
export async function api<T>(page: Page, method: string, path: string, body?: unknown) {
  const response = await page.request.fetch(`${API_URL}${path}`, {
    method,
    headers: { Authorization: `Bearer ${await tokenOf(page)}` },
    data: body,
  })
  expect(response.ok(), `${method} ${path} -> ${response.status()}`).toBe(true)
  const text = await response.text()

  return (text ? JSON.parse(text) : null) as T
}

/** A throwaway company; names are unique across prepza, so each gets a random part. */
export async function createCompany(page: Page, name = `E2E ${randomId()}`) {
  const company = await api<{ id: string }>(page, "POST", "/companies/companies", { name })

  return { id: company.id, name }
}

/** The local English templates a company can use, fewest topics first, or a skip when there's
 * none: interviews are made from templates here, since generating one needs OpenAI. */
export async function templatesBySize(page: Page): Promise<Template[]> {
  const templates = await api<Template[]>(
    page,
    "GET",
    "/library/templates/copyable?language=en&limit=50"
  )
  test.skip(
    templates.length === 0,
    "No usable templates locally: an interview can't be made without a real (OpenAI) generation"
  )

  return templates.sort((a, b) => a.topic_count - b.topic_count)
}

/** An interview made from the smallest template a company can use, with the shortest time per
 * question. */
export async function createInterview(page: Page, companyId: string) {
  const [template] = await templatesBySize(page)
  const interview = await api<{ id: string }>(
    page,
    "POST",
    `/companies/interviews/from-template?company_id=${companyId}`,
    { template_id: template.id }
  )
  await api(page, "PATCH", `/companies/interviews/${interview.id}/settings`, {
    question_seconds: MIN_QUESTION_SECONDS,
  })

  return interview.id
}

/** Invites one candidate to the interview. */
export async function inviteCandidate(page: Page, interviewId: string, email: string) {
  await api(page, "POST", `/companies/interviews/${interviewId}/candidates`, { email })
}

/** Deletes the companies the signed-in throwaway user owns: only ever the tests' own. */
export async function deleteOwnCompanies(page: Page) {
  const companies = await api<{ id: string; role: string }[]>(
    page,
    "GET",
    "/companies/companies?limit=100"
  )

  for (const company of companies.filter((item) => item.role === "owner")) {
    await api(page, "DELETE", `/companies/companies/${company.id}`)
  }
}
