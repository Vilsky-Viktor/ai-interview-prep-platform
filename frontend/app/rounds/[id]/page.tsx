import type { Metadata } from "next"
import { getTranslations } from "next-intl/server"

import { RoundView } from "@/components/rounds/round-view"

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("rounds")

  return { title: t("title") }
}

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
