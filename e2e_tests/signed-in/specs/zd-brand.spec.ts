import { expect, test } from "../fixtures"
import { api, createCompany, createInterview, inviteCandidate } from "../helpers/api"
import { inviteToken } from "../helpers/db"
import { visit } from "../helpers/navigation"
import { shot } from "../helpers/screenshots"
import { ownerEmail, throwawayEmail } from "../helpers/users"

// An owner picks the company's colors on its brand tab, sees them in the preview, can't save
// unreadable ones, and its candidate's invitation shows them.
test("an owner sets the company's colors and its candidates see them", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail())
  const company = await createCompany(owner)
  const interviewId = await createInterview(owner, company.id)

  await owner.setViewportSize({ width: 1280, height: 1300 })
  await visit(owner, `/companies/${company.id}/brand`)
  await expect(owner.getByRole("heading", { name: "Colors" })).toBeVisible()
  await shot(owner, "prepza-colors")

  // A dark page with an orange primary: the preview follows as they're typed.
  const field = (group: string, label: string) =>
    owner
      .getByRole("listitem")
      .filter({ has: owner.getByText(group, { exact: true }) })
      .locator(`input:not([type=color])[aria-label="${label}"]`)
  await field("Page", "Background").fill("#101418")
  await field("Page", "Text").fill("#f4f1ea")
  await field("Primary", "Color").fill("#ff7a1a")
  await field("Primary", "Text").fill("#1a1007")
  await field("Secondary", "Fill").fill("#1d242c")
  await field("Secondary", "Text").fill("#a9b4bf")
  await field("Dialogs", "Background").fill("#1d242c")
  await field("Dialogs", "Text").fill("#f4f1ea")
  await field("Borders", "Lines").fill("#2c3640")
  // The font and the cards' and buttons' rounding, the same in both themes, saved with the colors.
  await owner.getByRole("button", { name: "Font" }).click()
  await expect(owner.getByRole("menuitemradio", { name: "Inter" })).toBeVisible()
  await shot(owner, "fonts")
  await owner.getByRole("menuitemradio", { name: "Inter" }).click()
  await owner.getByRole("spinbutton", { name: "Card rounding" }).fill("4")
  await owner.getByRole("spinbutton", { name: "Button rounding" }).fill("8")
  await shot(owner, "picked")
  await owner.setViewportSize({ width: 390, height: 900 })
  await shot(owner, "picked-phone")
  await owner.setViewportSize({ width: 1280, height: 1300 })

  // Text too close to its background is refused, saying which.
  await field("Page", "Text").fill("#202428")
  await owner.getByRole("button", { name: "Save", exact: true }).first().click()
  await expect(owner.getByText("The page's text is too hard to read on its background.")).toBeVisible()
  await shot(owner, "unreadable")
  await field("Page", "Text").fill("#f4f1ea")
  await owner.getByRole("button", { name: "Save", exact: true }).first().click()
  await expect(owner.getByText("Saved", { exact: true })).toBeVisible()
  await expect
    .poll(
      async () =>
        (
          await api<{ brand_style: { font: string; radius: number; button_radius: number } }>(
            owner,
            "GET",
            `/companies/companies/${company.id}`
          )
        ).brand_style
    )
    .toEqual({ font: "inter", radius: 4, button_radius: 8 })
  // Saved colors of its own: the way back to prepza's shows, reset waits for a change.
  await expect(owner.getByRole("button", { name: "Reset to prepza defaults" }).first()).toBeVisible()
  await expect(owner.getByRole("button", { name: "Reset", exact: true }).first()).toBeDisabled()
  await owner.setViewportSize({ width: 390, height: 900 })
  await shot(owner, "saved-phone")
  await owner.setViewportSize({ width: 1280, height: 1300 })

  // Back to prepza's defaults and saved again: colors, font and rounding.
  await owner.getByRole("button", { name: "Reset to prepza defaults" }).first().click()
  await expect(owner.getByText("Back to prepza's defaults")).toBeVisible()
  await expect
    .poll(async () => (await api<{ brand_colors: unknown }>(owner, "GET", `/companies/companies/${company.id}`)).brand_colors)
    .toEqual({ light: null, dark: null })
  await field("Page", "Background").fill("#101418")
  await field("Page", "Text").fill("#f4f1ea")
  await field("Primary", "Color").fill("#ff7a1a")
  await field("Primary", "Text").fill("#1a1007")
  await field("Secondary", "Fill").fill("#1d242c")
  await field("Secondary", "Text").fill("#a9b4bf")
  await field("Dialogs", "Background").fill("#1d242c")
  await field("Dialogs", "Text").fill("#f4f1ea")
  await field("Borders", "Lines").fill("#2c3640")
  await owner.getByRole("button", { name: "Save", exact: true }).first().click()
  await expect(owner.getByRole("button", { name: "Reset to prepza defaults" }).first()).toBeVisible()

  // The dark set is its own, prepza's until changed.
  await owner.getByRole("tab", { name: "Dark theme" }).click()
  await expect(field("Page", "Background")).toHaveValue("#0a0a0a")
  await shot(owner, "dark")

  // The candidate's invitation, in the company's colors.
  const email = throwawayEmail("branded")
  await inviteCandidate(owner, interviewId, email)
  const candidate = await signInAs(email)
  await visit(candidate, `/invite/${await inviteToken(email)}`)
  await expect(candidate.getByRole("button", { name: "Accept & Start" })).toBeVisible()
  await expect(candidate.locator("html")).toHaveCSS("--background", "#101418")
  await shot(candidate, "invitation")

  // Asked for the dark theme in the address: prepza's dark set, as the company has none.
  await visit(candidate, `/invite/${await inviteToken(email)}?theme=dark`)
  await expect(candidate.locator("html")).toHaveCSS("--background", "#0a0a0a")
})
