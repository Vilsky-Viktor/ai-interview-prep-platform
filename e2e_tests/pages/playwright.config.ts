import { defineConfig, devices } from "@playwright/test"

// Runs in Playwright's Docker image (e2e_tests/pages.sh). The browser keeps the site's own
// address, so Next.js sees its usual origin; HOST_RULES points it at the gateway on the compose
// network.
export default defineConfig({
  testDir: ".",
  reporter: "list",
  use: {
    baseURL: process.env.SITE_URL ?? "http://localhost:8090",
    launchOptions: {
      args: process.env.HOST_RULES
        ? [`--host-resolver-rules=${process.env.HOST_RULES}`]
        : [],
    },
  },
  projects: [
    {
      name: "desktop",
      use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 800 } },
    },
    { name: "phone", use: { ...devices["Pixel 7"] } },
  ],
})
