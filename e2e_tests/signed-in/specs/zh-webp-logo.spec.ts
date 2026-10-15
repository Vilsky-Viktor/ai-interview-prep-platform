import { expect, test } from "../fixtures";
import { API_URL } from "../constants";
import { api, createCompany } from "../helpers/api";
import { throwawayEmail } from "../helpers/users";

// A 4×4 WebP with transparency.
const WEBP = "UklGRh4AAABXRUJQVlA4TBEAAAAvA8AAEAdQjyLXo4CBiOh/AAA=";

// A WebP logo is kept as PNG, which every email client shows (classic Outlook shows no WebP).
test("a WebP logo is served as PNG", async ({ signInAs }) => {
  const owner = await signInAs(throwawayEmail("webp-logo"));
  const company = await createCompany(owner);

  const { logo_url } = await api<{ logo_url: string }>(
    owner,
    "PUT",
    `/companies/companies/${company.id}/logo`,
    { image: WEBP },
  );
  const served = await owner.request.get(
    `${API_URL}${logo_url.replace(/^\/api/, "")}`,
  );

  expect(served.status()).toBe(200);
  expect(served.headers()["content-type"]).toBe("image/png");
  expect((await served.body()).subarray(1, 4).toString()).toBe("PNG");
});
