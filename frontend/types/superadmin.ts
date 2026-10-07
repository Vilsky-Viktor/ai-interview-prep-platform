import type { components as companies } from "@/types/api/companies"
import type { components } from "@/types/api/library"

type Schemas = components["schemas"]

export type TemplateSummary = Schemas["TemplateSummary"]
export type Template = Schemas["TemplateOut"]
export type TemplateFilters = Schemas["TemplateFiltersOut"]
export type FlaggedQuestion = Schemas["FlaggedQuestionOut"]
export type ReplacedQuestion = Schemas["ReplacedQuestionOut"]

/** A question on the quality tab: flagged now, or one revision of it as replaced. */
export type QualityRow = {
  // Replaced questions: the kept revision, whose reports are listed.
  revision_id?: string
  question_id: string
  text: string
  options: { answer: string; correct: boolean }[]
  flag?: string
  // A flagged template question: it can be fixed now or dismissed.
  actionable?: boolean
  answers: number
  correct: number
  reports: number
  set_title: string
  set_kind: string
  at: string
}

/** A company interview's pass rate, for the monitoring tab. */
export type PassRate = companies["schemas"]["PassRateOut"]

/** A company sent for review, for the verification tab. */
export type VerificationRequest = companies["schemas"]["VerificationRequestOut"]

/** One service's counts in a month, for the stats tab. */
export type Stats = companies["schemas"]["StatsOut"]

/** A revealed question of a template, with its answers, for the public role test pages. */
export type SampleQuestion = Schemas["SampleQuestionOut"]
