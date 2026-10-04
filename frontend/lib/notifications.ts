import { MAX_RECONNECT_MS, RECONNECT_MS } from "@/constants/notifications"
import { authHeaders } from "@/lib/api"

/** Keeps the bell's live stream open until `signal` aborts, calling onNew whenever a
 * notification comes, and onOpen each time it (re)connects so nothing missed meanwhile is lost.
 * A dropped stream (the server's hour is up, a deploy, the network) reconnects by itself. */
export async function watchNotifications(
  signal: AbortSignal,
  onOpen: () => void,
  onNew: () => void
) {
  let wait = RECONNECT_MS

  while (!signal.aborted) {
    try {
      const response = await fetch("/api/notifications/me/stream", {
        headers: await authHeaders(),
        signal,
      })

      if (response.ok && response.body) {
        wait = RECONNECT_MS
        onOpen()
        const reader = response.body
          .pipeThrough(new TextDecoderStream())
          .getReader()

        while (true) {
          const { value, done } = await reader.read()

          if (done) {
            break
          }

          // Heartbeats are comments (": heartbeat"); only data lines announce something new.
          if (value.includes("data:")) {
            onNew()
          }
        }
      }
    } catch {
      // Aborted, or the network dropped: the loop decides whether to try again.
    }

    if (signal.aborted) {
      return
    }

    await new Promise((resolve) => setTimeout(resolve, wait))
    wait = Math.min(wait * 2, MAX_RECONNECT_MS)
  }
}
