import { expect, test } from "../fixtures";
import { api, createCompany, createInterview } from "../helpers/api";
import { visit } from "../helpers/navigation";
import { throwawayEmail } from "../helpers/users";

// An editable title needs at least 3 characters: a shorter one isn't saved, and says why.
test("a test's title under three characters isn't saved", async ({
  signInAs,
}) => {
  const owner = await signInAs(throwawayEmail("title-length"));
  const company = await createCompany(owner);
  const interviewId = await createInterview(owner, company.id);

  await visit(owner, `/companies/${company.id}/interviews/${interviewId}`);
  const heading = owner.getByRole("heading", { level: 1 });
  const before = await heading.innerText();
  // The pencil after the title.
  await heading.getByRole("button").click();
  const input = owner.getByRole("textbox");
  await input.fill("ab");
  await input.press("Enter");

  await expect(owner.getByText("Use at least 3 characters.")).toBeVisible();
  await expect(input).toHaveValue("ab");
  await input.press("Escape");
  await expect(heading).toHaveText(before);
  await owner.reload();
  await expect(heading).toHaveText(before);
});

// A company name needs at least 2 characters (EY and 3M are companies): one letter is refused
// under the field, and no company is made.
test("a one-letter company name isn't accepted", async ({ signInAs }) => {
  const owner = await signInAs(throwawayEmail("company-name-length"));

  await visit(owner, "/companies");
  await owner.getByTestId("new-company").click();
  const dialog = owner.getByRole("dialog");
  const name = dialog.getByRole("textbox");
  await name.fill("A");
  // Create, the dialog's last button.
  await dialog.getByRole("button").last().click();

  await expect(name).toHaveAttribute("aria-invalid", "true");
  await expect(dialog.locator("#company-name-error")).toHaveText(
    "Use at least 2 characters.",
  );
  await expect(owner).toHaveURL(/\/companies$/);
  expect(await api<unknown[]>(owner, "GET", "/companies/companies")).toEqual([]);
});
