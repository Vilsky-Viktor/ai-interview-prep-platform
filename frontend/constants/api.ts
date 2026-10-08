// The public API's reference on the site, and where its requests go.
export const API_DOCS_PATH = "/api-docs"
export const API_BASE_PATH = "/api/v1"
// The longest key name and web hook address the API takes.
export const MAX_KEY_NAME = 80
export const MAX_WEBHOOK_URL = 500
// The landing page's example request: inviting a candidate, and what the API answers, each as
// its first lines and its body.
export const API_EXAMPLE = {
  request: {
    head: "POST /api/v1/interviews/{id}/candidates\nAuthorization: Bearer pz_…",
    body: '{ "email": "anna@example.com" }',
  },
  response: {
    head: "201 Created",
    body: '{ "status": "invited", "progress": 0 }',
  },
}
