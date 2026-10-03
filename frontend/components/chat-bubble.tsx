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
