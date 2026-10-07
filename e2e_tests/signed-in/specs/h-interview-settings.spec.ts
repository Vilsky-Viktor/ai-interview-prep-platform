import { expect, test } from "../fixtures"
import { createCompany, createInterview } from "../helpers/api"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { throwawayEmail } from "../helpers/users"

// An interview's settings are its own tab: time per question, passing grade and hired, each
// saved as it changes and kept after a reload.
test("an owner changes an interview's settings on its settings tab", async ({ signInAs }) => {
  const owner = await signInAs(throwawayEmail("interview-settings"))
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const interviewUrl = `/companies/${company.id}/interviews/${interviewId}`

  await visit(owner, interviewUrl)
  await owner.locator("main nav").getByRole("link", { name: "Settings" }).click()
  await expect(owner).toHaveURL(new RegExp(`${interviewUrl}\\?tab=settings$`))
  await shot(owner, "settings-tab")

  const seconds = owner.getByLabel("Time per question in seconds")
  const mark = owner.getByLabel("Passing grade in percent")
  await seconds.fill("90")
  await seconds.press("Enter")
  await mark.fill("70")
  await mark.press("Enter")
  await owner.getByRole("checkbox").click()
  await expect(owner.getByRole("checkbox")).toBeChecked()

  await owner.reload()
  await expect(seconds).toHaveValue("90")
  await expect(mark).toHaveValue("70")
  await expect(owner.getByRole("checkbox")).toBeChecked()
})
