import { expect, test } from "../fixtures"
import { api, createCompany, createInterview, inviteCandidate } from "../helpers/api"
import { inviteToken } from "../helpers/db"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail, throwawayEmail } from "../helpers/users"

// The invite dialog's three tabs: one email with a name, a list with a name beside one email,
// and a file (its examples download; the welcome credits cover three candidates, so it isn't
// sent: the backend's tests read CSV name columns). The list shows each name under the
// email ("No name yet" without one), and search finds a candidate by name.
test("owner invites candidates with names three ways and finds one by name", async ({
  signInAs,
}) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const list = `/companies/${company.id}/interviews/${interviewId}?tab=candidates`
  const ann = throwawayEmail("ann")
  const bob = throwawayEmail("bob")
  const plain = throwawayEmail("plain")
  await visit(owner, list)
  const dialog = owner.getByRole("dialog")

  // Invite one: an email and its name.
  await owner.getByRole("button", { name: "New candidate(s)" }).click()
  await dialog.getByRole("tab", { name: "invite one" }).click()
  await dialog.getByLabel("Candidate email").fill(ann)
  await dialog.getByLabel("Name (optional)").fill("  Ann Lee ")
  await shot(owner, "invite-one")
  await dialog.getByRole("button", { name: "Invite" }).click()
  await expect(owner.getByText("Ann Lee", { exact: true })).toBeVisible()

  // Invite many: a name beside one email, none beside the other.
  await visit(owner, list)
  await owner.getByRole("button", { name: "New candidate(s)" }).click()
  await dialog.getByRole("tab", { name: "invite many" }).click()
  await expect(dialog.getByText("Ann Lee <ann.lee@example.com>")).toBeVisible()
  await dialog.getByLabel("Candidate emails").fill(`Bob Stone <${bob}>\n${plain}`)
  await shot(owner, "invite-many")
  await dialog.getByRole("button", { name: "Invite" }).click()
  await expect(owner.getByText("Bob Stone", { exact: true })).toBeVisible()
  const plainRow = owner.getByRole("link").filter({ hasText: plain })
  await expect(plainRow.getByText("No name yet")).toBeVisible()
  // Its tooltip says when it's filled in, and that an owner can enter it.
  await plainRow.getByText("No name yet").hover()
  await expect(
    owner.getByText(
      "Comes from the candidate's sign-in, or add it on their page."
    )
  ).toBeVisible()
  await shot(owner, "no-name-tooltip")

  // Upload from file: the example files download, and a CSV with a name column invites.
  await visit(owner, list)
  await owner.getByRole("button", { name: "New candidate(s)" }).click()
  await dialog.getByRole("tab", { name: "upload from file" }).click()

  for (const [label, file] of [
    ["example .csv", "prepza-candidates-example.csv"],
    ["example .txt", "prepza-candidates-example.txt"],
  ]) {
    const download = owner.waitForEvent("download")
    await dialog.getByRole("button", { name: label }).click()
    expect((await download).suggestedFilename()).toBe(file)
  }

  // A file is read on Invite, like a pasted list (the list tab invites the same way).
  await owner.locator("input[type=file]").setInputFiles({
    name: "candidates.csv",
    mimeType: "text/csv",
    buffer: Buffer.from(`email,name\n${throwawayEmail("cid")},Cid Moss\n`),
  })
  await expect(dialog.getByRole("button", { name: "candidates.csv" })).toBeVisible()
  await shot(owner, "invite-file")
  await owner.keyboard.press("Escape")
  await shot(owner, "candidates-with-names")

  // The dialog opens on the tab used last.
  await owner.getByRole("button", { name: "New candidate(s)" }).click()
  await expect(dialog.getByRole("tab", { name: "upload from file" })).toHaveAttribute(
    "aria-selected",
    "true"
  )
  await owner.keyboard.press("Escape")

  // Search matches part of a name, in any case.
  await owner.getByLabel("Search candidates by email or name").fill("stone")
  await owner.getByLabel("Search candidates by email or name").press("Enter")
  await expect(owner).toHaveURL(/q=stone/)
  await expect(owner.getByText(bob, { exact: true })).toBeVisible()
  await expect(owner.getByText(ann, { exact: true })).toHaveCount(0)
  await shot(owner, "search-by-name")
})

// A candidate without a name gets the one their sign-in has when they start; an owner corrects
// it on the candidate's page, and starting again doesn't change it back.
test("the sign-in fills a name once and an owner's correction stays", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  const email = throwawayEmail("named")
  await inviteCandidate(owner, interviewId, email)
  const list = `/companies/${company.id}/interviews/${interviewId}?tab=candidates`
  await visit(owner, list)
  await expect(owner.getByRole("link").filter({ hasText: email }).getByText("No name yet")).toBeVisible()

  const candidate = await signInAs(email, {}, "Maria Kowalska")
  const start = `/companies/invites/${await inviteToken(email)}/start`
  await api(candidate, "POST", start)

  await visit(owner, list)
  await owner.getByText("Maria Kowalska", { exact: true }).click()
  await expect(owner.getByRole("heading", { name: email })).toBeVisible()
  await expect(owner.getByRole("button", { name: "Edit name" })).toBeVisible()
  await shot(owner, "report-name")

  await owner.getByRole("button", { name: "Edit name" }).click()
  await owner.getByLabel("Name", { exact: true }).fill("Maria Nowak")
  await owner.getByLabel("Name", { exact: true }).press("Enter")
  const nameLine = owner.locator("p").filter({
    has: owner.getByRole("button", { name: "Edit name" }),
  })
  await expect(nameLine).toContainText("Maria Nowak")
  await shot(owner, "report-name-edited")

  // Starting again (reopening the invite) keeps the corrected name.
  await api(candidate, "POST", start)
  await owner.reload()
  await expect(nameLine).toContainText("Maria Nowak")
  await expect(owner.getByText("Maria Kowalska")).toHaveCount(0)
})
