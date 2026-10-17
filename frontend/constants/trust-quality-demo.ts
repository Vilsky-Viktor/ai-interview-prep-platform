// The home page's "trust, quality and compliance" section: the quality loop's steps and the
// cards under it. Display only.

// The loop's steps, in order, by their text's key; after the last, back to the first.
export const QUALITY_STEPS = [
  "generated",
  "checked",
  "answered",
  "flagged",
  "rewritten",
] as const

export type QualityStep = (typeof QUALITY_STEPS)[number]

// Where each step sits on the ring, in a three-column grid on phones and a five-column one from
// laptops up: the first at the top, then clockwise. From laptops up the side steps overlap the
// rows above and below, so the top step sits closer to the bottom ones,
// and the two bottom steps move toward each other.
export const QUALITY_PLACES: Record<QualityStep, string> = {
  generated: "col-start-2 row-start-1 lg:col-start-3",
  checked: "col-start-3 row-start-2 lg:col-start-5 lg:-my-10",
  answered: "col-start-3 row-start-3 lg:relative lg:-left-14 lg:col-start-4",
  flagged: "col-start-1 row-start-3 lg:relative lg:left-14 lg:col-start-2",
  rewritten: "col-start-1 row-start-2 lg:-my-10",
}

// How long the question rests on a step before it moves on, in milliseconds.
export const QUALITY_PAUSE_MS = 900

// The cards under the loop, by their text's key.
export const TRUST_CARDS = ["person", "fair", "laws", "log"] as const

export type TrustCard = (typeof TRUST_CARDS)[number]

// The question travelling the loop, this many times the usual traveller's size.
export const QUESTION_SIZE = 1.9
