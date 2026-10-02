import type { components } from "@/types/api/library"

type Schemas = components["schemas"]

export type PreparationSummary = Schemas["PreparationSummary"]
export type MyPreparation = Schemas["MyPreparation"]
export type PreparationTopic = Schemas["TopicOut"]
export type PreparationDetail = Schemas["PreparationDetail"]
export type PreparationAccess = PreparationDetail["access"]
