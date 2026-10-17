"use client"

import { cn } from "cn"
import { useTranslations } from "next-intl"
import { useRef } from "react"

import { DemoPanel } from "@/components/landing/demo-panel"
import { DemoPointer } from "@/components/landing/demo-pointer"
import { InterviewHeader } from "@/components/landing/interview-header"
import { TemplateRow } from "@/components/landing/template-row"
import { TopicCard } from "@/components/landing/topic-card"
import { TypedSearch } from "@/components/landing/typed-search"
import { buttonVariants } from "@/components/ui/button"
import {
  DEMO_PICKED,
  DEMO_SEARCH,
  DEMO_TEMPLATES,
  DEMO_TEMPLATE_TOPICS,
} from "@/constants/create-demo"
import {
  countedAt,
  type DemoStep,
  pointedAt,
  useDemoSteps,
} from "@/hooks/use-demo-steps"

// The pointer clicks into the search and it's typed, the list narrows to it, the pointer picks
// a template and clicks "use template", then the interview it creates opens.
const STEPS: DemoStep[] = [
  { name: "empty", ms: 900, point: "search" },
  { name: "focus", ms: 300, click: true },
  { name: "typing", ms: 110, repeat: DEMO_SEARCH.length },
  { name: "found", ms: 900, point: "row" },
  { name: "pick", ms: 400, click: true },
  { name: "aim", ms: 800, point: "use" },
  { name: "use", ms: 600, click: true },
  { name: "opened", ms: 4000, point: "none" },
]
const TYPING = STEPS.findIndex(({ name }) => name === "typing")

const FOUND = DEMO_TEMPLATES.filter(({ title }) =>
  title.toLowerCase().includes(DEMO_SEARCH)
)

/** The other way to create an interview: a template searched, used, and its interview open.
 * The list, the templates found and the interview share one place, so the panel never changes
 * size. */
export function CreateTemplateDemo() {
  const t = useTranslations("templates")
  const { ref: playRef, ...at } = useDemoSteps<HTMLDivElement>(STEPS)
  const step = STEPS[at.index].name
  const letters = countedAt(STEPS, at, "typing", DEMO_SEARCH.length)
  const found = at.index > TYPING
  const opened = step === "opened"
  const picked = ["pick", "aim", "use"].includes(step)
  const searchRef = useRef<HTMLDivElement>(null)
  const rowRef = useRef<HTMLLIElement>(null)
  const buttonRef = useRef<HTMLSpanElement>(null)
  const targets = { search: searchRef, row: rowRef, use: buttonRef }
  const point = pointedAt(STEPS, at.index)

  return (
    <DemoPanel ref={playRef}>
      <DemoPointer
        target={
          point && point in targets
            ? targets[point as keyof typeof targets]
            : null
        }
        clicking={STEPS[at.index].click === true}
        click={at.index}
      />
      <div className="grid flex-1 *:[grid-area:1/1]">
        {/* The search over the whole list and over the templates found, each keeping its
            place while the other shows. */}
        {[DEMO_TEMPLATES, FOUND].map((templates) => (
          <div
            key={templates.length}
            className={cn(
              "flex flex-col gap-3",
              (opened || (templates === FOUND) !== found) &&
                "invisible opacity-0"
            )}
          >
            <TypedSearch
              ref={templates === FOUND ? searchRef : undefined}
              text={at.index < TYPING ? null : DEMO_SEARCH.slice(0, letters)}
              typing={step === "typing"}
              placeholder={t("search")}
            />
            <ul className="divide-y overflow-hidden rounded-2xl border">
              {templates.map((template) => (
                <TemplateRow
                  key={template.title}
                  ref={
                    templates === FOUND && template === DEMO_PICKED
                      ? rowRef
                      : undefined
                  }
                  {...template}
                  picked={picked && template === DEMO_PICKED}
                />
              ))}
            </ul>
            {/* The picked template's action, at the panel's foot, the list's width; in its
                place from the start, seen once a template is picked. */}
            <span
              ref={templates === FOUND ? buttonRef : undefined}
              className={buttonVariants({
                className: cn(
                  "mt-auto w-full lowercase",
                  !picked && "invisible opacity-0",
                  step === "use" && "ring-3 ring-ring/50"
                ),
              })}
            >
              {t("use")}
            </span>
          </div>
        ))}
        {/* The interview's page, small: its title, status and size, then its topics. */}
        <div className={cn("space-y-3", !opened && "invisible opacity-0")}>
          <InterviewHeader
            title={DEMO_PICKED.title}
            topics={DEMO_PICKED.topics}
            questions={DEMO_PICKED.questions}
          />
          <ul className="space-y-2">
            {DEMO_TEMPLATE_TOPICS.map((topic) => (
              <TopicCard key={topic} name={topic} />
            ))}
          </ul>
        </div>
      </div>
    </DemoPanel>
  )
}
