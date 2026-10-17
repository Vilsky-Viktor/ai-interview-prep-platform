// The home page's "create an interview" demos: what their three panels show. Display only.

// The job description typed into the box.
export const DEMO_DESCRIPTION =
  "Senior Python developer for our payments team: async code, FastAPI services and PostgreSQL."

// The topics proposed for it, one for each skill it names; the one given a new subtopic by
// hand; the change asked of the AI and the topic it adds, which the description doesn't name.
export const DEMO_TOPICS = [
  { name: "Python and async code", subtopics: ["asyncio", "Testing"] },
  { name: "FastAPI services", subtopics: ["REST design", "Auth"] },
  { name: "PostgreSQL", subtopics: ["Indexes", "Transactions"] },
]

export const DEMO_EDITED = "PostgreSQL"
export const DEMO_ADDED_SUBTOPIC = "Migrations"
export const DEMO_CHANGE = "Add a topic on mentoring"
export const DEMO_NEW_TOPIC = {
  name: "Mentoring",
  subtopics: ["Code reviews", "Feedback"],
}

// The search typed; the templates listed (those whose title has the search stay); the one
// used, and its topics on the interview it creates.
export const DEMO_SEARCH = "marketing"

export const DEMO_TEMPLATES = [
  { title: "Digital Marketing Manager", topics: 4, questions: 360 },
  { title: "Senior Accountant", topics: 5, questions: 450 },
  { title: "Content Marketing Specialist", topics: 5, questions: 450 },
  { title: "Customer Support Agent", topics: 4, questions: 360 },
]

export const DEMO_PICKED = DEMO_TEMPLATES[0]

export const DEMO_TEMPLATE_TOPICS = [
  "SEO and content",
  "Paid ads and budgets",
  "Analytics and attribution",
  "Email and lifecycle",
]
