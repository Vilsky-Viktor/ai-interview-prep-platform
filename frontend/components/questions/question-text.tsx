import { cn } from "cn"

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
          <pre
            key={index}
            className="overflow-x-auto rounded-xl bg-muted px-4 py-3 font-mono text-sm leading-relaxed font-normal"
          >
            <code>{part.text}</code>
          </pre>
        ) : (
          <p key={index} className="bidi-auto whitespace-pre-line">
            <InlineText text={part.text.trim()} />
          </p>
        )
      )}
    </div>
  )
}
