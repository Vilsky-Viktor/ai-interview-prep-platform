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

  // Laid out like the home page's start: a title and the box, nothing else.
  return (
    <main className="mx-auto max-w-5xl px-6">
      <div className="flex min-h-[calc(100svh-3.5rem)] flex-col items-center justify-center pb-24">
        <div className="w-full max-w-176 space-y-10">
          <div className="relative">
            <BackLink
              href={`/company/${companyId}/interviews`}
              className="xl:top-2.5"
            >
              {t("title")}
            </BackLink>
            <h1 className="font-heading text-5xl font-medium tracking-tight text-balance sm:text-6xl">
              {t("createTitle")}
            </h1>
          </div>
          <NewInterview companyId={companyId} />
        </div>
      </div>
    </main>
  )
}
