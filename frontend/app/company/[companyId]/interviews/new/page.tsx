import { getTranslations } from "next-intl/server"

import { BackLink } from "@/components/back-link"
import { NewInterview } from "@/components/company/new-interview"
import { translatedTitle } from "@/lib/site"

export const generateMetadata = () => translatedTitle("interviews", "new")

export default async function NewInterviewPage({
  params,
}: {
  params: Promise<{ companyId: string }>
}) {
  const { companyId } = await params
  const t = await getTranslations("interviews")

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <div className="relative">
        <BackLink href={`/company/${companyId}/interviews`}>
          {t("title")}
        </BackLink>
        <h1 className="font-heading text-3xl font-medium tracking-tight">
          {t("new")}
        </h1>
      </div>
      <NewInterview companyId={companyId} />
    </main>
  )
}
