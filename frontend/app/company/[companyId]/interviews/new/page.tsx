import type { Metadata } from "next"

import { BackLink } from "@/components/back-link"
import { NewInterview } from "@/components/company/new-interview"

export const metadata: Metadata = { title: "New interview" }

export default async function NewInterviewPage({
  params,
}: {
  params: Promise<{ companyId: string }>
}) {
  const { companyId } = await params

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <div className="relative">
        <BackLink href={`/company/${companyId}/interviews`}>Interviews</BackLink>
        <h1 className="font-heading text-3xl font-medium tracking-tight">
          New interview
        </h1>
      </div>
      <NewInterview companyId={companyId} />
    </main>
  )
}
