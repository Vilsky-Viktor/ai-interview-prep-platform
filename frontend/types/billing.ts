import type { components } from "@/types/api/billing"

type Schemas = components["schemas"]

export type Catalog = Schemas["CatalogOut"]
export type Product = Schemas["TopUpOut"]
export type Balance = Schemas["BalanceOut"]
export type Entry = Schemas["EntryOut"]
export type Quote = Schemas["QuoteOut"]
export type CompanyCredits = { available: number; low: boolean }
