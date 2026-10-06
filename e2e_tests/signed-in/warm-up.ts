import { FRONTEND_URL, WARM_UP_PATHS } from "./constants"

// The local frontend is a dev server: it compiles each page on its first visit, and compiling
// takes much memory. Asking for every page once before the browser starts keeps those spikes
// away from the tests (in a small Docker VM they can get the browser killed).
export default async function warmUp() {
  for (const path of WARM_UP_PATHS) {
    const deadline = Date.now() + 120_000

    while (Date.now() < deadline) {
      const status = await fetch(`${FRONTEND_URL}${path}`, { redirect: "manual" })
        .then((response) => response.status)
        .catch(() => 0)

      // A 502 or no answer: the dev server is restarting.
      if (status > 0 && status !== 502) {
        break
      }

      await new Promise((resolve) => setTimeout(resolve, 2_000))
    }
  }
}
