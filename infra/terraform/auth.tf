# Ways to sign in besides Google (which Firebase has on by default): GitHub, and LinkedIn through
# OpenID Connect. Each is created only once its client id is set, from the apps you register
# (see README.md). LinkedIn needs the project upgraded to Identity Platform first. One account
# per email stays Firebase's default, so the frontend links a new way to an existing account.
resource "google_identity_platform_default_supported_idp_config" "github" {
  count         = var.github_client_id == "" ? 0 : 1
  project       = var.project_id
  idp_id        = "github.com"
  client_id     = var.github_client_id
  client_secret = var.github_client_secret
  enabled       = true

  depends_on = [google_project_service.apis]
}

resource "google_identity_platform_oauth_idp_config" "linkedin" {
  count         = var.linkedin_client_id == "" ? 0 : 1
  project       = var.project_id
  name          = "oidc.linkedin"
  display_name  = "LinkedIn"
  issuer        = "https://www.linkedin.com/oauth"
  client_id     = var.linkedin_client_id
  client_secret = var.linkedin_client_secret
  enabled       = true

  # LinkedIn signs in with the authorization code flow, which needs the client secret.
  response_type {
    code     = true
    id_token = false
  }

  depends_on = [google_project_service.apis]
}
