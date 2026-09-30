import type { Metadata } from "next"

import { SessionView } from "@/components/company/session-view"

export const metadata: Metadata = { title: "Interview" }

export default async function SessionPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  return (
    <main className="mx-auto max-w-5xl px-6 py-12">
      <SessionView id={id} />
    </main>
  )
}
