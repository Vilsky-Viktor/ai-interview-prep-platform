import type { components } from "@/types/api/billing"

type Schemas = components["schemas"]

export type Catalog = Schemas["CatalogOut"]
export type Product = Schemas["TopUpOut"]
export type Referral = Schemas["ReferralOut"]
export type AutoTopUp = Schemas["AutoTopUpOut"]
export type CompanyCredits = { available: number; low: boolean }
