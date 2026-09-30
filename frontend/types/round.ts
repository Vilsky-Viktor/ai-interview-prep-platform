export type RoundMode = "open" | "choice"

export type Round = {
  id: string
  topic_id: string
  preparation_id: string
  topic_title: string
  mode: RoundMode
  status: "in_progress" | "finished"
  total: number
  answered: number
  current_score: number | null
  final_score: number | null
  started_at: string
  finished_at: string | null
  certificate_id: string | null
}

export type AnswerView = {
  answer_id: string
  text: string | null
  option_index: number | null
  correct: boolean | null
  score: number
  feedback: string | null
}

export type ReviewItem = {
  question_id: string
  number: number
  text: string
  options: string[] | null
  reference_answer: string | null
  correct_option_index: number | null
  answer: AnswerView | null
}

export type ChatMessage = {
  role: "user" | "assistant"
  content: string
}

export type Certificate = {
  id: string
  user_name: string
  topic_title: string
  score: number
  issued_at: string
  preparation_id: string
}

export type TopicPass = {
  topic_id: string
  mode: RoundMode
  score: number
  answered: number
  certificate_id: string | null
}

export type MasteredTopic = {
  preparation_id: string
  topic_id: string
}

export type NextQuestion = {
  question_id: string
  number: number
  text: string
  options: string[] | null
}

export type AnswerResult = {
  answer_id: string
  correct: boolean | null
  score: number
  feedback: string | null
  reference_answer: string
  correct_option_index: number | null
  current_score: number
  answered: number
  total: number
  option_index?: number | null
  text?: string | null
}

export type AnswerInput = { text: string } | { option_index: number }
