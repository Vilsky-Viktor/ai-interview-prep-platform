import { cn } from "cn"

/** One message of a chat with the AI: the person's on the end side, the AI's on the start. */
export function ChatBubble({
  role,
  content,
  className,
}: {
  role: "user" | "assistant"
  // Plain text keeps its line breaks; the assistant's answers come as rendered markdown.
  content: React.ReactNode
  className?: string
}) {
  return (
    <li
      className={cn(
        "bidi-auto w-fit max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap",
        role === "user" ? "ms-auto bg-muted" : "bg-card",
        className
      )}
    >
      {content}
    </li>
  )
}

/** The AI's answer before its first words arrive: three dots rising in turn, named `label`
 * for screen readers. */
export function ThinkingDots({ label }: { label: string }) {
  return (
    <>
      <span className="sr-only">{label}</span>
      {[0, 150, 300].map((delay) => (
        <span
          key={delay}
          aria-hidden
          className="size-1.5 animate-[thinking_1.2s_ease-in-out_infinite] rounded-full bg-muted-foreground"
          style={{ animationDelay: `${delay}ms` }}
        />
      ))}
    </>
  )
}
