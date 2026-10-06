import { type Browser, expect, type Page } from "@playwright/test"

import { TOKEN_COOKIE } from "../constants"
import { env } from "./env"
import { visit } from "./navigation"

/** A new browser signed in as `email`, through the site's own "Continue with Google" and the
 * Auth emulator's sign-in page (never real Google): an account the emulator already has is
 * picked from its list, any other is added. The emulator marks these emails verified. */
export async function signIn(browser: Browser, email: string): Promise<Page> {
  if (!env("NEXT_PUBLIC_FIREBASE_AUTH_EMULATOR_URL")) {
    throw new Error("Signed-in tests need the Firebase Auth emulator")
  }

  const context = await browser.newContext()
  const page = await context.newPage()
  // A page that only asks to sign in shows the options inline.
  await visit(page, "/company")
  const popup = await openGooglePopup(page)
  await popup.waitForLoadState()
  // Each listed account carries its claims, the email among them, URL-encoded.
  const claim = encodeURIComponent(`"email":"${email}"`)
  const existing = popup.locator(`li.js-reuse-account[data-id-token*="${claim}"]`)

  if ((await existing.count()) > 0) {
    await existing.first().click()
  } else {
    await popup.getByText(/add new account/i).click()
    await popup.locator("#email-input").fill(email)
    await popup.locator("#display-name-input").fill(email.split("@")[0])
    await popup.locator("#sign-in").click()
  }

  await popup.waitForEvent("close")
  // Signed in once the frontend writes the token cookie and re-renders the page with it.
  await expect
    .poll(async () => (await context.cookies()).some((c) => c.name === TOKEN_COOKIE))
    .toBe(true)
  await expect(page.getByRole("button", { name: /new company/i })).toBeVisible()

  return page
}

/** Clicks "Continue with Google" until the emulator's page opens: a click before the page is
 * ready opens nothing. */
async function openGooglePopup(page: Page): Promise<Page> {
  const popups: Page[] = []

  await expect(async () => {
    const opened = page.context().waitForEvent("page", { timeout: 5_000 })
    await page.getByRole("button", { name: /continue with google/i }).click()
    popups.push(await opened)
  }).toPass({ timeout: 120_000 })

  return popups[0]
}

/** The signed-in user's token, for setting things up through the API. */
export async function tokenOf(page: Page): Promise<string> {
  const cookie = (await page.context().cookies()).find((c) => c.name === TOKEN_COOKIE)

  if (!cookie?.value) {
    throw new Error("not signed in")
  }

  return cookie.value
}
