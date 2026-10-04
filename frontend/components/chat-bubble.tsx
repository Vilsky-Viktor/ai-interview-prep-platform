import { cn } from "cn"

/** One message of a chat with the AI: the person's on the end side, the AI's on the start. */
export function ChatBubble({
  role,
  content,
}: {
  role: "user" | "assistant"
  content: string
}) {
  return (
    <li
      className={cn(
        "bidi-auto w-fit max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap",
        role === "user" ? "ms-auto bg-muted" : "bg-card"
      )}
    >
      {content}
    </li>
  )
}

/** The AI's bubble before its first words arrive: three dots rising in turn. */
export function ThinkingBubble({ label }: { label: string }) {
  return (
    <li className="flex w-fit items-center gap-1 rounded-2xl bg-card px-4 py-4">
      <span className="sr-only">{label}</span>
      {[0, 150, 300].map((delay) => (
        <span
          key={delay}
          aria-hidden
          className="size-1.5 animate-[thinking_1.2s_ease-in-out_infinite] rounded-full bg-muted-foreground"
          style={{ animationDelay: `${delay}ms` }}
        />
      ))}
    </li>
  )
}
