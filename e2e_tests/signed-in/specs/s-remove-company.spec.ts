import { expect, test } from "../fixtures";
import { createCompany } from "../helpers/api";
import { visit } from "../helpers/navigation";
import { shot } from "../helpers/screenshots";
import { ownerEmail } from "../helpers/users";

// Removing a company deletes its credits: the dialog says how many are lost (and the
// candidates they'd pay for) when there are any, and nothing about credits otherwise.
test("removing a company warns about the credits it loses", async ({ signInAs }) => {
  const owner = await signInAs(ownerEmail());
  // A first company gets the welcome credits (900, three candidates); a second one none.
  const funded = await createCompany(owner);
  const empty = await createCompany(owner);
  await visit(owner, "/companies");

  await owner.getByRole("button", { name: `Remove ${funded.name}` }).click();
  let dialog = owner.getByRole("dialog");
  await expect(dialog.getByText("Its 900 credits (about 3 candidates) will be lost and aren't refunded.")).toBeVisible();
  await shot(owner, "remove-with-credits");
  await dialog.getByRole("button", { name: "Cancel" }).click();
  await expect(dialog).toHaveCount(0);

  await owner.getByRole("button", { name: `Remove ${empty.name}` }).click();
  dialog = owner.getByRole("dialog");
  await expect(dialog.getByText("Its interviews and invites will be deleted.")).toBeVisible();
  await expect(dialog.getByText(/will be lost/)).toHaveCount(0);

  // Removed, it's gone from the list.
  await dialog.getByRole("button", { name: "Remove" }).click();
  await expect(owner.getByText(empty.name)).toHaveCount(0);
  await expect(owner.getByText(funded.name)).toBeVisible();
});
