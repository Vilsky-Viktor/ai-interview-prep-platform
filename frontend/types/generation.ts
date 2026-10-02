import type { components } from "@/types/api/generation"

type Schemas = components["schemas"]

export type Generation = Schemas["GenerationOut"]
export type GenerationStatus = Generation["status"]
export type DraftTopic = Schemas["DraftTopic"]
/** A preparation generation that hasn't produced a preparation yet. */
export type GenerationSummary = Schemas["GenerationSummary"]
