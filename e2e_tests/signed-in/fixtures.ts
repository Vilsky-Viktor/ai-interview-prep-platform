import { test as base, type Page } from "@playwright/test"

import { deleteOwnCompanies } from "./helpers/api"
import { env } from "./helpers/env"
import { signIn, type SignInEmails } from "./helpers/sign-in"

type Fixtures = {
  // Signs in through a new browser; a throwaway user's companies are deleted when the test ends,
  // and every browser is closed.
  signInWith: (email: string, throwaway: boolean, emails?: SignInEmails) => Promise<Page>
  // A new browser signed in as `email`, a throwaway user the test made up; `emails` ticks the
  // sign-in's email boxes first.
  signInAs: (email: string, emails?: SignInEmails) => Promise<Page>
  // A new browser signed in as the first superadmin in SUPERADMIN_EMAILS (emulator only). Nothing
  // of theirs is deleted.
  signInSuperadmin: () => Promise<Page>
}

export const test = base.extend<Fixtures>({
  signInWith: async ({ browser }, use) => {
    const opened: { page: Page; throwaway: boolean }[] = []

    await use(async (email, throwaway, emails) => {
      const page = await signIn(browser, email, emails)
      opened.push({ page, throwaway })

      return page
    })

    for (const { page, throwaway } of opened) {
      if (throwaway) {
        await deleteOwnCompanies(page).catch(() => {})
      }

      await page.context().close()
    }
  },
  signInAs: async ({ signInWith }, use) => {
    await use((email, emails) => signInWith(email, true, emails))
  },
  signInSuperadmin: async ({ signInWith }, use) => {
    const email = env("SUPERADMIN_EMAILS").split(",")[0].trim().toLowerCase()
    await use(() => signInWith(email, false))
  },
})

export { expect } from "@playwright/test"
