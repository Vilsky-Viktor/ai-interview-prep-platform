import { describe, expect, it } from "vitest"

import { postHeading } from "@/lib/news"

describe("postHeading", () => {
  it("ends a title with the dot, never two", () => {
    expect(postHeading("Greenhouse integration")).toEqual({
      text: "Greenhouse integration",
      dot: true,
    })
    expect(postHeading("We moved.")).toEqual({ text: "We moved", dot: true })
  })

  it("leaves a question or an exclamation without one", () => {
    expect(postHeading("What's new?")).toEqual({
      text: "What's new?",
      dot: false,
    })
    expect(postHeading("We're live!")).toEqual({
      text: "We're live!",
      dot: false,
    })
  })
})
