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

// A list's problems are said in the dialog: a file that isn't a CSV or TXT file, one too large to
// send (not read at all), and a list's lines without an email or with a name that couldn't be read.
test("the invite dialog says what it couldn't read", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  await visit(owner, `/companies/${company.id}/interviews/${interviewId}?tab=candidates`)
  const dialog = owner.getByRole("dialog")
  const file = owner.locator("input[type=file]")

  await owner.getByRole("button", { name: "New candidate(s)" }).click()
  await dialog.getByRole("tab", { name: "upload from file" }).click()
  await file.setInputFiles({
    name: "candidates.xlsx",
    mimeType: "application/octet-stream",
    buffer: Buffer.from(`email\n${throwawayEmail("xlsx")}\n`),
  })
  await dialog.getByRole("button", { name: "Invite" }).click()
  await expect(dialog.getByText("Only CSV or TXT files.")).toBeVisible()
  await shot(owner, "wrong-file-type")

  await file.setInputFiles({
    name: "big.csv",
    mimeType: "text/csv",
    buffer: Buffer.alloc(60_000, "a"),
  })
  await expect(dialog.getByText("The file is too large (max 50 KB).")).toBeVisible()
  await expect(dialog.getByRole("button", { name: "Invite" })).toBeDisabled()
  await shot(owner, "file-too-large")

  await dialog.getByRole("tab", { name: "invite many" }).click()
  await dialog
    .getByLabel("Candidate emails")
    .fill(`${throwawayEmail("lines")}\nno email here\n\nBob <${throwawayEmail("bob")}\nnor here`)
  await dialog.getByRole("button", { name: "Invite" }).click()
  await expect(dialog.getByText("2 lines skipped: no email found (lines 2, 5)")).toBeVisible()
  await expect(dialog.getByText("1 name not read (line 4)")).toBeVisible()
  await shot(owner, "unusable-lines")
})
