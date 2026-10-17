import { isValidElement, type ReactNode } from "react"

import { CodeEditor } from "@/components/code-editor"

/** A Markdown code block ("```python" … "```") in the code editor: react-markdown's `pre`, whose
 * child is the `code` with its language as a class. */
export function MarkdownCode({ children }: { children?: ReactNode }) {
  if (!isValidElement<{ className?: string; children?: ReactNode }>(children)) {
    return <pre>{children}</pre>
  }

  const { className = "", children: text } = children.props

  return (
    <CodeEditor
      code={String(text ?? "").replace(/\n$/, "")}
      language={/language-(\S+)/.exec(className)?.[1]}
      className="my-2"
    />
  )
}
