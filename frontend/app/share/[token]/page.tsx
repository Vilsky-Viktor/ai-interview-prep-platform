import type { Metadata } from "next"

import { ShareInvite } from "@/components/preparations/share-invite"

export const metadata: Metadata = { title: "Share invite" }

export default async function SharePage({
  params,
}: {
  params: Promise<{ token: string }>
}) {
  const { token } = await params

  return (
    <main className="mx-auto flex min-h-[calc(100svh-3.5rem)] w-full max-w-5xl flex-col items-center justify-center px-6 py-12">
      <ShareInvite token={token} />
    </main>
  )
}
