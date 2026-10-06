import { fileURLToPath } from "node:url"
import { defineConfig } from "vitest/config"

// Unit tests of the pure helpers, in tests/ (`pnpm test`); "@/" is the app's root, as in
// tsconfig.json.
export default defineConfig({
  resolve: { alias: { "@": fileURLToPath(new URL(".", import.meta.url)) } },
  test: { include: ["tests/**/*.test.ts"] },
})
