import { COMPANY, type LegalSection } from "@/constants/legal"

export const TERMS_INTRO = `These terms apply when you use prepza, a service of ${COMPANY.name} (registry code ${COMPANY.registryCode}), ${COMPANY.address}. By signing in, you agree to them.`

export const TERMS_SECTIONS: LegalSection[] = [
  {
    heading: "Your account",
    paragraphs: [
      "You sign in with Google and are responsible for what happens in your account. You can delete it at any time from your account menu.",
    ],
  },
  {
    heading: "What prepza is, and isn't",
    items: [
      "Questions, answers and tutor replies are written by AI and can be wrong. We check and improve them continuously, but don't rely on them as professional advice.",
      "A prepza certificate shows that you answered every question of a topic on prepza with the required score. It is not an accredited qualification.",
    ],
  },
  {
    heading: "Your content",
    paragraphs: [
      "You keep the rights to what you paste and create. You let us store and process it to run prepza, including sending it to our AI provider. When you make a preparation public, anyone can see and practise with it, and its proven questions may help write new preparations.",
      "Don't paste anything you aren't allowed to share, such as someone else's confidential information.",
    ],
  },
  {
    heading: "Fair use",
    items: [
      "Don't use prepza to send unwanted email, to scrape it, or to overload or attack it.",
      "Don't try to get around limits, security or another user's access.",
      "In an interview, answer on your own and follow the interview's rules; the company sees how long each answer took and when you left the page.",
    ],
  },
  {
    heading: "Companies",
    paragraphs: [
      "A company using prepza for interviews is responsible for inviting candidates lawfully, for telling them how their results are used, and for its hiring decisions. We process candidates' data on the company's behalf; ask us for our data processing terms.",
    ],
  },
  {
    heading: "Prices",
    paragraphs: [
      "prepza is free for now. Paid plans, when they come, are shown with their prices before you buy and are sold through Paddle, who acts as the reseller and handles payments and taxes.",
    ],
  },
  {
    heading: "Availability and changes",
    paragraphs: [
      "We work to keep prepza available and safe but can't promise it will always be. We may change or stop features, and may suspend accounts that break these terms. We will tell you about significant changes to these terms before they apply.",
    ],
  },
  {
    heading: "Liability",
    paragraphs: [
      "prepza is provided as it is. As far as the law allows, we are not liable for indirect losses, and our total liability is limited to what you paid us in the last 12 months, or 100 euros if you paid nothing. Nothing here limits rights you have as a consumer under the law of your country.",
    ],
  },
  {
    heading: "Law",
    paragraphs: [
      `Estonian law applies, without taking away the mandatory protections of the country you live in. Questions about these terms: ${COMPANY.privacyEmail}.`,
    ],
  },
]
