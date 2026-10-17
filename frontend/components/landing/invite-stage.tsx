"use client"

import { cn } from "cn"
import {
  BotIcon,
  BracesIcon,
  FileUpIcon,
  LinkIcon,
  MailIcon,
  PanelsTopLeftIcon,
  SparklesIcon,
} from "lucide-react"
import { useCallback, useEffect, useRef, useState } from "react"

import { KeepAcronyms } from "@/components/keep-acronyms"
import { ArrivingCandidates } from "@/components/landing/arriving-candidates"
import { SOURCE_CARD } from "@/components/landing/demo-panel"
import { InterviewHeader } from "@/components/landing/interview-header"
import { Wire } from "@/components/landing/wire"
import { ATS_PROVIDERS } from "@/constants/ats"
import {
  DEMO_INVITE_CANDIDATES,
  DEMO_INVITE_INTERVIEW,
  INVITE_SOURCES,
  INVITE_WIRE_GAP,
  INVITE_WIRE_INSET,
  type InviteSource,
  PHONE_ATS_LOGOS,
  INVITE_SPEED,
} from "@/constants/invite-demo"
import { ON_SCREEN, useDemoSteps } from "@/hooks/use-demo-steps"
import { boxOf, sourceWires } from "@/lib/source-wires"

const ICONS = {
  email: MailIcon,
  file: FileUpIcon,
  link: LinkIcon,
  api: BracesIcon,
  sdk: PanelsTopLeftIcon,
  agent: SparklesIcon,
  apps: BotIcon,
}

/** The interview in the middle and the ways candidates come into it around it, each a small
 * floating card with a wire to the interview and a candidate running along it to it, counted
 * in as they arrive. From laptops
 * up the ways sit on both sides at their own heights; below, half in a row above and half
 * below. Plays while on screen; with reduced motion, the wires alone and nothing floats. */
export function InviteStage({
  labels,
  interview,
}: {
  labels: Record<InviteSource["key"], string>
  // The pill on the interview card's top edge.
  interview: string
}) {
  const { ref, index } = useDemoSteps<HTMLDivElement>(ON_SCREEN)
  const playing = ON_SCREEN[index].name === "playing"
  const cardRef = useRef<HTMLDivElement>(null)
  const sourceRefs = useRef<(HTMLLIElement | null)[]>([])
  const [wires, setWires] = useState<string[]>([])
  // Candidates arrived since it started playing, back to none after a while.
  const [arrived, setArrived] = useState(0)
  const arrive = useCallback(
    () => setArrived((count) => (count + 1) % DEMO_INVITE_CANDIDATES.arrivals),
    []
  )

  // Back to none whenever it stops (off screen).
  const [wasPlaying, setWasPlaying] = useState(playing)

  if (wasPlaying !== playing) {
    setWasPlaying(playing)
    setArrived(0)
  }

  // The wires, from where the cards are laid out (their float moves them only a little, over
  // the wires' ends), again whenever a card or the stage changes size.
  useEffect(() => {
    const stage = ref.current
    const card = cardRef.current

    if (!stage || !card) {
      return
    }

    const sources = sourceRefs.current.filter((element) => element !== null)
    const observer = new ResizeObserver(() =>
      setWires(
        sourceWires(
          boxOf(card),
          sources.map(boxOf),
          INVITE_WIRE_GAP,
          INVITE_WIRE_INSET
        )
      )
    )

    for (const element of [stage, card, ...sources]) {
      observer.observe(element)
    }

    return () => observer.disconnect()
  }, [ref])

  const list = (sources: readonly InviteSource[], offset: number) => (
    <ul className="grid grid-cols-[repeat(4,minmax(0,1fr))] gap-2 lg:contents">
      {sources.map((source, at) => (
        <Source
          key={source.key}
          ref={(element) => {
            sourceRefs.current[offset + at] = element
          }}
          source={source}
          label={labels[source.key]}
          floating={playing}
        />
      ))}
    </ul>
  )

  return (
    <div
      ref={ref}
      aria-hidden
      className="relative flex flex-col gap-12 lg:block lg:h-112"
    >
      {/* Drawn anew as it starts playing, so the candidates start then, each after its delay. */}
      <svg
        key={String(playing)}
        className="pointer-events-none absolute inset-0 size-full overflow-visible text-ring"
      >
        {wires.map((d, at) => (
          <Wire
            key={INVITE_SOURCES[at].key}
            d={d}
            delay={INVITE_SOURCES[at].delay}
            fired={playing ? undefined : 0}
            traveller="candidate"
            speed={INVITE_SPEED}
            onArrive={arrive}
          />
        ))}
      </svg>
      {list(INVITE_SOURCES.slice(0, 4), 0)}
      <div
        ref={cardRef}
        className="relative z-10 mx-auto w-full max-w-88 space-y-5 rounded-3xl bg-muted p-6 text-start lg:absolute lg:inset-0 lg:m-auto lg:h-fit dark:bg-card"
      >
        {/* What the card is, on its top edge. */}
        <span className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border bg-background px-4 py-1 text-sm text-muted-foreground lowercase">
          {interview}
        </span>
        <InterviewHeader {...DEMO_INVITE_INTERVIEW} large />
        <ArrivingCandidates arrived={arrived} />
      </div>
      {list(INVITE_SOURCES.slice(4), 4)}
    </div>
  )
}

/** One way in: its icon (or the ATSs' logos, overlapping) and its short label, floating
 * gently while `floating`. A cell of the grid on phones and tablets; from laptops up, placed on
 * its side of the stage. */
function Source({
  ref,
  source,
  label,
  floating,
}: {
  ref: React.Ref<HTMLLIElement>
  source: InviteSource
  label: string
  floating: boolean
}) {
  const Icon = source.key === "ats" ? null : ICONS[source.key]

  return (
    <li
      ref={ref}
      style={
        {
          "--x": `${source.x}%`,
          "--y": `${source.y}%`,
          "--float": `${source.sway}s`,
          "--phase": `${-source.phase}s`,
        } as React.CSSProperties
      }
      className={cn(
        SOURCE_CARD,
        "lg:absolute lg:top-(--y)",
        source.side === "start" ? "lg:start-(--x)" : "lg:end-(--x)",
        floating &&
          "lg:motion-safe:animate-[source-float_var(--float)_ease-in-out_var(--phase)_infinite]"
      )}
    >
      {Icon ? (
        <Icon className="size-6 shrink-0 text-primary" />
      ) : (
        <span className="flex -space-x-1.5 rtl:space-x-reverse">
          {/* All of them from laptops up; three in a phone's narrow card. */}
          {ATS_PROVIDERS.map((provider, index) => (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              key={provider.id}
              src={provider.logo}
              alt=""
              className={cn(
                "size-6 rounded-md bg-background object-contain ring-2 ring-muted dark:ring-card",
                index >= PHONE_ATS_LOGOS && "max-lg:hidden"
              )}
            />
          ))}
        </span>
      )}
      <span>
        <KeepAcronyms text={label} />
      </span>
    </li>
  )
}
