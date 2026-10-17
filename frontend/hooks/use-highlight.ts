"use client"

import { useEffect, useState } from "react"

import { CODE_THEMES } from "@/constants/code"

export type CodeToken = { content: string; style?: Record<string, string> }

/** The code's lines as colored tokens, once shiki has loaded the language; null until then, or
 * for a language it doesn't know, so the code shows plain meanwhile. */
export function useHighlight(code: string, language?: string) {
  // The lines with the code and language they were made for, so a change shows plain at once.
  const [result, setResult] = useState<{
    code: string
    language: string
    lines: CodeToken[][]
  } | null>(null)

  useEffect(() => {
    let current = true

    if (!language) {
      return
    }

    import("shiki").then(async ({ bundledLanguages, codeToTokens }) => {
      if (!(language in bundledLanguages)) {
        return
      }

      const { tokens } = await codeToTokens(code, {
        lang: language as keyof typeof bundledLanguages,
        themes: CODE_THEMES,
        defaultColor: false,
      })

      if (current) {
        setResult({
          code,
          language,
          lines: tokens.map((line) =>
            line.map((token) => ({
              content: token.content,
              style: token.htmlStyle as Record<string, string> | undefined,
            }))
          ),
        })
      }
    })

    return () => {
      current = false
    }
  }, [code, language])

  return result?.code === code && result.language === language
    ? result.lines
    : null
}
