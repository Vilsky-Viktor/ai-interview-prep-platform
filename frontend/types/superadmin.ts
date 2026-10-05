import type { components } from "@/types/api/library"

type Schemas = components["schemas"]

export type TemplateSummary = Schemas["TemplateSummary"]
export type Template = Schemas["TemplateOut"]
export type TemplateFilters = Schemas["TemplateFiltersOut"]
export type FlaggedQuestion = Schemas["FlaggedQuestionOut"]
export type ReplacedQuestion = Schemas["ReplacedQuestionOut"]
