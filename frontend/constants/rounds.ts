import { ListChecksIcon, PenLineIcon, type LucideIcon } from "lucide-react"

import type { RoundMode } from "@/types/round"

export const ROUND_MODES: RoundMode[] = ["choice", "open"]

export const MODE_LABELS: Record<RoundMode, string> = {
  choice: "Multi choice",
  open: "Open answer",
}

export const MODE_ICONS: Record<RoundMode, LucideIcon> = {
  choice: ListChecksIcon,
  open: PenLineIcon,
}

export const MODE_HINTS: Record<RoundMode, string> = {
  choice: "Pick the right option for each question.",
  open: "Write your own answer and get feedback.",
}

export const MAX_ANSWER_LENGTH = 5000
export const MAX_CHAT_MESSAGE_LENGTH = 2000
export const OPEN_ANSWER_FORM_ID = "open-answer-form"
export const PASSING_SCORE = 70
export const CERTIFICATE_RULES = [
  "A topic counts as mastered once you earn its certificate.",
  "Answer every question of the topic in Open answer rounds. It can take several rounds.",
  "Only your latest answer to each question counts.",
  `Your average across all the topic's questions must be ${PASSING_SCORE}% or higher.`,
  "Each round shows questions you haven't answered yet first, then your weakest ones.",
  "Multiple choice rounds don't count towards the certificate.",
]
