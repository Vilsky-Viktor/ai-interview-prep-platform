// The company behind prepza, as named in the privacy policy and terms.
// TODO before launch: set the privacy email, and have a lawyer review both documents.
export const COMPANY = {
  name: "Arcolabs OÜ",
  registryCode: "17587452",
  address: "Sepapaja tn 6, 15551 Tallinn, Harju maakond, Estonia",
  privacyEmail: "[privacy@prepza.ai]",
}

// When the privacy policy and terms last changed.
export const LEGAL_UPDATED = "2026-10-03"

export type LegalSection = {
  heading: string
  paragraphs?: string[]
  items?: string[]
}
