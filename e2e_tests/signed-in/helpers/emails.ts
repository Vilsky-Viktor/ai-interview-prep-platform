import type { Page } from "@playwright/test"

// The email settings' boxes, in their order (Settings > Emails, and an account found on the
// admin zone's emails tab): the digest, its four kinds (candidates who finished, undelivered
// invites, ATS candidates not invited, interviews ready), then reminders, product updates and
// offers.
export const EMAIL_BOXES = {
  digest: 0,
  kinds: [1, 2, 3, 4],
  undelivered: 2,
  ready: 4,
  reminders: 5,
  updates: 6,
  offers: 7,
  count: 8,
}

/** The email settings' boxes on the page. */
export function emailBoxes(page: Page) {
  return page.getByTestId("email-preferences").getByRole("checkbox")
}
