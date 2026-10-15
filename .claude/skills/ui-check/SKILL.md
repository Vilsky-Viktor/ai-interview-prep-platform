---
name: ui-check
description: Look at a UI change in the browser on desktop and phone through the browser tests, compare before and after, and share the screenshots. Use for any change a user sees.
---

# Check a UI change

Never report a UI change without looking at it. Use the browser tests, never ad-hoc sign-in
scripts: they sign in through the Auth emulator with throwaway users and clean up after.

## Take screenshots

- **Signed in:** in a spec under `e2e_tests/signed-in/specs/`, call `shot(page, "name")`
  (`helpers/screenshots.ts`). Files land in
  `e2e_tests/signed-in/test-results/screenshots/<spec>/NN-name.png`.
- **Public pages:** in `e2e_tests/pages/`, `page.screenshot({ path: test.info().outputPath("name.png") })`.
- **Phone:** `await page.setViewportSize(PHONE)` (`helpers/layout.ts`, 390 × 844).
- Show exactly the state asked for: closed or open, empty or filled, focused or not.

Keep a screenshot step in the spec when the screen is new: it's how the next change gets its
"before".

## Compare before and after (refactors)

For a change that should look the same, take the screenshots before and after and diff them:

```bash
uv run -q --with pillow python - <<'EOF'
from PIL import Image, ImageChops
a = Image.open("before.png").convert("RGB"); b = Image.open("after.png").convert("RGB")
print(a.size, b.size, ImageChops.difference(a, b).getbbox() if a.size == b.size else "size differs")
EOF
```

Random test data (company names) and the Next.js dev-tools badge also differ: find where the
difference is before calling it a regression.

## Share

Copy each screenshot the user should see to `~/Desktop/prepza-screenshots/` with a descriptive
name (`k11-expired-invite.png`) and send it with SendUserFile, saying where it is.
