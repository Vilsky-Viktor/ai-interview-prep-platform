import type { components } from "@/types/api/billing"

type Schemas = components["schemas"]

export type Catalog = Schemas["CatalogOut"]
export type Product = Schemas["TopUpOut"]
export type Referral = Schemas["ReferralOut"]
export type AutoTopUp = Schemas["AutoTopUpOut"]
// A company's credits: available, running low, and how many candidates they pay for.
export type CompanyCredits = {
  available: number
  low: boolean
  candidates: number
}
