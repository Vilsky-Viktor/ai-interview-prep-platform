import { createElement } from "react"
import { renderToStaticMarkup } from "react-dom/server"
import Markdown from "react-markdown"
import { describe, expect, it } from "vitest"

import { ANSWER_MARKDOWN, FAQ_MARKDOWN, plainAnswer } from "@/lib/markdown"

/** An answer as the panel renders it, before its links become the app's own. */
function render(text: string) {
  return renderToStaticMarkup(createElement(Markdown, ANSWER_MARKDOWN, text))
}

describe("ANSWER_MARKDOWN", () => {
  it("keeps emphasis, lists, code and links to the app's own pages", () => {
    expect(render("**Ann** passed:\n\n- one\n- `two`\n\n[open](/faq)")).toBe(
      '<p><strong>Ann</strong> passed:</p>\n<ul>\n<li>one</li>\n<li><code>two</code></li>\n</ul>\n<p><a href="/faq">open</a></p>'
    )
  })

  it("drops other links' addresses and keeps their text", () => {
    const html = render(
      "[a](https://evil.example) [b](//evil.example) [c](javascript:alert(1))"
    )

    expect(html).not.toContain("evil")
    expect(html).not.toContain("javascript")
    expect(html).toContain("a")
  })

  it("shows no images, raw HTML, headings or tables", () => {
    const html = render(
      '# Title\n\n![x](https://evil.example/a.png)\n\n<img src="x" onerror="y"><b>bold</b>'
    )

    expect(html).not.toMatch(/<img|<h1|<b>|onerror/)
    expect(html).toContain("Title")
  })
})

/** A FAQ answer as the FAQ list renders it, before its links become the site's own. */
function renderFaq(text: string) {
  return renderToStaticMarkup(createElement(Markdown, FAQ_MARKDOWN, text))
}

describe("FAQ_MARKDOWN", () => {
  it("makes links to the site's own pages links", () => {
    expect(
      renderFaq(
        "See the [pricing page](/pricing) and the [MCP tab](/api-docs?tab=mcp)."
      )
    ).toBe(
      '<p>See the <a href="/pricing">pricing page</a> and the <a href="/api-docs?tab=mcp">MCP tab</a>.</p>'
    )
  })

  it("keeps other links as their text", () => {
    const html = renderFaq(
      "[a](https://evil.example) [b](//evil.example) [c](javascript:alert(1)) [d](mailto:x@y.z)"
    )

    expect(html).toBe("<p>a b c d</p>")
  })

  it("shows everything else as escaped text", () => {
    const html = renderFaq('<img src="x" onerror="y"> <b>bold</b>')

    expect(html).not.toMatch(/<img|<b>/)
    expect(html).toContain("&lt;b&gt;bold&lt;/b&gt;")
  })
})

describe("plainAnswer", () => {
  it("keeps each link's text without its address", () => {
    expect(
      plainAnswer("The [pricing page](/pricing) lists [every](/a) price.")
    ).toBe("The pricing page lists every price.")
  })
})
