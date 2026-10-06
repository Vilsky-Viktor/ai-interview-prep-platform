# The largest PDF report a member can email: a one-page report is about 250 KB. It travels inside
# the event (Pub/Sub carries up to 10 MB), base64 adding a third.
MAX_REPORT_BYTES = 1_000_000
# What every PDF file starts with.
PDF_SIGNATURE = b"%PDF-"
# Why a report email is refused.
NOT_A_PDF = "The report isn't a PDF"
NO_FINISHED_CANDIDATES = "A report can be emailed once a candidate has finished this interview."
TOO_MANY_REPORT_EMAILS = "Your company has emailed its daily limit of reports. Try again tomorrow."
