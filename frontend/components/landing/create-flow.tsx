"use client"

import { cn } from "cn"
import { useTranslations } from "next-intl"
import { useRef } from "react"

import { Caret } from "@/components/landing/caret"
import { DemoPanel } from "@/components/landing/demo-panel"
import { DemoPointer } from "@/components/landing/demo-pointer"
import { DemoWriting } from "@/components/landing/demo-writing"
import { FlowArrows } from "@/components/landing/flow-arrows"
import { SubtopicChip, TopicCard } from "@/components/landing/topic-card"
import { TypedDescription } from "@/components/landing/typed-description"
import { buttonVariants } from "@/components/ui/button"
import {
  DEMO_ADDED_SUBTOPIC,
  DEMO_CHANGE,
  DEMO_DESCRIPTION,
  DEMO_EDITED,
  DEMO_NEW_TOPIC,
  DEMO_TOPICS,
} from "@/constants/create-demo"
import {
  countedAt,
  type DemoStep,
  pointedAt,
  useDemoSteps,
} from "@/hooks/use-demo-steps"

// The pointer clicks into the box and the description is typed, then it clicks send; the topics
// show one by one; it clicks into a topic and a subtopic is typed, then into the request for
// changes, which is typed, then clicks apply and a topic is added; then it clicks approve and
// the questions are written, topic by topic.
const STEPS: DemoStep[] = [
  { name: "empty", ms: 900, point: "field" },
  { name: "focus", ms: 300, click: true },
  { name: "typing", ms: 30, repeat: DEMO_DESCRIPTION.length },
  { name: "aim", ms: 800, point: "send" },
  { name: "send", ms: 500, click: true },
  { name: "sent", ms: 400, point: "none" },
  { name: "topics", ms: 400, repeat: DEMO_TOPICS.length },
  { name: "review", ms: 900, point: "topic" },
  { name: "open", ms: 300, click: true },
  { name: "adding", ms: 90, repeat: DEMO_ADDED_SUBTOPIC.length },
  { name: "edited", ms: 900, point: "ask" },
  { name: "ask", ms: 300, click: true },
  { name: "asking", ms: 50, repeat: DEMO_CHANGE.length },
  { name: "aimApply", ms: 800, point: "apply" },
  { name: "apply", ms: 500, click: true },
  { name: "applying", ms: 800, point: "none" },
  { name: "applied", ms: 1200 },
  { name: "aimGo", ms: 800, point: "apply" },
  { name: "go", ms: 500, click: true },
  { name: "writing", ms: 130, repeat: 20, point: "none" },
  { name: "written", ms: 3000 },
]
// What the pointer moves to in each panel.
const DESCRIBE = ["field", "send"]
const ADJUST = ["topic", "ask", "apply"]
const APPLIED = STEPS.findIndex(({ name }) => name === "applied")
const WRITING = STEPS.findIndex(({ name }) => name === "writing")
// The topics the questions are written for: the adjusted ones.
const WRITTEN = [...DEMO_TOPICS, DEMO_NEW_TOPIC].map(({ name }) => name)

/** The first way to create an interview, as two panels joined by arrows: a job description
 * typed and sent, then the topics it gives, adjusted by hand and by asking the AI. Every row
 * keeps its place before it shows, so the panels never change size. */
export function CreateFlow({
  labels,
}: {
  labels: { describe: string; adjust: string; ask: string }
}) {
  const start = useTranslations("start")
  const generation = useTranslations("generation")
  const { ref: playRef, ...at } = useDemoSteps<HTMLDivElement>(STEPS)
  const step = STEPS[at.index].name
  const letters = countedAt(STEPS, at, "typing", DEMO_DESCRIPTION.length)
  const shown = countedAt(STEPS, at, "topics", DEMO_TOPICS.length)
  const added = countedAt(STEPS, at, "adding", DEMO_ADDED_SUBTOPIC.length)
  const asked = countedAt(STEPS, at, "asking", DEMO_CHANGE.length)
  const adding = step === "open" || step === "adding"
  const asking = ["asking", "aimApply", "apply", "applying"].includes(step)
  const fieldRef = useRef<HTMLParagraphElement>(null)
  const sendRef = useRef<HTMLSpanElement>(null)
  const topicRef = useRef<HTMLSpanElement>(null)
  const askRef = useRef<HTMLDivElement>(null)
  const applyRef = useRef<HTMLSpanElement>(null)
  const targets = {
    field: fieldRef,
    send: sendRef,
    topic: topicRef,
    ask: askRef,
    apply: applyRef,
  }
  const point = pointedAt(STEPS, at.index)
  const clicking = STEPS[at.index].click === true

  // The pointer in `panel`, on what it points at there.
  function pointer(panel: string[]) {
    const on = point && panel.includes(point) ? point : null

    return (
      <DemoPointer
        target={on ? targets[on as keyof typeof targets] : null}
        clicking={clicking && on !== null}
        click={at.index}
      />
    )
  }

  return (
    <>
      <DemoPanel ref={playRef} label={labels.describe}>
        {pointer(DESCRIBE)}
        <TypedDescription
          ref={fieldRef}
          sendRef={sendRef}
          full={DEMO_DESCRIPTION}
          letters={step === "empty" ? null : letters}
          typing={step === "typing"}
          placeholder={start("placeholder")}
          pressed={step === "send"}
        />
      </DemoPanel>
      <FlowArrows />
      <DemoPanel label={labels.adjust}>
        {pointer(ADJUST)}
        {/* The review, then the questions being written in its place. */}
        <div className="grid flex-1 *:[grid-area:1/1]">
          <div
            className={cn(
              "flex flex-col gap-3",
              at.index >= WRITING && "invisible opacity-0"
            )}
          >
            <ul className="flex-1 space-y-2">
              {DEMO_TOPICS.map((topic, position) => {
                const edited = topic.name === DEMO_EDITED

                return (
                  <TopicCard
                    key={topic.name}
                    name={topic.name}
                    hidden={position >= shown}
                    highlighted={edited && adding}
                  >
                    {topic.subtopics.map((subtopic) => (
                      <SubtopicChip key={subtopic}>{subtopic}</SubtopicChip>
                    ))}
                    {/* The added subtopic keeps its place, unseen, until it's typed; sized by
                      the whole word (and caret) all along, so nothing moves as it's typed. */}
                    {edited && (
                      <SubtopicChip
                        ref={topicRef}
                        typing={adding}
                        hidden={!adding && added === 0}
                      >
                        <span className="grid *:[grid-area:1/1]">
                          {/* The caret's width as padding. */}
                          <span className="invisible pe-0.5">
                            {DEMO_ADDED_SUBTOPIC}
                          </span>
                          <span className="flex h-4 items-center">
                            {DEMO_ADDED_SUBTOPIC.slice(0, added)}
                            {adding && <Caret />}
                          </span>
                        </span>
                      </SubtopicChip>
                    )}
                  </TopicCard>
                )
              })}
              <TopicCard name={DEMO_NEW_TOPIC.name} hidden={at.index < APPLIED}>
                {DEMO_NEW_TOPIC.subtopics.map((subtopic) => (
                  <SubtopicChip key={subtopic}>{subtopic}</SubtopicChip>
                ))}
              </TopicCard>
            </ul>
            {/* The request for changes, as the review's box, and its button. */}
            <div
              ref={askRef}
              className="flex h-10 items-center rounded-full bg-muted px-4 dark:bg-card"
            >
              {asking ? (
                <span className="flex h-5 min-w-0 items-center">
                  <span className="truncate">
                    {DEMO_CHANGE.slice(0, asked)}
                  </span>
                  {step === "asking" && <Caret />}
                </span>
              ) : (
                <span className="truncate text-muted-foreground">
                  {labels.ask}
                </span>
              )}
            </div>
            <div className="flex justify-end">
              <span
                ref={applyRef}
                className={buttonVariants({
                  size: "sm",
                  className: cn(
                    "lowercase",
                    step === "applying" && "opacity-50",
                    (step === "apply" || step === "go") && "ring-3 ring-ring/50"
                  ),
                })}
              >
                {/* As the real button: applying the changes while there are some, else
                  approving the topics. */}
                {asking ? generation("apply") : generation("approve")}
              </span>
            </div>
          </div>
          <div
            className={cn("flex", at.index < WRITING && "invisible opacity-0")}
          >
            <DemoWriting
              topics={WRITTEN}
              percent={countedAt(STEPS, at, "writing", 20) * 5}
            />
          </div>
        </div>
      </DemoPanel>
    </>
  )
}
