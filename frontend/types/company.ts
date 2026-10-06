import type { components as companies } from "@/types/api/companies"
import type { components as rounds } from "@/types/api/rounds"

type Schemas = companies["schemas"]
type RoundSchemas = rounds["schemas"]

export type Company = Schemas["CompanyOut"]
export type CompanyBalance = Schemas["CompanyBalanceOut"]
export type CompanyMember = Schemas["MemberOut"]
export type AdminInvite = Schemas["AdminInviteOut"]
export type Interview = Schemas["InterviewOut"]
export type InterviewDetail = Schemas["InterviewDetail"]
export type Candidate = Schemas["CandidateOut"]
export type InterviewReportData = Schemas["InterviewReportOut"]
export type CandidateFilters = Schemas["CandidateFiltersOut"]
export type InviteView = Schemas["InviteView"]
export type SessionSummary = Schemas["SessionSummary"]
export type SessionTopic = RoundSchemas["SessionTopicOut"]
export type InterviewSession = RoundSchemas["SessionOut"]
// The option picked is kept on the client to mark it after the answer.
export type SessionAnswerResult = RoundSchemas["SessionAnswerResult"] & {
  option_index?: number | null
}
export type CompanyReferral = Schemas["ReferralOut"]

/** A candidate's result as the PDF report and the shared summary show it. */
export type CandidateReportData = {
  company: string
  logoUrl: string | null
  verifiedDomain: string | null
  title: string | null
  email: string
  grade: number | null
  passed: boolean | null
  passMark: number
  sections: {
    id: string
    topic_title: string
    final_score: number | null
    passed: boolean | null
    tab_leaves: number
    copies: number
    fast_answers: number
  }[]
}
export type BulkInviteResult = Schemas["BulkInviteOut"]
export type Brand = Schemas["BrandOut"]
export type Verification = Schemas["VerificationOut"]
