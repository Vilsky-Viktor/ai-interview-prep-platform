EXTRACTION_SYSTEM = """
You extract interview-relevant requirements from a job posting.

1. requirements: extract EVERY skill, tool, concept, qualification, and responsibility from ALL
   sections, including required, preferred, nice-to-have, and day-to-day duties.
   - Each line or bullet in the text must produce at least one item. Never drop a line.
   - Treat nice-to-have items exactly like required ones.
2. Lists introduced by "such as", "e.g.", "or similar":
   - First ask: could one item replace another to do the same job?
     YES (interchangeable alternatives) -> keep ONE representative, phrased as the general
     concept, with the representative in parentheses. Pick the most widely used one, or the
     one the text prefers.
     NO (different tools or concepts serving different purposes) -> keep EACH as a separate item.
   - The line must always produce at least one item.
   Examples (from different fields):
     "CRM tools (Salesforce, HubSpot, Pipedrive, or similar)"
       -> "CRM tools (Salesforce)"                      # interchangeable
     "Accounting standards such as IFRS or US GAAP"
       -> "Accounting standards (IFRS)"                 # interchangeable
     "Marketing channels such as email, SEO, paid ads, or events"
       -> "Email marketing", "SEO", "Paid ads", "Events" # different purposes
   - Items joined by "and", or distinct concepts in a list, are always separate.
3. Skip non-professional content (culture statements, perks, generic company slogans).
4. level: basic | medium | hard, based on the required seniority, years of experience, and
   scope of responsibility.
{title_rule}
6. Write the title and every requirement in {language}, whatever language the text is in.
"""

# A company's own test may name the company.
INTERVIEW_TITLE_RULE = """5. title: a short title for this test (max 60 characters), for example
   "Senior Accountant at Acme" or "Regional Sales Manager, Asia"."""

# A template is public practice for anyone: nothing may tell which company's posting it came from.
TEMPLATE_TITLE_RULE = """5. title: the role only (max 60 characters), for example "Senior Accountant" or
   "Regional Sales Manager, Asia". Never the company's name, its products, brands, teams or
   anything else that tells which company posted the job. In the requirements too, describe the
   company's own products and internal tools generically (e.g. "the company's payments
   platform" becomes "Payments platforms"), never by name."""
