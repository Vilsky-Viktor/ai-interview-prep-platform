import { expect, test } from "@playwright/test";

// The home page's advantages: each card's one-line title ends before the icon on its corner,
// in every language, on a desktop and a phone.
const LOCALES = [
  "en", "ru", "uk", "es", "pt", "de", "fr", "it", "pl", "nl", "tr", "ar", "he", "fa", "ja",
  "zh", "ko", "hi", "id", "th", "vi", "fil", "et",
];

for (const locale of LOCALES) {
  test(`advantages titles fit beside their icons: ${locale}`, async ({ page }) => {
    await page.goto(locale === "en" ? "/" : `/${locale}`);
    const cards = page.locator("#advantages li");
    await expect(cards).toHaveCount(6);

    const overlaps = await cards.evaluateAll((items) =>
      items.flatMap((item) => {
        const icon = item.querySelector("span.absolute")!.getBoundingClientRect();
        const title = item.querySelector("span.whitespace-nowrap")!;
        const range = document.createRange();
        range.selectNodeContents(title);
        const text = range.getBoundingClientRect();
        const rtl = getComputedStyle(item).direction === "rtl";
        const fits = rtl ? text.left >= icon.right : text.right <= icon.left;

        return fits ? [] : [title.textContent];
      }),
    );

    expect(overlaps).toEqual([]);
  });
}
