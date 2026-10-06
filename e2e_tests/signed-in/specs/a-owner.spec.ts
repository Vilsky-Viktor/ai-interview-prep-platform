import { expect, test } from "../fixtures"
import { templatesBySize } from "../helpers/api"
import { openTab, visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail, randomId, throwawayEmail } from "../helpers/users"

// A company owner: a company, an interview from a template, its questions, a candidate invited.
test("owner creates a company, an interview from a template and invites a candidate", async ({
  signInAs,
}) => {
  const owner = await signInAs(ownerEmail())
  await expect(owner.getByText("No companies yet.")).toBeVisible()
  await shot(owner, "companies-empty")

  // The home page's start: the description, then which company. Going on would generate the
  // interview with OpenAI, so the company is created from the companies page instead.
  await visit(owner, "/")
  await owner.getByLabel("Job description").fill("Backend developer: SQL basics and indexes.")
  await owner.locator("form").getByRole("button", { name: "Create an interview" }).click()
  await expect(owner.getByText("What's your company called?")).toBeVisible()
  await shot(owner, "home-company-step", false)

  const name = `E2E Owner ${randomId()}`
  await visit(owner, "/company")
  await owner.getByRole("button", { name: "New company" }).click()
  await owner.getByRole("dialog").getByLabel("Company name").fill(name)
  await shot(owner, "new-company-dialog")
  await owner.getByRole("dialog").getByRole("button", { name: "Create" }).click()
  await expect(owner).toHaveURL(/\/company\/[^/]+\/interviews$/)
  await expect(owner.getByRole("heading", { name })).toBeVisible()
  await expect(owner.getByText("No interviews yet. Create your first one.")).toBeVisible()
  await shot(owner, "interviews-empty")

  // Templates tab: the warning card and "Use template" on each row.
  const templates = await templatesBySize(owner)
  await openTab(owner, "Templates")
  await expect(owner.getByText("Templates are ready-made for common roles.")).toBeVisible()
  await shot(owner, "templates")
  // The smallest template that can be used: one with too few questions left can't.
  let used = ""

  for (const template of templates) {
    const row = owner.getByRole("listitem").filter({ hasText: template.title }).first()
    await row.getByRole("button", { name: "Use template" }).click()
    const failed = owner.getByText("Couldn't start an interview from this template.", {
      exact: false,
    })
    const outcome = await Promise.race([
      owner
        .waitForURL(/\/interviews\/[^/?]+$/)
        .then(() => "opened")
        .catch(() => ""),
      failed
        .waitFor()
        .then(() => "failed")
        .catch(() => ""),
    ])

    if (outcome === "opened") {
      used = template.title
      break
    }

    await shot(owner, "template-failed")
    await failed.waitFor({ state: "hidden" })
  }

  expect(used, "a template that can be used").not.toBe("")
  await expect(owner.getByRole("button", { name: "Manage questions" }).first()).toBeVisible()
  await shot(owner, "interview")

  // The questions of the first topic: the AI warning card and every answer option.
  await owner.getByRole("button", { name: "Manage questions" }).first().click()
  const dialog = owner.getByRole("dialog")
  await expect(dialog.getByText(/AI-written questions and answer keys can be wrong/)).toBeVisible()
  await expect(dialog.getByRole("img", { name: "Correct answer" }).first()).toBeVisible()
  await expect(dialog.getByRole("img", { name: "Wrong answer" }).first()).toBeVisible()
  await shot(owner, "manage-questions")
  await owner.keyboard.press("Escape")

  const interviewUrl = owner.url()
  await owner.getByRole("button", { name: "Interviews" }).click()
  await expect(owner).toHaveURL(/\/interviews$/)
  await expect(owner.getByText(used).first()).toBeVisible()
  await shot(owner, "interviews-list")

  // Inviting a candidate opens the candidate list with them on it.
  await visit(owner, `${interviewUrl}?tab=candidates`)
  await expect(owner.getByText("No candidates invited yet.")).toBeVisible()
  await shot(owner, "candidates-empty")
  const candidate = throwawayEmail("candidate")
  await owner.getByRole("button", { name: "New candidate(s)" }).click()
  await owner.getByRole("dialog").getByLabel("Candidate emails").fill(candidate)
  await shot(owner, "invite-dialog")
  await owner.getByRole("dialog").getByRole("button", { name: "Invite" }).click()
  await expect(owner.getByText(`Invite sent to ${candidate}`)).toBeVisible()
  await expect(owner.getByText(candidate, { exact: true }).first()).toBeVisible()
  await shot(owner, "candidates")
})
