import { cn } from "cn"

import { CodeEditor } from "@/components/code-editor"
import { InlineText } from "@/components/questions/inline-text"
import { splitCodeBlocks } from "@/lib/question-text"

export function QuestionText({
  text,
  heading = false,
  className,
}: {
  text: string
  heading?: boolean
  className?: string
}) {
  return (
    <div
      role={heading ? "heading" : undefined}
      aria-level={heading ? 1 : undefined}
      // A heading takes focus when its question opens, for keyboard and screen reader users.
      tabIndex={heading ? -1 : undefined}
      className={cn("space-y-3", heading && "outline-none", className)}
    >
      {splitCodeBlocks(text).map((part, index) =>
        part.code ? (
          <CodeEditor
            key={index}
            code={part.text}
            language={part.language}
            header={false}
          />
        ) : (
          <p key={index} className="bidi-auto whitespace-pre-line">
            <InlineText text={part.text.trim()} />
          </p>
        )
      )}
    </div>
  )
}
