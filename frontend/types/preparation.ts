export type PreparationSummary = {
  id: string
  title: string
  level: string
  visibility: "private" | "public"
  created_at: string
  topic_count: number
  rating_avg: number | null
  rating_count: number
  join_count: number
}

export type PreparationTopic = {
  id: string
  title: string
  subtopics: string[]
  question_count: number
  question_limit: number | null
}

export type PreparationAccess = "owner" | "joined" | "public"

export type PreparationDetail = PreparationSummary & {
  requirements: string[]
  topics: PreparationTopic[]
  access: PreparationAccess
  my_rating: number | null
}
