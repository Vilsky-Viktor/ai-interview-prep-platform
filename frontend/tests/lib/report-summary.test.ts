import { describe, expect, it } from "vitest"

import { candidateLabel, reportSummary } from "@/lib/report-summary"
import type { CandidateReportData } from "@/types/company"

const t = (key: string, values?: Record<string, string | number>) =>
  values ? `${key}:${JSON.stringify(values)}` : key

const report: CandidateReportData = {
  company: "Acme",
  logoUrl: null,
  verifiedDomain: null,
  title: "Backend",
  email: "ann@example.com",
  name: "Ann Lee",
  grade: 80,
  passed: true,
  passMark: 70,
  sections: [],
}

describe("candidateLabel", () => {
  it("names a candidate with their email once the name is known", () => {
    expect(candidateLabel(report)).toBe("Ann Lee (ann@example.com)")
  })

  it("is the email while the name is unknown", () => {
    expect(candidateLabel({ email: "ann@example.com", name: null })).toBe(
      "ann@example.com"
    )
  })
})

describe("reportSummary", () => {
  it("names the candidate in the shared summary", () => {
    expect(reportSummary(report, t).split("\n")[1]).toMatch(
      /^Ann Lee \(ann@example\.com\): 80%, /
    )
  })
})
