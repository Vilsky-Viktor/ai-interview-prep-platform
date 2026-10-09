import { readdirSync, readFileSync } from "node:fs"
import { describe, expect, it } from "vitest"

import {
  COMPANY_TAB_HELP,
  INTERVIEW_TAB_HELP,
  PAGE_HELP_KEYS,
} from "@/constants/page-help"

type Help = { title: string; text: string; actions: string[]; tips: string[] }

const messagesDir = new URL("../../messages/", import.meta.url)
const helpOf = (code: string) =>
  JSON.parse(readFileSync(new URL(`${code}.json`, messagesDir), "utf8"))
    .pageHelp as Record<string, Help | string>
const locales = readdirSync(messagesDir).map((name) =>
  name.replace(".json", "")
)

describe("page help", () => {
  it("gives every company and interview tab its own page's text", () => {
    const tabs = [
      ...Object.values(COMPANY_TAB_HELP),
      ...Object.values(INTERVIEW_TAB_HELP),
    ]

    expect(new Set(tabs).size).toBe(tabs.length)

    for (const key of tabs) {
      expect(PAGE_HELP_KEYS).toContain(key)
    }

    expect(COMPANY_TAB_HELP.members).toBe("team")
  })

  it.each(locales)(
    "has a title, a text, actions and tips for every page in %s",
    (code) => {
      const help = helpOf(code)

      for (const key of PAGE_HELP_KEYS) {
        const page = help[key] as Help

        expect(page.title, `${code} ${key}`).toBeTruthy()
        expect(page.text, `${code} ${key}`).toBeTruthy()
        expect(page.actions.length, `${code} ${key}`).toBeGreaterThan(0)
        expect(page.tips.length, `${code} ${key}`).toBeGreaterThan(0)
      }

      expect(Object.keys(help).sort()).toEqual(
        [...PAGE_HELP_KEYS, "label", "actionsTitle", "tipsTitle"].sort()
      )
    }
  )
})
