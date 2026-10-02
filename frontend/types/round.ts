import type { components } from "@/types/api/rounds"

type Schemas = components["schemas"]

export type Round = Schemas["RoundOut"]
export type AnswerView = Schemas["AnswerView"]
export type ReviewItem = Schemas["ReviewItem"]
// Messages show before the server stores them, so the client needs only these fields.
export type ChatMessage = Pick<Schemas["ChatMessageOut"], "role" | "content">
export type Certificate = Schemas["CertificateOut"]
/** How far the user is towards a topic's certificate; missing until they practice it. */
export type TopicProgress = Schemas["TopicProgressOut"]
export type MasteredTopic = Schemas["MasteredTopicOut"]
export type NextQuestion = Schemas["NextQuestion"]
// The option picked is kept on the client to mark it after the answer. The right option can be
// null because candidate results reuse this shape and may not reveal it.
export type AnswerResult = Omit<
  Schemas["AnswerResult"],
  "correct_option_index"
> & {
  correct_option_index: number | null
  option_index?: number | null
}
export type AnswerInput = Omit<Schemas["AnswerCreate"], "question_id">
