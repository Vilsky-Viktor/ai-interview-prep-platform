import { describe, expect, it } from "vitest"

import {
  chooseCodeLanguage,
  chosenCodeLanguage,
  onCodeLanguage,
} from "@/lib/code-language"

describe("the chosen code language", () => {
  it("is shared, and every editor listening hears a new choice until it stops", () => {
    const heard: (string | null)[] = []
    const stop = onCodeLanguage(() => heard.push(chosenCodeLanguage()))

    chooseCodeLanguage("typescript")
    stop()
    chooseCodeLanguage("python")

    expect(heard).toEqual(["typescript"])
    expect(chosenCodeLanguage()).toBe("python")
  })
})
