import { expect, test } from "../fixtures"
import { createCompany, createInterview } from "../helpers/api"
import { failGeneration } from "../helpers/db"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { throwawayEmail } from "../helpers/users"

// An interview whose generation failed says so, in the list and on its page, instead of
// looking like it's still generating.
test("an interview whose generation failed says so", async ({ signInAs }) => {
  const owner = await signInAs(throwawayEmail("generation-failed"))
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  await failGeneration(interviewId, company.id)

  await visit(owner, `/companies/${company.id}/interviews`)
  const row = owner.getByRole("link", { name: /Generation failed/ })
  await expect(row).toHaveAttribute("href", `/companies/${company.id}/interviews/${interviewId}`)
  await expect(owner.getByText("Generating…")).toHaveCount(0)
  await shot(owner, "list")

  await visit(owner, `/companies/${company.id}/interviews/${interviewId}`)
  await expect(owner.getByRole("heading", { level: 1 })).toHaveText("Generation failed")
  await shot(owner, "page")
})

// Until its first top-up, a company has one generated interview waiting without candidates
// before it generates another: the attempt says how to go on, and nothing is generated.
test("an unpaid company with a generated interview waiting is asked to invite or delete it", async ({
  signInAs,
}) => {
  const owner = await signInAs(throwawayEmail("waiting-limit"))
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  await failGeneration(interviewId, company.id)

  await visit(owner, `/companies/${company.id}/interviews/new`)
  await owner
    .getByRole("textbox", { name: "Job description" })
    .fill("Senior accountant: month-end close, IFRS reporting and audits.")
  await owner.getByRole("button", { name: "Generate interview" }).click()
  await expect(
    owner.getByText(
      "Invite a candidate to your interview, or delete it, before generating another: until your first top-up, 1 generated interview can wait without candidates (5 after)."
    )
  ).toBeVisible()
  await shot(owner, "waiting-limit")
})
