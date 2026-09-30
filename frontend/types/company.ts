export type Company = {
  id: string
  name: string
  role: "owner" | "admin"
  interview_count: number
  created_at: string
}

export type CompanyMember = {
  email: string
  role: "owner" | "admin"
  joined: boolean
  token: string | null
  created_at: string
}

export type AdminInvite = {
  company_name: string
  email: string
  joined: boolean
}

export type Interview = {
  id: string
  generation_id: string
  set_id: string | null
  title: string | null
  mode: "open" | "choice"
  share_results: boolean
  candidate_count: number
  created_at: string
}

export type InterviewDetail = Interview & {
  topics: {
    id: string
    title: string
    subtopics: string[]
    question_count: number
    question_limit: number | null
  }[]
}

export type Candidate = {
  id: string
  email: string
  status: "invited" | "in_process" | "finished"
  progress: number
  grade: number | null
  created_at: string
}

export type InviteView = {
  interview_id: string
  title: string | null
  company: string
  email: string
  status: "invited" | "in_process" | "finished"
}

export type SessionTopic = {
  id: string
  topic_title: string
  status: "in_progress" | "finished"
  total: number
  answered: number
}

export type SessionSummary = {
  id: string
  topic_title: string
  status: "in_progress" | "finished"
  final_score: number | null
}

export type InterviewSession = {
  id: string
  topic_id: string
  topic_title: string
  interview_title: string | null
  mode: "open" | "choice"
  share_results: boolean
  status: "in_progress" | "finished"
  total: number
  answered: number
  current_score: number | null
  final_score: number | null
  started_at: string
  finished_at: string | null
}

export type SessionAnswerResult = {
  answer_id: string
  answered: number
  total: number
  correct?: boolean | null
  score?: number | null
  feedback?: string | null
  current_score?: number | null
  option_index?: number | null
}
