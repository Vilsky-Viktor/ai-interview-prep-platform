import type { Page } from "@playwright/test";

import { expect, test } from "../fixtures";
import { createCompany } from "../helpers/api";
import { visit } from "../helpers/navigation";
import { shot } from "../helpers/screenshots";
import { ownerEmail } from "../helpers/users";

/** The Remove button on a company's row in the companies list, beside its link. */
function removeButton(page: Page, companyId: string) {
  return page.locator(`a[href="/companies/${companyId}/interviews"] ~ div button`);
}

// Removing a company deletes its credits: the dialog says how many are lost (and the
// candidates they'd pay for) when there are any, and nothing about credits otherwise.
test("removing a company warns about the credits it loses", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail());
  // A first company gets the welcome credits (900, three candidates); a second one none.
  const funded = await createCompany(owner);
  const empty = await createCompany(owner);
  await visit(owner, "/companies");

  await removeButton(owner, funded.id).click();
  let dialog = owner.getByRole("dialog");
  const credits = dialog.getByTestId("remove-credits");
  await expect(credits).toContainText("900");
  await expect(credits).toContainText("3");
  await shot(owner, "remove-with-credits");
  // Cancel, then Remove.
  await dialog.getByRole("button").first().click();
  await expect(dialog).toHaveCount(0);

  await removeButton(owner, empty.id).click();
  dialog = owner.getByRole("dialog");
  await expect(dialog).toBeVisible();
  await expect(dialog.getByTestId("remove-credits")).toHaveCount(0);

  // Removed, it's gone from the list.
  await dialog.getByRole("button").last().click();
  await expect(owner.getByText(empty.name)).toHaveCount(0);
  await expect(owner.getByText(funded.name)).toBeVisible();
});
