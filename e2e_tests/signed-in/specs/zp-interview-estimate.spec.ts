import type { Page } from "@playwright/test"

import { expect, test } from "../fixtures"
import { api, createCompany, deleteOwnCompanies, templatesBySize } from "../helpers/api"
import { openTab, visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { throwawayEmail } from "../helpers/users"

type Detail = {
  topics: { id: string; question_limit: number }[]
  question_seconds: number
  total_questions: number
  total_minutes: number
}

const SECONDS = 30

async function detail(page: Page, interviewId: string) {
  return api<Detail>(page, "GET", `/companies/interviews/${interviewId}`)
}

/** The estimate's three numbers as the page shows them. */
async function expectEstimate(page: Page, found: Detail) {
  const estimate = page.getByTestId("interview-estimate")
  await expect(estimate.getByTestId("total-questions")).toContainText(String(found.total_questions))
  await expect(estimate.getByTestId("question-seconds")).toContainText(
    String(found.question_seconds)
  )
  await expect(estimate.getByTestId("total-minutes")).toContainText(String(found.total_minutes))
}

// The topics tab adds up what each candidate gets: the total questions, the time per question
// and the whole interview's time, as the API counts them. A topic's number changed on the tab,
// to 0 too, changes them; the candidates and settings tabs don't show them.
test("the topics tab shows what the interview adds up to and follows each topic's number", async ({
  signInAs,
}) => {
  test.setTimeout(180_000)
  const owner = await signInAs(throwawayEmail("interview-estimate"))
  const company = await createCompany(owner)
  const template = (await templatesBySize(owner)).find((found) => found.topic_count >= 2)
  test.skip(!template, "No local template with two topics")

  try {
    const { id } = await api<{ id: string }>(
      owner,
      "POST",
      `/companies/interviews/from-template?company_id=${company.id}`,
      { template_id: template!.id }
    )
    await api(owner, "PATCH", `/companies/interviews/${id}/settings`, {
      question_seconds: SECONDS,
    })
    const url = `/companies/${company.id}/interviews/${id}`
    const before = await detail(owner, id)
    expect(before.question_seconds).toBe(SECONDS)
    expect(before.total_minutes).toBe(Math.ceil((before.total_questions * SECONDS) / 60))

    await visit(owner, url)
    await expectEstimate(owner, before)
    await shot(owner, "interview-estimate")

    // The first topic down to 1 question.
    const first = owner.getByRole("main").getByRole("spinbutton").first()
    await first.fill("1")
    await first.press("Enter")
    const one = before.total_questions - before.topics[0].question_limit + 1
    await expect(owner.getByTestId("total-questions")).toContainText(String(one))
    const afterOne = await detail(owner, id)
    expect(afterOne.total_questions).toBe(one)
    await expectEstimate(owner, afterOne)

    // Then to 0: the topic is left out, and its questions with it.
    await first.fill("0")
    await first.press("Enter")
    await expect(owner.getByTestId("total-questions")).toContainText(String(one - 1))
    const afterZero = await detail(owner, id)
    expect(afterZero.topics[0].question_limit).toBe(0)
    await expectEstimate(owner, afterZero)
    await shot(owner, "interview-estimate-zero")

    // Not on the other tabs.
    await openTab(owner, "?tab=candidates")
    await expect(owner.getByTestId("interview-estimate")).toHaveCount(0)
    await openTab(owner, "?tab=settings")
    await expect(owner.getByTestId("interview-estimate")).toHaveCount(0)
  } finally {
    await deleteOwnCompanies(owner)
  }
})

// Every topic at 0 would leave candidates nothing: the last one is refused, with the reason.
test("the last topic with questions can't be set to 0", async ({ signInAs }) => {
  test.setTimeout(180_000)
  const owner = await signInAs(throwawayEmail("interview-last-topic"))
  const company = await createCompany(owner)
  const template = (await templatesBySize(owner)).find((found) => found.topic_count >= 2)
  test.skip(!template, "No local template with two topics")

  try {
    const { id } = await api<{ id: string }>(
      owner,
      "POST",
      `/companies/interviews/from-template?company_id=${company.id}`,
      { template_id: template!.id }
    )
    const { topics } = await detail(owner, id)

    for (const topic of topics.slice(1)) {
      await api(owner, "PUT", `/companies/interviews/${id}/topics/${topic.id}/limit`, { limit: 0 })
    }

    await visit(owner, `/companies/${company.id}/interviews/${id}`)
    const first = owner.getByRole("main").getByRole("spinbutton").first()
    await first.fill("0")
    await first.press("Enter")

    const refused = owner.locator('[data-sonner-toast][data-type="error"]')
    await expect(refused).toContainText("An interview needs at least one topic with questions.")
    await expect(first).toHaveValue(String(topics[0].question_limit))
    expect((await detail(owner, id)).topics[0].question_limit).toBe(topics[0].question_limit)
  } finally {
    await deleteOwnCompanies(owner)
  }
})
