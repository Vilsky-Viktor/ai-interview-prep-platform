import type { components as ats } from "@/types/api/ats"
import type { components as companies } from "@/types/api/companies"
import type { components as rounds } from "@/types/api/rounds"
import type { ReviewItem } from "@/types/round"

type Schemas = companies["schemas"]
type RoundSchemas = rounds["schemas"]
type AtsSchemas = ats["schemas"]

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
// A test's shareable job-ad link, as someone opening it sees it.
export type JobLink = Schemas["LinkView"]
export type InterviewSettingsData = Schemas["InterviewSettings"]
export type SessionSummary = Schemas["SessionSummary"]
export type SessionTopic = RoundSchemas["SessionTopicOut"]
export type InterviewSession = RoundSchemas["SessionOut"]
export type InterviewStep = RoundSchemas["InterviewStep"]
// The option picked is kept on the client to mark it after the answer.
export type SessionAnswerResult = RoundSchemas["SessionAnswerResult"] & {
  option_index?: number | null
}
export type CompanyReferral = Schemas["ReferralOut"]
// One movement of a company's credits, and a candidate whose invite holds or was charged credits.
export type CreditHistoryEntry = Schemas["HistoryEntryOut"]
export type CreditCandidate = Schemas["CreditCandidateOut"]
export type AtsIntegrations = AtsSchemas["IntegrationsOut"]
export type AtsConnection = AtsSchemas["ConnectionOut"]
export type AtsItem = AtsSchemas["AtsItemOut"]
export type AtsJobLink = AtsSchemas["JobLinkOut"]

/** A candidate's result as the PDF report and the shared summary show it. */
export type CandidateReportData = {
  company: string
  logoUrl: string | null
  verifiedDomain: string | null
  title: string | null
  email: string
  name: string | null
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
export type VerificationStatus = Schemas["VerificationStatus"]

/** A candidate's scorecard: their result per section, with their answers. */
export type Scorecard = {
  id: string
  email: string
  // The name from the candidate's sign-in, or as an owner or admin corrected it; null when unknown.
  name: string | null
  status: string
  // Extra time on each question, in percent, and the amounts still offered (none once started).
  extra_time: number
  extra_time_options: number[]
  // Whether the user may resend, revoke or delete the candidate: owners and admins.
  can_edit: boolean
  // The invite link's token while the candidate hasn't started and it works; null otherwise.
  invite_token: string | null
  // For the PDF report: the test, the company and the overall result.
  title: string | null
  company: string
  logo_url: string | null
  verified_domain: string | null
  grade: number | null
  passed: boolean | null
  pass_mark: number
  sessions: {
    id: string
    topic_title: string
    status: string
    final_score: number | null
    // Against the test's passing grade; null while the section is still going.
    passed: boolean | null
    tab_leaves: number
    copies: number
    fast_answers: number
    review: ReviewItem[]
  }[]
}
