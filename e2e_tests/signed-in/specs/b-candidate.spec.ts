import { expect, test } from "../fixtures"
import { createCompany, createInterview, inviteCandidate } from "../helpers/api"
import { inviteToken } from "../helpers/db"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { answered } from "../helpers/session"
import { ownerEmail, throwawayEmail } from "../helpers/users"
import { MIN_QUESTION_SECONDS } from "../constants"

// A candidate takes an interview from their invite link: picks, changes the pick, goes on, lets a
// question's time run out, and finishes.
test("candidate takes the interview from the invite link", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const email = throwawayEmail("candidate")
  await inviteCandidate(owner, interviewId, email)

  const candidate = await signInAs(email)
  await visit(candidate, `/invite/${await inviteToken(email)}`)
  await expect(candidate.getByText(`${company.name} invited you to interview.`)).toBeVisible()
  await expect(candidate.getByText("You can change your pick until you press Next question.")).toBeVisible()
  await shot(candidate, "invite")
  await candidate.getByRole("button", { name: "Accept & Start" }).click()
  await expect(candidate).toHaveURL(/\/sessions\//)

  // The pick can change until Next: one option marked at a time.
  const question = candidate.locator("[role=heading]").first()
  const options = candidate.getByRole("main").locator("button[aria-pressed]")
  await expect(options.first()).toBeVisible()
  await shot(candidate, "question")
  await options.nth(0).click()
  await expect(options.nth(0)).toHaveAttribute("aria-pressed", "true")
  await options.nth(1).click()
  await expect(options.nth(1)).toHaveAttribute("aria-pressed", "true")
  await expect(options.nth(0)).toHaveAttribute("aria-pressed", "false")
  await shot(candidate, "pick-changed")
  const first = await question.textContent()
  await candidate.getByRole("button", { name: "Next question" }).click()
  await expect(question).not.toHaveText(first ?? "")
  await expect.poll(() => answered(candidate)).toBe("1")

  // No pick: the question's clock runs out and the next one opens by itself.
  const second = await question.textContent()
  await expect(candidate.getByRole("timer")).toBeVisible()
  await shot(candidate, "timer")
  await expect(question).not.toHaveText(second ?? "", {
    timeout: (MIN_QUESTION_SECONDS + 10) * 1000,
  })
  await expect.poll(() => answered(candidate)).toBe("2")
  await shot(candidate, "after-timeout")

  await candidate.getByRole("button", { name: "Finish interview" }).click()
  await expect(candidate.getByRole("dialog")).toContainText("Finish the whole interview?")
  await shot(candidate, "finish-dialog")
  await candidate.getByRole("dialog").getByRole("button", { name: "Finish", exact: true }).click()
  await expect(candidate.getByText("You have finished the interview. Good luck!")).toBeVisible()
  await shot(candidate, "done")

  // The company sees them finished.
  await visit(owner, `/company/${company.id}/interviews/${interviewId}?tab=candidates`)
  await expect(owner.getByText(email, { exact: true }).first()).toBeVisible()
  await shot(owner, "owner-candidates")
})
