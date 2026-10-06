import { ApiError, authHeaders, errorDetail } from "@/lib/api"
import type { HelpMessage } from "@/types/help"

/** Posts to a streaming chat route and calls onDelta with each piece of the reply, until
the reply ends or `signal` aborts. */
async function streamReply(
  path: string,
  body: unknown,
  onDelta: (delta: string) => void,
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
        throw new Error(data.error)
      }

      if (data.delta) {
        onDelta(data.delta)
      }
    }
  }
}

/** Asks the FAQ page's help chat; the page keeps the conversation and sends it whole. */
export function streamHelp(
  messages: HelpMessage[],
  onDelta: (delta: string) => void,
  signal: AbortSignal
) {
  return streamReply("/rounds/help/chat", { messages }, onDelta, signal)
}
