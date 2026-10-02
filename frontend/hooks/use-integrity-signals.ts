import { useEffect } from "react"

import { apiFetch } from "@/lib/api"

/** Tells the server when the candidate leaves the page or copies, for the company's scorecard.

Reporting never gets in the candidate's way: a failed report is dropped. */
export function useIntegritySignals(sessionId: string, active: boolean) {
  useEffect(() => {
    if (!active) {
      return
    }

    function report(kind: "tab_leave" | "copy") {
      apiFetch(`/rounds/sessions/${sessionId}/signals`, {
        method: "POST",
        body: JSON.stringify({ kind }),
      }).catch(() => {})
    }

    // Blur covers both another tab and another app.
    const onBlur = () => report("tab_leave")
    const onCopy = () => report("copy")

    window.addEventListener("blur", onBlur)
    document.addEventListener("copy", onCopy)

    return () => {
      window.removeEventListener("blur", onBlur)
      document.removeEventListener("copy", onCopy)
    }
  }, [sessionId, active])
}
