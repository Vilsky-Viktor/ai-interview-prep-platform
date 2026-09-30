import { PlusIcon } from "lucide-react"
import type { Metadata } from "next"
import Link from "next/link"

import { PreparationList } from "@/components/preparations/preparation-list"
import { SignInPrompt } from "@/components/sign-in-prompt"
import { Button } from "@/components/ui/button"
import { isPreparationDone } from "@/lib/rounds"
import { serverFetch } from "@/lib/server-api"
import type { PreparationSummary } from "@/types/preparation"
import type { MasteredTopic } from "@/types/round"

export const metadata: Metadata = { title: "My preparations" }

export default async function PreparationsPage() {
  const [mine, joined, masteredTopics] = await Promise.all([
    serverFetch<PreparationSummary[]>("/library/preparations"),
    serverFetch<PreparationSummary[]>("/library/preparations/joined"),
    serverFetch<MasteredTopic[]>("/rounds/preparations/mastered"),
  ])
  const masteredByPrep = new Map<string, Set<string>>()

  for (const item of masteredTopics ?? []) {
    const current = masteredByPrep.get(item.preparation_id) ?? new Set<string>()

    current.add(item.topic_id)
    masteredByPrep.set(item.preparation_id, current)
  }

  const items = mine
    ? [
        ...mine.map((item) => ({
          ...item,
          owned: true,
          done: isPreparationDone(
            item.topic_count,
            masteredByPrep.get(item.id)?.size ?? 0
          ),
        })),
        ...(joined ?? []).map((item) => ({
          ...item,
          owned: false,
          done: isPreparationDone(
            item.topic_count,
            masteredByPrep.get(item.id)?.size ?? 0
          ),
        })),
      ].sort((a, b) => (a.created_at < b.created_at ? 1 : -1))
    : null

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

      {!items && (
        <SignInPrompt message="Sign in to see your preparations." />
      )}

      {items && items.length === 0 && (
        <p className="py-16 text-center text-muted-foreground">
          No preparations yet. Create your first one or pick from the public library.
        </p>
      )}

      {items && items.length > 0 && (
        <PreparationList preparations={items} className="p-6" />
      )}
    </main>
  )
}
