# Whether a public kit's title names a company; public titles can't.
TITLE_COMPANY_PROMPT = """Does the title of a practice kit below name a company or organization itself?

That means a company named as the employer, the place of an interview, or the subject of the kit,
for example "Accountant at Acme", "Google interview prep", "Bank of America analyst" or
"Amazon leadership principles".

Products, tools, platforms and technologies are fine even when a company makes them, for example
AWS, Salesforce, Google Ads, Excel, SAP, Figma, Python or PostgreSQL. So are job titles, skills,
subjects and places.

The title can be in any language.

Title: {title}
"""
