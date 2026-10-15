import { expect, test } from "../fixtures"
import { createCompany, createInterview } from "../helpers/api"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail } from "../helpers/users"

// Keyboard use: the first Tab offers to skip past the header to the page, and a dialog's tabs
// move with the arrow keys.
test("the keyboard skips the header and moves between tabs with the arrows", async ({
  signInAs,
}) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)
  await visit(owner, `/companies/${company.id}/interviews/${interviewId}?tab=candidates`)

  // The skip link is the first Tab, even on a page whose tab row scrolled to its current tab;
  // hidden until then, it takes the focus past the header.
  const skip = owner.getByRole("link", { name: "Skip to content" })
  await expect(owner.getByRole("button", { name: "New candidate(s)" })).toBeVisible()
  await owner.keyboard.press("Tab")
  await expect(skip).toBeFocused()
  await expect(skip).toBeVisible()
  await shot(owner, "skip-link")
  await owner.keyboard.press("Enter")
  await expect(owner.locator("#content")).toBeFocused()

  // The invite dialog's tabs: the arrows move between them, Home and End to the ends.
  await owner.getByRole("button", { name: "New candidate(s)" }).click()
  const dialog = owner.getByRole("dialog")
  const one = dialog.getByRole("tab", { name: "one", exact: true })
  await one.click()
  await owner.keyboard.press("ArrowRight")
  const many = dialog.getByRole("tab", { name: "many", exact: true })
  await expect(many).toBeFocused()
  await expect(many).toHaveAttribute("aria-selected", "true")
  await owner.keyboard.press("End")
  await expect(dialog.getByRole("tab", { name: "upload", exact: true })).toBeFocused()
  await owner.keyboard.press("Home")
  await expect(one).toHaveAttribute("aria-selected", "true")
  await shot(owner, "tabs-keyboard")
})
