import type { REPORT_REASONS } from "@/constants/feedback"

export type ReportReason = keyof typeof REPORT_REASONS

export type QuestionReport = {
  id: string
  reason: string
  comment: string
  created_at: string
}

export type QuestionStats = {
  id: string
  text: string
  likes: number
  dislikes: number
  reports: number
}
