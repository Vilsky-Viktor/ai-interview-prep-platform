import { ApiError, authHeaders, errorDetail } from "@/lib/api"
import type { AssistantBlock } from "@/types/assistant"
import type { HelpMessage } from "@/types/help"

/** An error event in a stream: its message, already in the user's language, and its code when
the service gave one (the assistant's "session_expired"). */
export class StreamError extends Error {
  constructor(
    message: string,
    public code?: string
  ) {
    super(message)
  }
}

/** Posts to a streaming route (server-sent events) and calls onEvent with each event's data,
until the stream ends or `signal` aborts. An error event throws a StreamError; a refused request
throws an ApiError. */
export async function streamEvents<T>(
  path: string,
  body: unknown,
  onEvent: (event: T) => void,
  signal: AbortSignal
) {
  const response = await fetch(`/api${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(await authHeaders()) },
    body: JSON.stringify(body),
    signal,
  })

  if (!response.ok || !response.body) {
    const detail = errorDetail(await response.json().catch(() => null))

    throw new ApiError(
      response.status,
      detail ?? `Chat failed with status ${response.status}`
    )
  }

  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader()
  let buffer = ""

  while (true) {
    const { value, done } = await reader.read()

    if (done) {
      return
    }

    // Events end with a blank line; proxies may send CRLF line ends.
    buffer += value.replace(/\r\n?/g, "\n")
    const events = buffer.split("\n\n")
    buffer = events.pop() ?? ""

    for (const event of events) {
      // Only data lines carry the reply; comments (": keep-alive") and other fields don't.
      const lines = event
        .split("\n")
        .filter((line) => line.startsWith("data:"))
        .map((line) => line.slice(5).trimStart())

      if (lines.length === 0) {
        continue
      }

      const data = JSON.parse(lines.join("\n"))

      if (data.error) {
        throw new StreamError(data.error, data.code)
      }

      onEvent(data)
    }
  }
}

/** Asks prepza's help chat (signed-out visitors' assistant); the panel keeps the conversation
and sends it whole. Its events: {"delta"}, and a {"block"} sign-in card when the visitor asks to
sign in. */
export function streamHelp(
  messages: HelpMessage[],
  onEvent: (event: {
    delta?: string
    block?: AssistantBlock
    removed?: boolean
  }) => void,
  signal: AbortSignal
) {
  return streamEvents("/rounds/help/chat", { messages }, onEvent, signal)
}
