import type { components } from "@/types/api/generation"

type Schemas = components["schemas"]

export type Generation = Schemas["GenerationOut"]
export type GenerationStatus = Generation["status"]
export type DraftTopic = Schemas["DraftTopic"]
/** A template's latest question addition and the numbers a superadmin's addition may ask for. */
export type Addition = Schemas["AdditionOut"]
