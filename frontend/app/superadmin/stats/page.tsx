import { notFound } from "next/navigation"

import { StatsView } from "@/components/superadmin/stats-view"
import { SuperadminHeader } from "@/components/superadmin/superadmin-header"
import { serverFetch } from "@/lib/server-api"
import { translatedTitle } from "@/lib/site"

export const generateMetadata = () => translatedTitle("superadmin", "zone")

/** The admin zone's stats, all time or for a year or month the superadmin picks; the browser
 * keeps the choice (components/superadmin/stats-view.tsx). The API answers superadmins only. */
export default async function StatsPage() {
  const me = await serverFetch<{ is_superadmin: boolean }>("/library/me")

  if (!me?.is_superadmin) {
    notFound()
  }

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <SuperadminHeader current="stats" />
      <StatsView />
    </main>
  )
}
