// Deletes every load run's throwaway accounts, as their users would in settings, which also
// deletes the companies they alone own; fails when any is left. e2e_tests/load.sh runs it after
// each scenario, so a failed or stopped run leaves nothing behind either.
import { deleteAccounts } from "./lib/accounts.js"

export const options = { vus: 1, iterations: 1 }

export default function () {
  const left = deleteAccounts()

  if (left > 0) {
    throw new Error(`${left} throwaway accounts left`)
  }

  console.log("no throwaway accounts left")
}
