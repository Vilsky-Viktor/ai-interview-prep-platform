import type { Metadata } from "next"

import { RoundView } from "@/components/rounds/round-view"

export const metadata: Metadata = { title: "Round" }

export default async function RoundPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  return (
    <main className="mx-auto max-w-5xl px-6 py-12">
      <RoundView id={id} />
    </main>
  )
}
