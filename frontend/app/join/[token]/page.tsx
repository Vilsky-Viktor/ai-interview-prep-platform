import type { Metadata } from "next"

import { AdminInvite } from "@/components/company/admin-invite"

export const metadata: Metadata = { title: "Company invite" }

export default async function JoinPage({
  params,
}: {
  params: Promise<{ token: string }>
}) {
  const { token } = await params

  return (
    <main className="mx-auto flex min-h-[calc(100svh-3.5rem)] w-full max-w-5xl flex-col items-center justify-center px-6 py-12">
      <AdminInvite token={token} />
    </main>
  )
}
