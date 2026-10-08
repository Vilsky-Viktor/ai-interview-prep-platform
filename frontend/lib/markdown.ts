import type { Options } from "react-markdown"

import { inAppHref } from "@/lib/assistant"

// The markdown an assistant's answer may use: text, emphasis, lists, code and links. Anything
// else (images, tables, headings, raw HTML) shows as its text, or not at all.
const ELEMENTS = ["p", "br", "strong", "em", "ul", "ol", "li", "code", "a"]

/** react-markdown's options for an answer: only ELEMENTS, no raw HTML, and links only to the
 * app's own pages (any other link keeps its text and loses its address). */
export const ANSWER_MARKDOWN: Options = {
  allowedElements: ELEMENTS,
  unwrapDisallowed: true,
  skipHtml: true,
  urlTransform: (url) => inAppHref(url),
}
