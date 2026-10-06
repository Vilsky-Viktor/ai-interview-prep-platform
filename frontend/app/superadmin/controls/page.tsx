import { notFound } from "next/navigation"

import { MaintenanceSwitch } from "@/components/superadmin/maintenance-switch"
import { PauseSwitch } from "@/components/superadmin/pause-switch"
import { SuperadminHeader } from "@/components/superadmin/superadmin-header"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"

export const generateMetadata = () => translatedTitle("superadmin", "zone")

/** The admin zone's controls: the emergency pause and maintenance mode. The pause's state is
 * public (pages show a notice), so the page asks who's signed in; maintenance's is for
 * superadmins only. The API turns both for superadmins only. */
export default async function ControlsPage() {
  const [me, pause, maintenance] = await Promise.all([
    serverFetch<{ is_superadmin: boolean }>("/library/me"),
    serverFetch<{ paused: boolean }>("/companies/pause"),
    serverFetch<{ on: boolean }>("/companies/superadmin/maintenance"),
  ])

  if (!me?.is_superadmin || !pause || !maintenance) {
    notFound()
  }

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <SuperadminHeader current="controls" />
      <div className="space-y-4">
        <PauseSwitch paused={pause.paused} />
        <MaintenanceSwitch on={maintenance.on} />
      </div>
    </main>
  )
}
