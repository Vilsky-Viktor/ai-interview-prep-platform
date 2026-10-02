import type { REPORT_REASONS } from "@/constants/feedback"
import type { components } from "@/types/api/library"

type Schemas = components["schemas"]

export type ReportReason = keyof typeof REPORT_REASONS
export type QuestionReport = Schemas["ReportOut"]
export type QuestionStats = Schemas["QuestionText"]
