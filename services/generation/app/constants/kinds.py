from enum import StrEnum


class GenerationKind(StrEnum):
    INTERVIEW = "interview"
    # A superadmin's template (docs/company-plan.md, Phase 2), saved to library without a company.
    TEMPLATE = "template"
