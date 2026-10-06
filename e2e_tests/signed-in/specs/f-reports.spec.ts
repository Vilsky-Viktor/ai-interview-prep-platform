import { readFile } from "node:fs/promises"

import { expect, test } from "../fixtures"
import { createCompany, createInterview, inviteCandidate } from "../helpers/api"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail, throwawayEmail } from "../helpers/users"

// The candidates tab's report of all candidates: downloaded as a PDF, or shared.
test("owner downloads and shares the report of all candidates", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  await inviteCandidate(owner, interviewId, throwawayEmail("candidate"))
  await visit(owner, `/company/${company.id}/interviews/${interviewId}?tab=candidates`)
  // Labels are lowercase like the filters beside them, in every language (CSS, not the text).
  await expect(owner.getByText("Shareable link", { exact: true })).toHaveCSS(
    "text-transform",
    "lowercase"
  )
  await shot(owner, "candidates")

  const downloaded = owner.waitForEvent("download")
  await owner.getByRole("button", { name: "Download PDF" }).click()
  const file = await downloaded
  expect(file.suggestedFilename()).toMatch(/^Candidates .*\.pdf$/)
  const path = test.info().outputPath(file.suggestedFilename())
  await file.saveAs(path)
  expect((await readFile(path)).subarray(0, 5).toString()).toBe("%PDF-")

  await owner.getByRole("button", { name: "Share report" }).click()
  const dialog = owner.getByRole("dialog")
  await expect(dialog.getByLabel("Recipient's email")).toBeVisible()
  await expect(dialog.getByText("Or send via")).toHaveCSS("text-transform", "lowercase")
  await shot(owner, "share-dialog")
  await owner.keyboard.press("Escape")
})
