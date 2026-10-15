import { expect, test } from "../fixtures";
import { addPracticeRounds, addTemplate, deleteTemplate } from "../helpers/db";
import { visit } from "../helpers/navigation";
import { uidOf } from "../helpers/sign-in";
import { throwawayEmail } from "../helpers/users";

/** The date `daysAgo` days ago, as the list shows it. */
function day(daysAgo: number) {
  const date = new Date(Date.now() - daysAgo * 24 * 60 * 60 * 1000);

  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

// A talent's practice history shows its rounds newest first, a page (20) at a time: scrolling
// past the first page loads the oldest.
test("the practice history loads its older rounds as it scrolls", async ({
  signInAs,
}) => {
  const talent = await signInAs(throwawayEmail("practice-history"));
  const templateId = await addTemplate("E2E practice history", 1);

  try {
    // One a day: the oldest, 21 days ago, is on the second page.
    await addPracticeRounds(await uidOf(talent), templateId, 22);
    await visit(talent, `/practice/history/${templateId}`);
    await expect(talent.getByText(day(0), { exact: true })).toBeVisible();

    const oldest = talent.getByText(day(21), { exact: true });
    await expect(async () => {
      await talent.mouse.wheel(0, 4000);
      await expect(oldest).toBeVisible({ timeout: 1000 });
    }).toPass({ timeout: 30_000 });
  } finally {
    await deleteTemplate(templateId);
  }
});
