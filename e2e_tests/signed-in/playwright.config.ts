import { defineConfig, devices } from "@playwright/test"

// Runs in Playwright's Docker image (e2e_tests/signed-in.sh), like the signed-out page tests.
// HOST_RULES points the site and the Firebase Auth emulator at their containers, so the browser
// keeps the addresses the frontend uses. One worker: maintenance mode and the pause are global,
// so the specs run one after another, in file order.
export default defineConfig({
  testDir: "specs",
  globalSetup: "./warm-up.ts",
  // Deletes every throwaway account and its companies after each run (teardown.ts).
  globalTeardown: "./teardown.ts",
  reporter: "list",
  workers: 1,
  // Once more on failure: the local dev frontend can restart mid-test (see helpers/navigation.ts).
  retries: 1,
  fullyParallel: false,
  timeout: 180_000,
  expect: { timeout: 15_000 },
  use: {
    ...devices["Desktop Chrome"],
    viewport: { width: 1280, height: 800 },
    baseURL: process.env.SITE_URL ?? "http://localhost:8090",
    acceptDownloads: true,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    launchOptions: {
      args: process.env.HOST_RULES
        ? [`--host-resolver-rules=${process.env.HOST_RULES}`]
        : [],
    },
  },
})
