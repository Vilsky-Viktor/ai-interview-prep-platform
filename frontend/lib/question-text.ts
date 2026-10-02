export type TextPart = { code: boolean; text: string }

const CODE_BLOCK = /```[\w+-]*\n?([\s\S]*?)```/g
const INLINE_CODE = /`([^`\n]+)`/g

function split(text: string, pattern: RegExp): TextPart[] {
  const parts: TextPart[] = []
  let last = 0

  for (const match of text.matchAll(pattern)) {
    const before = text.slice(last, match.index)

    if (before) {
      parts.push({ code: false, text: before })
    }

    parts.push({ code: true, text: match[1].replace(/\n$/, "") })
    last = match.index + match[0].length
  }

  const rest = text.slice(last)

  if (rest) {
    parts.push({ code: false, text: rest })
  }

  return parts
}

/** Fenced ``` blocks become code parts; everything else stays text. */
export function splitCodeBlocks(text: string): TextPart[] {
  return split(text, CODE_BLOCK).filter((part) => part.code || part.text.trim())
}

/** `inline code` within a line of text. */
export function splitInlineCode(text: string): TextPart[] {
  return split(text, INLINE_CODE)
}
