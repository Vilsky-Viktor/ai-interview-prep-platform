import { PlusIcon } from "lucide-react"
import type { Metadata } from "next"
import Link from "next/link"
import { getTranslations } from "next-intl/server"

import { UnfinishedGenerations } from "@/components/generation/unfinished-generations"
import { PreparationList } from "@/components/preparations/preparation-list"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { Button } from "@/components/ui/button"
import { PAGE_SIZE } from "@/constants/lists"
import { serverFetch } from "@/lib/server-api"
import type { GenerationSummary } from "@/types/generation"
import type { MyPreparation } from "@/types/preparation"

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("preparations")

  return { title: t("title") }
}

export default async function PreparationsPage() {
  const t = await getTranslations("preparations")
  // The first page renders on the server; the rest load as the user scrolls.
  const [first, unfinished] = await Promise.all([
    serverFetch<MyPreparation[]>(`/library/preparations?limit=${PAGE_SIZE}`),
    serverFetch<GenerationSummary[]>(
      `/generate/generations?limit=${PAGE_SIZE}`
    ),
  ])

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <div className="flex items-center justify-between gap-4">
        <h1 className="font-heading text-3xl font-medium tracking-tight">
          {t("title")}
        </h1>
        <Button
          render={<Link href="/" />}
          nativeButton={false}
          size="icon"
          className="size-14 rounded-full"
          aria-label={t("new")}
        >
          <PlusIcon className="size-6" />
        </Button>
      </div>

      {!first && <SignInPrompt message={t("signIn")} />}

      {unfinished && unfinished.length > 0 && (
        <UnfinishedGenerations generations={unfinished} />
      )}

      {first && (
        <PreparationList
          path="/library/preparations"
          initial={first}
          className="p-6"
          empty={
            (unfinished ?? []).length === 0 && (
              <p className="py-16 text-center text-muted-foreground">
                {t("empty")}
              </p>
            )
          }
        />
      )}
    </main>
  )
}
