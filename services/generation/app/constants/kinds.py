from enum import StrEnum


class GenerationKind(StrEnum):
    INTERVIEW = "interview"
    # A superadmin's template (docs/features/admin-zone.md, Templates), saved to library without a company.
    TEMPLATE = "template"
