import type { Page } from "@playwright/test"

import { expect, test } from "../fixtures"
import { api, createCompany, createInterview, inviteCandidate } from "../helpers/api"
import { openDialog, visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail, throwawayEmail } from "../helpers/users"

/** Opens the page's info button, checks its dialog's title and a line of its text, and closes it. */
async function checkHelp(page: Page, title: string, line: RegExp) {
  const button = page.getByRole("main").getByRole("button", { name: "About this page" })
  await openDialog(page, button)
  const dialog = page.getByRole("dialog", { name: title })
  await expect(dialog.getByText(line)).toBeVisible()
  await shot(page, title.toLowerCase().replaceAll(" ", "-"))
  await dialog.getByRole("button", { name: "Close" }).click()
  await expect(dialog).toBeHidden()
}

// Every page from the companies list inward has an info button under its back arrow, opening a
// short guide to that page; the companies list's arrow goes home.
test("the info buttons explain the companies list, an interview and a candidate", async ({
  signInAs,
}) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  await inviteCandidate(owner, interviewId, throwawayEmail("candidate"))
  const [candidate] = await api<{ id: string }[]>(
    owner,
    "GET",
    `/companies/interviews/${interviewId}/candidates?sort=date&limit=5`
  )

  await visit(owner, "/companies")
  await checkHelp(owner, "Companies", /Create a company/)

  const interviewHref = `/companies/${company.id}/interviews/${interviewId}`
  await visit(owner, interviewHref)
  await checkHelp(owner, "Topics", /manage questions/)
  // Each tab explains itself.
  await visit(owner, `${interviewHref}?tab=candidates`)
  await checkHelp(owner, "Candidates", /Invite candidates/)

  await visit(owner, `${interviewHref}/candidates/${candidate.id}`)
  await checkHelp(owner, "Candidate report", /Download the report/)

  // The companies list's back arrow goes to the home page.
  await visit(owner, "/companies")
  const home = owner.getByRole("main").getByRole("button", { name: "Home" })
  await expect(home).toHaveAttribute("href", "/")
  await home.click()
  await expect(owner).toHaveURL(/\/$/)
})
