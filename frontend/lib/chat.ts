import { ApiError, authHeaders, errorDetail } from "@/lib/api"
import type { HelpMessage } from "@/types/help"

/** Posts to a streaming chat route and calls onDelta with each piece of the reply. */
async function streamReply(
  path: string,
  body: unknown,
  onDelta: (delta: string) => void
) {
  const response = await fetch(`/api${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(await authHeaders()) },
    body: JSON.stringify(body),
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

    buffer += value
    const events = buffer.split("\n\n")
    buffer = events.pop() ?? ""

    for (const event of events) {
      const data = JSON.parse(event.replace(/^data: /, ""))

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
  onDelta: (delta: string) => void
) {
  return streamReply("/rounds/help/chat", { messages }, onDelta)
}
