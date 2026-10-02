export const REPORT_REASONS = {
  wrong_answer: "The marked answer is wrong",
  unclear: "The question is unclear",
  off_topic: "It doesn't fit the topic",
  other: "Something else",
} as const

export const FEEDBACK_HOVER_CLASS =
  "text-muted-foreground transition-colors hover:bg-foreground/10 hover:text-foreground dark:hover:bg-foreground/15"

export const MAX_REPORT_COMMENT_LENGTH = 1000
export const MAX_RATING = 5
