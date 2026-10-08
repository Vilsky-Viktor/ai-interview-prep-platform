// The longest text each field takes, as the services accept it (the service's constant is named
// after each). The services enforce these; the fields stop typing at the same point, so nothing
// is refused on sending.

// prepza_common MAX_GOAL_LENGTH: a learner's goal or a job description.
export const MAX_GOAL_LENGTH = 10000
// generation MAX_INSTRUCTIONS_LENGTH: changes described in words during topic review.
export const MAX_INSTRUCTIONS_LENGTH = 500
// generation MAX_TOPIC_NAME_LENGTH: a topic or subtopic edited during review.
export const MAX_TOPIC_NAME_LENGTH = 50
// prepza_common MAX_TITLE_LENGTH: a kit's or an interview's title.
export const MAX_TITLE_LENGTH = 70
// companies MAX_COMPANY_NAME_LENGTH: a company's name.
export const MAX_COMPANY_NAME_LENGTH = 45
// companies MAX_DECLINE_REASON_LENGTH: why a superadmin declined a company's verification.
export const MAX_DECLINE_REASON_LENGTH = 500
// library MAX_REPORT_COMMENT_LENGTH: details of a question report.
export const MAX_REPORT_COMMENT_LENGTH = 1000
// rounds MAX_HELP_QUESTION_LENGTH: a question to the FAQ's help chat.
export const MAX_HELP_QUESTION_LENGTH = 1000
// rounds MAX_CONTACT_NAME_LENGTH and MAX_CONTACT_MESSAGE_LENGTH: the contact form.
export const MAX_CONTACT_NAME_LENGTH = 100
export const MAX_CONTACT_MESSAGE_LENGTH = 5000
// The language picker's search: it only filters the list in the browser, and names are short.
export const MAX_LANGUAGE_SEARCH_LENGTH = 50
// The longest email address there can be (RFC 5321); the services check every address.
export const MAX_EMAIL_LENGTH = 254
// companies MAX_SEARCH_LENGTH: a search through candidates' emails.
export const MAX_SEARCH_LENGTH = 254
// companies MAX_BULK_TEXT_LENGTH: a pasted or uploaded list of candidate emails.
export const MAX_BULK_TEXT_LENGTH = 50000
// prepza_common MAX_NEWS_TITLE_LENGTH and MAX_NEWS_TEXT_LENGTH: a news post.
export const MAX_NEWS_TITLE_LENGTH = 120
export const MAX_NEWS_TEXT_LENGTH = 500
