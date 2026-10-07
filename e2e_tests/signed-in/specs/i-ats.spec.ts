import { expect, test } from "../fixtures"
import { createCompany, createInterview } from "../helpers/api"
import { addAtsConnection } from "../helpers/db"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { throwawayEmail } from "../helpers/users"

// The ATS tab: Workable with what connecting needs, how candidates flow, and once connected, the
// linked jobs. A real connection needs a Workable account, so one is saved straight into the
// database, and Workable's lists are answered in the browser.
test("an owner sees how to connect Workable and manages its linked jobs", async ({
  signInAs,
}) => {
  const owner = await signInAs(throwawayEmail("ats"))
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const tab = `/companies/${company.id}/integrations`

  await visit(owner, `/companies/${company.id}/interviews`)
  await owner.locator("main nav").getByRole("link", { name: "ATS" }).click()
  await expect(owner).toHaveURL(new RegExp(`${tab}$`))
  await expect(owner.getByText("Not connected")).toBeVisible()

  // The candidate flow, explained before connecting.
  await owner.getByRole("button", { name: "How candidates come from Workable" }).click()
  await expect(owner.getByRole("dialog").getByRole("listitem")).toHaveCount(6)
  await shot(owner, "candidate-flow")
  await owner.keyboard.press("Escape")

  // Where to make the token, and its scopes.
  await owner.getByRole("button", { name: "Connect" }).click()
  const connect = owner.getByRole("dialog")
  await expect(connect.getByText("API access tokens")).toBeVisible()
  await expect(connect.getByText("w_candidates")).toBeVisible()
  await expect(connect.getByRole("button", { name: "Connect" })).toBeDisabled()
  await shot(owner, "connect")
  await owner.keyboard.press("Escape")

  await addAtsConnection(company.id, interviewId)
  await visit(owner, tab)
  await expect(owner.getByText("Connected as e2e-acme")).toBeVisible()
  await expect(owner.getByText("E2E Backend developer")).toBeVisible()

  // A new interview from a Workable job starts from the job's own text, which can be edited.
  await owner.route("**/api/companies/ats/workable/jobs?*", (route) =>
    route.fulfill({ json: [{ id: "J1", name: "Senior Accountant" }] })
  )
  await owner.route("**/api/companies/ats/workable/jobs/J1/stages?*", (route) =>
    route.fulfill({ json: [{ id: "assessment", name: "Assessment" }] })
  )
  await owner.route("**/api/companies/ats/workable/jobs/J1/text?*", (route) =>
    route.fulfill({ json: { text: "Senior Accountant\n\nOwn our monthly close." } })
  )
  await owner.getByRole("button", { name: "Link a job" }).click()
  await owner.getByRole("button", { name: "Job", exact: true }).click()
  await owner.getByRole("menuitemradio", { name: "Senior Accountant" }).click()
  await owner.getByRole("button", { name: "Stage", exact: true }).click()
  await owner.getByRole("menuitemradio", { name: "Assessment" }).click()
  await owner.getByRole("button", { name: "Interview", exact: true }).click()
  await owner.getByRole("menuitemradio", { name: /new interview from this job/i }).click()
  await expect(owner.getByRole("textbox", { name: "The job from Workable" })).toHaveValue(
    "Senior Accountant\n\nOwn our monthly close."
  )
  await shot(owner, "new-interview-from-job")
  await owner.keyboard.press("Escape")

  // Unlinking asks first, then the job is gone.
  await owner.getByRole("button", { name: "Unlink" }).click()
  await owner.getByRole("dialog").getByRole("button", { name: "Unlink" }).click()
  await expect(owner.getByText("No linked jobs yet.")).toBeVisible()
})
