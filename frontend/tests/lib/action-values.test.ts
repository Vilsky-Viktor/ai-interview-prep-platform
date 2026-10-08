import { describe, expect, it } from "vitest"

import { previewValue } from "@/lib/action-values"

describe("previewValue", () => {
  it("shows each kind of value plainly", () => {
    expect(previewValue("hired", true, "yes", "no")).toBe("yes")
    expect(previewValue("generate_in", "de", "yes", "no")).toBe("Deutsch")
    expect(previewValue("kinds", ["a", "b"], "yes", "no")).toBe("a, b")
    expect(
      previewValue("changes", { updates: false, reminders: true }, "on", "off")
    ).toBe("updates: off\nreminders: on")
    expect(previewValue("pass_mark", 70, "yes", "no")).toBe("70")
  })
})
