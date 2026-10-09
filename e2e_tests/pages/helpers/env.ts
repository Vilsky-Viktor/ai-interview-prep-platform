import { readFileSync } from "node:fs"

// The repo's .env, mounted read-only by pages.sh. Values are read here and never printed.
const ENV_FILE = process.env.ENV_FILE ?? "/env/.env"

/** A setting from the environment, or else from the repo's .env. */
export function env(name: string): string {
  if (process.env[name]) {
    return process.env[name]!
  }

  for (const line of readFileSync(ENV_FILE, "utf8").split("\n")) {
    if (line.startsWith(`${name}=`)) {
      return line.slice(name.length + 1).trim()
    }
  }

  throw new Error(`${name} isn't set`)
}
