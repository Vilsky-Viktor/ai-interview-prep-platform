import { GoalForm } from "@/components/goal-form"
import { HomeTitle } from "@/components/home-title"

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-[calc(100svh-3.5rem)] w-full max-w-3xl flex-col items-center justify-center px-6 pb-24">
      <div className="inline-grid max-w-full gap-16">
        <div className="space-y-4 text-center">
          <HomeTitle />
          <p className="text-left text-base text-balance text-muted-foreground">
            AI agents practice with you until you&apos;re confident.
          </p>
        </div>
        <div className="min-w-0">
          <GoalForm />
        </div>
      </div>
    </main>
  )
}
