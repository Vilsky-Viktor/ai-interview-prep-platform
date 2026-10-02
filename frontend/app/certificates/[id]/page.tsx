import type { Metadata } from "next"
import { notFound } from "next/navigation"

import { CopyLinkButton } from "@/components/copy-link-button"
import { Wordmark } from "@/components/wordmark"
import { formatDate } from "@/lib/format"
import { serverFetch } from "@/lib/server-api"
import { pageMetadata } from "@/lib/site"
import type { Certificate } from "@/types/round"

type PageProps = { params: Promise<{ id: string }> }

async function getCertificate(id: string) {
  return serverFetch<Certificate>(`/rounds/certificates/${id}`)
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { id } = await params
  const certificate = await getCertificate(id)

  if (!certificate) {
    return { title: "Certificate" }
  }

  return pageMetadata(
    `${certificate.user_name} · ${certificate.topic_title}`,
    `${certificate.user_name} completed ${certificate.topic_title} with a score of ${certificate.score}%.`,
    `/certificates/${id}`
  )
}

export default async function CertificatePage({ params }: PageProps) {
  const certificate = await getCertificate((await params).id)

  if (!certificate) {
    notFound()
  }

  return (
    <main className="mx-auto max-w-4xl space-y-6 px-6 py-12">
      <div className="space-y-10 rounded-3xl border bg-card px-8 py-14 text-center shadow-sm">
        <div className="flex flex-col items-center gap-6">
          <Wordmark className="text-2xl" />
          <p className="text-3xl font-medium tracking-[0.16em] whitespace-nowrap text-muted-foreground uppercase">
            Certificate of achievement
          </p>
        </div>
        <div className="space-y-3">
          <p className="font-heading text-4xl font-medium tracking-tight text-balance">
            {certificate.user_name}
          </p>
          <p className="text-muted-foreground">For successfully completing:</p>
          <p className="font-heading text-2xl font-medium text-balance">
            {certificate.topic_title}
          </p>
        </div>
        <div className="flex justify-center gap-12 text-sm">
          <div>
            <p className="font-heading text-3xl font-medium text-green-600 tabular-nums dark:text-green-400">
              {certificate.score}%
            </p>
            <p className="text-muted-foreground">Final score</p>
          </div>
          <div>
            <p className="font-heading text-3xl font-medium">
              {formatDate(certificate.issued_at)}
            </p>
            <p className="text-muted-foreground">Issued</p>
          </div>
        </div>
        <p className="font-mono text-xs text-muted-foreground">
          {certificate.id}
        </p>
      </div>
      <div className="flex justify-center">
        <CopyLinkButton />
      </div>
    </main>
  )
}
