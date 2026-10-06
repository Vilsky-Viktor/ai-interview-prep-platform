import { describe, expect, it } from "vitest"

import { splitCodeBlocks, splitInlineCode } from "@/lib/question-text"

describe("splitCodeBlocks", () => {
  it("keeps plain text as one text part", () => {
    expect(splitCodeBlocks("What does SELECT do?")).toEqual([
      { code: false, text: "What does SELECT do?" },
    ])
  })

  it("makes a fenced block a code part, without its language or last new line", () => {
    expect(
      splitCodeBlocks(
        "What does it print?\n```python\nprint(1)\n```\nPick one."
      )
    ).toEqual([
      { code: false, text: "What does it print?\n" },
      { code: true, text: "print(1)" },
      { code: false, text: "\nPick one." },
    ])
  })

  it("keeps the first word of a one-line fence", () => {
    expect(splitCodeBlocks("Run ```SELECT 1``` first")).toEqual([
      { code: false, text: "Run " },
      { code: true, text: "SELECT 1" },
      { code: false, text: " first" },
    ])
  })

  it("takes a fence without a language", () => {
    expect(splitCodeBlocks("```\nx\ny\n```")).toEqual([
      { code: true, text: "x\ny" },
    ])
  })

  it("drops text between blocks that is only whitespace", () => {
    expect(splitCodeBlocks("```c++\na\n```\n\n```objective-c\nb\n```")).toEqual(
      [
        { code: true, text: "a" },
        { code: true, text: "b" },
      ]
    )
  })

  it("leaves an unclosed fence as text", () => {
    expect(splitCodeBlocks("Look: ```sql\nSELECT 1")).toEqual([
      { code: false, text: "Look: ```sql\nSELECT 1" },
    ])
  })

  it("gives nothing for empty or blank text", () => {
    expect(splitCodeBlocks("")).toEqual([])
    expect(splitCodeBlocks("  \n ")).toEqual([])
  })
})

describe("splitInlineCode", () => {
  it("makes each backticked span a code part", () => {
    expect(splitInlineCode("Use `git add` then `git commit`.")).toEqual([
      { code: false, text: "Use " },
      { code: true, text: "git add" },
      { code: false, text: " then " },
      { code: true, text: "git commit" },
      { code: false, text: "." },
    ])
  })

  it("leaves a lone backtick, an empty pair and a span over a new line as text", () => {
    expect(splitInlineCode("a ` b")).toEqual([{ code: false, text: "a ` b" }])
    expect(splitInlineCode("a `` b")).toEqual([{ code: false, text: "a `` b" }])
    expect(splitInlineCode("`a\nb`")).toEqual([{ code: false, text: "`a\nb`" }])
  })
})
