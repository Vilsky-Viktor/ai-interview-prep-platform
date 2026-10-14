"use client"

import { useCallback, useEffect, useRef, useState } from "react"

import { InviteView } from "@/components/company/invite-view"
import { SessionView } from "@/components/company/session-view"
import { EMBED_EVENTS, EMBED_SOURCE } from "@/constants/embed"

/** A candidate's interview inside a company's own site (public/embed/v1.js frames it): the
 * invitation, then the questions in place. The company's page hears when it's ready, started and
 * finished, and how tall it is; only `origin`, the page that framed it, hears it. */
export function EmbedView({
  token,
  origin,
}: {
  token: string
  origin: string | null
}) {
  const [sessionId, setSessionId] = useState<string | null>(null)
  const content = useRef<HTMLDivElement>(null)
  const post = useCallback(
    (type: string, data: Record<string, unknown> = {}) => {
      if (origin && window.parent !== window) {
        window.parent.postMessage(
          { source: EMBED_SOURCE, type, ...data },
          origin
        )
      }
    },
    [origin]
  )

  const told = useRef(false)

  useEffect(() => {
    // Once, also when React mounts it twice (development).
    if (!told.current) {
      told.current = true
      post(EMBED_EVENTS.ready)
    }

    if (!content.current) {
      return
    }

    const observer = new ResizeObserver(([entry]) =>
      post(EMBED_EVENTS.resize, {
        height: Math.ceil(entry.target.getBoundingClientRect().height),
      })
    )
    observer.observe(content.current)

    return () => observer.disconnect()
  }, [post])

  const started = useCallback(
    (id: string) => {
      setSessionId(id)
      post(EMBED_EVENTS.started)
    },
    [post]
  )
  const finished = useCallback(
    (candidateId: string) => post(EMBED_EVENTS.finished, { candidateId }),
    [post]
  )

  return (
    <div ref={content} className="flex flex-col items-center py-12">
      {sessionId ? (
        <SessionView id={sessionId} onFinished={finished} />
      ) : (
        <InviteView token={token} onStarted={started} />
      )}
    </div>
  )
}
