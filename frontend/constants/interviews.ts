// The question's countdown turns red for its last seconds.
export const COUNTDOWN_WARNING_SECONDS = 10

// How an interview's candidates can be listed; the first is the default, as in the API.
export const CANDIDATE_SORTS = ["grade", "date"] as const

export type CandidateSort = (typeof CANDIDATE_SORTS)[number]
