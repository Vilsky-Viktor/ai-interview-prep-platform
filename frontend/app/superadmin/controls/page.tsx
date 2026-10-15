import { notFound } from "next/navigation"

import { LegalNotices } from "@/components/superadmin/legal-notices"
import { MaintenanceSwitch } from "@/components/superadmin/maintenance-switch"
import { PauseSwitch } from "@/components/superadmin/pause-switch"
import { SuperadminHeader } from "@/components/superadmin/superadmin-header"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"
import type { LegalNotice } from "@/types/superadmin"

export const generateMetadata = () => translatedTitle("superadmin", "zone")

/** The admin zone's controls: the emergency pause, maintenance mode and the legal notices. The pause's state is
 * public (pages show a notice), so the page asks who's signed in; maintenance's is for
 * superadmins only. The API turns both for superadmins only. */
export default async function ControlsPage() {
  const [pause, maintenance, notices] = await Promise.all([
    serverFetch<{ paused: boolean }>("/companies/pause"),
    serverFetch<{ on: boolean }>("/companies/superadmin/maintenance"),
    serverFetch<LegalNotice[]>("/notifications/superadmin/legal-notices"),
  ])

  if (!pause || !maintenance || !notices) {
    notFound()
  }

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <SuperadminHeader current="controls" />
      <div className="space-y-4">
        <PauseSwitch paused={pause.paused} />
        <MaintenanceSwitch on={maintenance.on} />
        <LegalNotices initial={notices} />
      </div>
    </main>
  )
}
