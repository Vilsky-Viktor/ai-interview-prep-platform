variable "project_id" {
  description = "The Google Cloud project, for example prepza-prod. Firebase uses the same project."
  type        = string
}

variable "region" {
  description = "Everything runs here: the EU, for data residency; the global load balancer keeps US latency low."
  type        = string
  default     = "europe-west1"
}

variable "domain" {
  description = "The site's domain; its A record points at the load balancer's address."
  type        = string
  default     = "prepza.ai"
}

variable "image_tag" {
  description = "The images' tag on the first apply; afterwards the deploy pipeline sets them."
  type        = string
  default     = "first"
}

variable "github_repository" {
  description = "The repository whose main branch may deploy (owner/name)."
  type        = string
  default     = "Vilsky-Viktor/ai-interview-prep-platform"
}

variable "db_tier" {
  description = "Cloud SQL machine type; db-g1-small to start, a dedicated one (db-custom-2-7680) as it grows."
  type        = string
  default     = "db-g1-small"
}

variable "db_high_availability" {
  description = "A standby in another zone that takes over on failure; doubles the database cost."
  type        = bool
  default     = false
}

variable "daily_generation_limit" {
  description = "New generations a day for everyone together: a ceiling on LLM spending (about $1.00 a test); 0 turns it off."
  type        = number
  default     = 200
}

variable "mail_from" {
  description = "Sender of every email, on a domain verified in Resend."
  type        = string
  default     = "prepza. <no-reply@prepza.ai>"
}

variable "sentry_dsn" {
  description = "Backend Sentry DSN; empty sends nothing. Not secret: it only allows sending events."
  type        = string
  default     = ""
}

variable "paddle_environment" {
  description = "sandbox or production."
  type        = string
  default     = "sandbox"
}

variable "paddle_client_token" {
  description = "Paddle.js's client-side token; public by design."
  type        = string
  default     = ""
}

variable "paddle_prices" {
  description = "Paddle price id of each product (services/billing/app/constants/products.py)."
  type        = map(string)
  default     = {}
}

variable "alert_email" {
  description = "Where outage and budget alerts go."
  type        = string
}

variable "billing_account" {
  description = "The billing account the project uses (XXXXXX-XXXXXX-XXXXXX), for the monthly budget."
  type        = string
}

variable "monthly_budget" {
  description = "Monthly Google Cloud budget, in the billing account's currency; alerts only, nothing stops."
  type        = number
  default     = 300
}

variable "superadmin_emails" {
  description = "Superadmins, prepza's own team (templates, the question bank): verified Google emails."
  type        = list(string)
  default     = []
}

variable "github_client_id" {
  description = "Client id of the GitHub OAuth app for signing in; empty leaves GitHub sign-in off."
  type        = string
  default     = ""
}

variable "github_client_secret" {
  description = "Client secret of the GitHub OAuth app (kept in the Terraform state)."
  type        = string
  default     = ""
  sensitive   = true
}

variable "linkedin_client_id" {
  description = "Client id of the LinkedIn app (Sign In with LinkedIn using OpenID Connect); empty leaves it off."
  type        = string
  default     = ""
}

variable "linkedin_client_secret" {
  description = "Client secret of the LinkedIn app (kept in the Terraform state)."
  type        = string
  default     = ""
  sensitive   = true
}
