import type { components } from "@/types/api/library"

type Schemas = components["schemas"]

export type Share = Schemas["ShareOut"]
export type ShareInvite = Schemas["ShareInviteOut"]
