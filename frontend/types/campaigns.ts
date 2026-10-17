import type { components } from "@/types/api/notifications"

type Schemas = components["schemas"]

export type Campaign = Schemas["CampaignOut"]
export type CampaignRow = Schemas["CampaignRowOut"]
export type CampaignTexts = Schemas["CampaignTexts"]
export type CampaignPreview = Schemas["PreviewOut"]
export type LegalChange = Schemas["LegalChangeOut"]
