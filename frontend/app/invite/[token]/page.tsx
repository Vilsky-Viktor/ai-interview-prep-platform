import type { Metadata } from "next"

import { InviteView } from "@/components/company/invite-view"

export const metadata: Metadata = { title: "Interview invite" }

export default async function InvitePage({
  params,
}: {
  params: Promise<{ token: string }>
}) {
  const { token } = await params

  return (
    <main className="mx-auto flex min-h-[calc(100svh-3.5rem)] w-full max-w-5xl flex-col items-center justify-center px-6 py-12">
      <InviteView token={token} />
    </main>
  )
}
