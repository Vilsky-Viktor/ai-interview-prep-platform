import { PlusIcon } from "lucide-react"
import type { Metadata } from "next"
import Link from "next/link"

import { UnfinishedGenerations } from "@/components/generation/unfinished-generations"
import { PreparationList } from "@/components/preparations/preparation-list"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { Button } from "@/components/ui/button"
import { PAGE_SIZE } from "@/constants/lists"
import { serverFetch } from "@/lib/server-api"
import type { GenerationSummary } from "@/types/generation"
import type { MyPreparation } from "@/types/preparation"
import type { MasteredTopic } from "@/types/round"

export const metadata: Metadata = { title: "My preparations" }

export default async function PreparationsPage() {
  // The first page renders on the server; the rest load as the user scrolls.
  const [first, masteredTopics, unfinished] = await Promise.all([
    serverFetch<MyPreparation[]>(`/library/preparations?limit=${PAGE_SIZE}`),
    serverFetch<MasteredTopic[]>("/rounds/preparations/mastered"),
    serverFetch<GenerationSummary[]>(
      `/generate/generations?limit=${PAGE_SIZE}`
    ),
  ])
  const mastered: Record<string, number> = {}

  for (const item of masteredTopics ?? []) {
    mastered[item.preparation_id] = (mastered[item.preparation_id] ?? 0) + 1
  }

  return (
    <main className="mx-auto max-w-5xl space-y-8 px-6 py-12">
      <div className="flex items-center justify-between gap-4">
        <h1 className="font-heading text-3xl font-medium tracking-tight">
          My preparations
        </h1>
        <Button
          render={<Link href="/" />}
          nativeButton={false}
          size="icon"
          className="size-14 rounded-full"
          aria-label="New preparation"
        >
          <PlusIcon className="size-6" />
        </Button>
      </div>

      {!first && <SignInPrompt message="Sign in to see your preparations." />}

      {unfinished && unfinished.length > 0 && (
        <UnfinishedGenerations generations={unfinished} />
      )}

      {first && (
        <PreparationList
          path="/library/preparations"
          initial={first}
          mastered={mastered}
          className="p-6"
          empty={
            (unfinished ?? []).length === 0 && (
              <p className="py-16 text-center text-muted-foreground">
                No preparations yet. Create your first one or pick from the
                public library.
              </p>
            )
          }
        />
      )}
    </main>
  )
}
