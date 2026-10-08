import { expect, test } from "../fixtures";
import { api } from "../helpers/api";
import { visit } from "../helpers/navigation";
import { shot } from "../helpers/screenshots";
import { randomId } from "../helpers/users";

// The admin zone's tabs, in order.
const TABS = [
  "templates",
  "news",
  "flagged",
  "replaced",
  "pass rates",
  "verification",
  "stats",
  "emails",
  "controls",
];

type Post = { id: string; title: string };

// A superadmin writes a news post in the admin zone's news tab: the text's limit is counted down
// and enforced by the API, the post shows on the news page with its date, and it's edited and
// deleted from its row. Posts left by a failed run are deleted at the end.
test("superadmin writes, edits and deletes a news post", async ({
  signInSuperadmin,
}) => {
  const superadmin = await signInSuperadmin();
  const title = `E2E news ${randomId()}`;
  const edited = `${title} edited`;

  try {
    await visit(superadmin, "/superadmin/news");
    await expect(
      superadmin.locator("main nav a"),
    ).toHaveText(TABS, {
      ignoreCase: true,
    });

    await superadmin.getByRole("button", { name: "New post" }).click();
    const dialog = superadmin.getByRole("dialog");
    await expect(dialog.getByText("500 characters left")).toBeVisible();
    await dialog.getByRole("textbox", { name: "Title" }).fill(title);
    const text = dialog.getByRole("textbox", { name: "Text" });
    // The field stops at 500 characters; past it, the API refuses with its own message.
    await text.evaluate((field) => field.removeAttribute("maxlength"));
    await text.fill("x".repeat(501));
    await dialog.getByRole("button", { name: "Save" }).click();
    await expect(superadmin.getByText(/at most 500 characters/)).toBeVisible();
    await expect(dialog).toBeVisible();

    await text.fill("First line.\nSecond line.");
    await expect(dialog.getByText("476 characters left")).toBeVisible();
    await shot(superadmin, "news-dialog");
    await dialog.getByRole("button", { name: "Save" }).click();
    await expect(dialog).toBeHidden();
    const row = superadmin.locator("li", { hasText: title });
    await expect(row).toBeVisible();
    await shot(superadmin, "news-tab");

    const today = new Date().toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
    await visit(superadmin, "/news");
    const post = superadmin.locator("article", { hasText: title });
    await expect(post.getByRole("heading", { level: 2 })).toHaveText(
      `${title}.`,
    );
    await expect(
      post.getByRole("heading").locator("span.text-primary"),
    ).toHaveText(".");
    await expect(post.locator("time")).toHaveText(today);
    await expect(post.getByText("First line.")).toBeVisible();
    await shot(superadmin, "news-page");

    await visit(superadmin, "/superadmin/news");
    await superadmin
      .locator("li", { hasText: title })
      .getByRole("button", { name: "Edit post" })
      .click();
    await expect(dialog.getByRole("textbox", { name: "Title" })).toHaveValue(
      title,
    );
    await dialog.getByRole("textbox", { name: "Title" }).fill(edited);
    await dialog.getByRole("button", { name: "Save" }).click();
    await expect(dialog).toBeHidden();
    await expect(superadmin.locator("li", { hasText: edited })).toBeVisible();

    await superadmin
      .locator("li", { hasText: edited })
      .getByRole("button", { name: `Delete ${edited}` })
      .click();
    const confirm = superadmin.getByRole("dialog");
    await expect(confirm).toContainText("Delete this post?");
    await shot(superadmin, "news-delete");
    await confirm.getByRole("button", { name: "Delete" }).click();
    await expect(superadmin.locator("li", { hasText: edited })).toHaveCount(0);
    await visit(superadmin, "/news");
    await expect(superadmin.locator("article", { hasText: title })).toHaveCount(
      0,
    );
  } finally {
    const posts = await api<Post[]>(
      superadmin,
      "GET",
      "/library/superadmin/news?limit=100",
    );

    for (const left of posts.filter((item) => item.title.startsWith(title))) {
      await api(superadmin, "DELETE", `/library/superadmin/news/${left.id}`);
    }
  }
});
