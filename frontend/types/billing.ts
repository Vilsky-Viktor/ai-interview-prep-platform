import type { components } from "@/types/api/billing"

type Schemas = components["schemas"]

export type Catalog = Schemas["CatalogOut"]
export type Product = Schemas["ProductOut"]
export type Plan = Schemas["PlanOut"]
export type CompanyCredits = { candidate_credits: number }
