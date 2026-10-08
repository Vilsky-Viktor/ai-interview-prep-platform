import { expect, test } from "../fixtures"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail } from "../helpers/users"

const KINDS = [
  "Candidates who finished",
  "Undelivered invites",
  "ATS candidates not invited",
  "Interviews ready",
]

// Settings > Emails: one block per kind of email, each saved as it changes. The digest's own
// box turns its four kinds on or off at once, and shows a dash when only some are on.
test("a user chooses their emails in settings", async ({ signInAs }) => {
  const user = await signInAs(ownerEmail())
  await visit(user, "/settings")
  const box = (name: string) => user.getByRole("checkbox", { name, exact: true })
  const digest = user.getByRole("checkbox", { name: /^Activity digest/ })

  // A new user: the digest and reminders on, offers off; product updates on, as the first
  // sign-in left the opt-out unticked.
  await expect(digest).toBeChecked()

  for (const kind of KINDS) {
    await expect(box(kind)).toBeChecked()
  }

  await expect(user.getByRole("checkbox", { name: /^Reminders/ })).toBeChecked()
  await expect(user.getByRole("checkbox", { name: /^Product updates and news/ })).toBeChecked()
  await expect(user.getByRole("checkbox", { name: /^Offers and promotions/ })).not.toBeChecked()
  await expect(user.getByText("Service emails, such as invites", { exact: false })).toBeVisible()
  await shot(user, "emails")

  // One kind off: kept after a reload, and the digest shows a dash.
  await box("Undelivered invites").click()
  await expect(box("Undelivered invites")).not.toBeChecked()
  await expect(digest).toHaveAttribute("data-indeterminate", "")
  await user.reload()
  await expect(box("Undelivered invites")).not.toBeChecked()
  await expect(digest).toHaveAttribute("data-indeterminate", "")
  await shot(user, "some-kinds")

  // The digest's box turns all four on, then all off.
  await digest.click()

  for (const kind of KINDS) {
    await expect(box(kind)).toBeChecked()
  }

  await digest.click()

  for (const kind of KINDS) {
    await expect(box(kind)).not.toBeChecked()
  }

  await expect(digest).not.toBeChecked()
  await user.reload()
  await expect(box("Interviews ready")).not.toBeChecked()
  await user.setViewportSize({ width: 390, height: 844 })
  await shot(user, "emails-phone")
})

// The sign-in's boxes: an unticked opt-out turns product updates on at a first sign-in only;
// offers go on only when ticked; a later sign-in never turns updates back on.
test("signing in sets product updates and offers", async ({ signInAs }) => {
  const product = /^Product updates and news/
  const offers = /^Offers and promotions/

  const ticked = await signInAs(ownerEmail(), { noUpdates: true, promotions: true })
  await visit(ticked, "/settings")
  await expect(ticked.getByRole("checkbox", { name: product })).not.toBeChecked()
  await expect(ticked.getByRole("checkbox", { name: offers })).toBeChecked()

  const email = ownerEmail()
  const first = await signInAs(email)
  await visit(first, "/settings")
  const updates = first.getByRole("checkbox", { name: product })
  await expect(updates).toBeChecked()
  await expect(first.getByRole("checkbox", { name: offers })).not.toBeChecked()
  await updates.click()
  await expect(updates).not.toBeChecked()
  // Saved before signing in again.
  await first.reload()
  await expect(first.getByRole("checkbox", { name: product })).not.toBeChecked()

  const again = await signInAs(email)
  await visit(again, "/settings")
  await expect(again.getByRole("checkbox", { name: product })).not.toBeChecked()
})
