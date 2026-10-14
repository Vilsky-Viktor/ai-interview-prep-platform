// The developer docs' tabs, in order: the API, its web hooks and the SDK (each with its part of
// the API's description, lib/openapi.ts descriptionTabs), and the objects they return. The first
// is the page's own address.
export const DOC_TABS = ["api", "webhooks", "sdk", "objects"] as const

export type DocTab = (typeof DOC_TABS)[number]
