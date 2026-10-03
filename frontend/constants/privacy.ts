import { COMPANY, type LegalSection } from "@/constants/legal"

export const PRIVACY_INTRO = `This policy explains what personal data prepza collects, why, how long we keep it, and the rights you have. prepza is run by ${COMPANY.name} (registry code ${COMPANY.registryCode}), ${COMPANY.address}.`

export const PRIVACY_SECTIONS: LegalSection[] = [
  {
    heading: "Who is responsible",
    paragraphs: [
      `For your own account, preparations and practice, ${COMPANY.name} is the controller of your data. Write to ${COMPANY.privacyEmail} with any question or request.`,
      "When a company invites you to an interview on prepza, that company decides why and how your interview results are used and is the controller of them; we process them on its behalf. You can contact the company directly, or us, and we will pass your request on.",
    ],
  },
  {
    heading: "What we collect",
    items: [
      "Account: your name, email address, profile photo and account id, from your Google sign-in.",
      "What you give us: job descriptions and goals you paste, the preparations made from them, your ratings, reports, shares, and messages to the AI tutor.",
      "Practice: your answers, scores, progress and certificates. A certificate shows your name and score to anyone with its link.",
      "Interviews: the email you were invited with, your answers, how long each answer took, and when you left the interview page or copied text during it. You are told about this before you start.",
      "Technical: error reports without your IP address or email, and short-lived server logs needed to run and secure the service.",
      "Referrals: whose referral link you or your company came through, and whether it has been rewarded.",
      "Usage statistics: steps such as signing up, a prep kit being ready, a round finished or a top-up, with counts like a score or an amount. Your account id is replaced by a code that can't be traced back to you, and no names, emails or texts are included.",
    ],
  },
  {
    heading: "Why we use it",
    items: [
      "To provide prepza: generating preparations and interviews, running practice and interviews, issuing certificates and sending the emails you ask for (contract).",
      "To keep prepza secure and working: preventing abuse, rate limits, error reports, and statistics that improve question quality (our legitimate interest).",
      "Usage statistics show which parts of prepza help people and which prices and limits work, so we can improve them (our legitimate interest).",
      "Interview results, timings and page-leave signals help the hiring company assess your answers fairly (the company's legitimate interest). People at the company make the hiring decision; prepza makes no decision about you on its own.",
    ],
  },
  {
    heading: "Who we share it with",
    paragraphs: [
      "We share data only with the service providers that run prepza for us, under agreements that protect it:",
    ],
    items: [
      "Google (Firebase Authentication): sign-in.",
      "OpenAI: writing questions and tutor replies from the text you provide. Under OpenAI's API terms, this data is not used to train their models.",
      "Resend: sending invite emails.",
      "Sentry: error reports, with emails removed.",
      "Our hosting provider, which stores the data.",
      "Paddle: payments and taxes, as the reseller.",
    ],
  },
  {
    heading: "Transfers outside the EU",
    paragraphs: [
      "Some of these providers are in the United States. Transfers are covered by the EU-US Data Privacy Framework or the European Commission's standard contractual clauses.",
    ],
  },
  {
    heading: "How long we keep it",
    items: [
      "Your account and everything in it: until you delete your account.",
      "Interview results, timings and page-leave signals: 12 months after the invitation was sent, then deleted automatically.",
      "Pasted job descriptions in our generation records: 90 days after the generation finishes. The preparation made from them stays in your account until you delete it.",
      "Error reports: up to 90 days.",
      "Usage statistics: 25 months, then deleted automatically.",
      "A one-way hash of your email after you delete your account, only so that signing up again doesn't repeat the welcome credits. It can't be turned back into your email.",
    ],
  },
  {
    heading: "Your rights",
    paragraphs: [
      'You can see, download and delete your data yourself: "Download my data" and "Delete account" are in Settings, in your account menu. You can also ask us to correct your data, to restrict or object to its use, or to move it to another service, at the address above.',
      "You can complain to the Estonian Data Protection Inspectorate (Andmekaitse Inspektsioon, www.aki.ee) or to the authority where you live.",
    ],
  },
  {
    heading: "Cookies and storage",
    paragraphs: [
      "prepza uses only what it needs to work: one cookie and the browser storage that keep you signed in, and a setting that remembers your light or dark theme. There are no advertising or analytics cookies, so there is nothing to consent to.",
    ],
  },
  {
    heading: "Children",
    paragraphs: ["prepza is not meant for anyone under 16."],
  },
  {
    heading: "Changes",
    paragraphs: [
      "We will update this page when our practices change and tell you about significant changes by email or in the app.",
    ],
  },
]
