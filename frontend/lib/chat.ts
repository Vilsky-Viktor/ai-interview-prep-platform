import { ApiError, authHeaders, errorDetail } from "@/lib/api"

/** Sends a follow-up message and calls onDelta with each streamed piece of the reply. */
export async function streamChat(
  answerId: string,
  message: string,
  onDelta: (delta: string) => void
) {
  const response = await fetch(`/api/rounds/answers/${answerId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(await authHeaders()) },
    body: JSON.stringify({ message }),
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
