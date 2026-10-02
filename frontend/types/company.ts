import type { components as companies } from "@/types/api/companies"
import type { components as rounds } from "@/types/api/rounds"

type Schemas = companies["schemas"]
type RoundSchemas = rounds["schemas"]

export type Company = Schemas["CompanyOut"]
export type CompanyMember = Schemas["MemberOut"]
export type AdminInvite = Schemas["AdminInviteOut"]
export type Interview = Schemas["InterviewOut"]
export type InterviewDetail = Schemas["InterviewDetail"]
export type Candidate = Schemas["CandidateOut"]
export type InviteView = Schemas["InviteView"]
export type SessionSummary = Schemas["SessionSummary"]
export type SessionTopic = RoundSchemas["SessionTopicOut"]
export type InterviewSession = RoundSchemas["SessionOut"]
// The option picked is kept on the client to mark it after the answer.
export type SessionAnswerResult = RoundSchemas["SessionAnswerResult"] & {
  option_index?: number | null
}
