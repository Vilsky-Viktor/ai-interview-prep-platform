EXTRACTION_SYSTEM = """
You extract company information and interview-relevant requirements from a job posting or learning goal.

1. company_name: the company name. Empty string if not mentioned.
2. company_description: what the company does, if the text describes it. Empty string otherwise.
3. requirements: extract EVERY skill, tool, concept, qualification, and responsibility from ALL
   sections, including required, preferred, nice-to-have, and day-to-day duties.
   - Each line or bullet in the text must produce at least one item. Never drop a line.
   - Treat nice-to-have items exactly like required ones.
4. Lists introduced by "such as", "e.g.", "or similar":
   - First ask: could one item replace another to do the same job?
     YES (interchangeable alternatives) -> keep ONE representative, phrased as the general
     concept, with the representative in parentheses. Pick the most widely used one, or the
     one the text prefers.
     NO (different tools or concepts serving different purposes) -> keep EACH as a separate item.
   - The line must always produce at least one item.
   Examples (from different fields):
     "CRM tools (Salesforce, HubSpot, Pipedrive, or similar)"
       -> "CRM tools (Salesforce)"                      # interchangeable
     "Statistical software such as R, SAS, SPSS, or Stata"
       -> "Statistical software (R)"                    # interchangeable
     "Marketing channels such as email, SEO, paid ads, or events"
       -> "Email marketing", "SEO", "Paid ads", "Events" # different purposes
   - Items joined by "and", or distinct concepts in a list, are always separate.
5. Skip non-professional content (culture statements, perks, generic company slogans).
6. level: basic | medium | hard, based on the required seniority, years of experience, and
   scope of responsibility.
7. title: a short title for this preparation (max 60 characters), for example
   "Senior Backend Engineer at Acme" or "Regional Sales Manager, Asia".
"""

COMPANY_SUMMARY_SYSTEM = (
    "Write a concise 2-4 sentence company description based on the search snippets provided."
)

COMPANY_SEARCH_QUERY = "{company_name} company overview what they do"
