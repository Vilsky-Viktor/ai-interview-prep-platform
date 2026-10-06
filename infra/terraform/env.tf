locals {
  # Every service gets these.
  common_env = {
    GOOGLE_CLOUD_PROJECT    = var.project_id
    FIREBASE_PROJECT_ID     = var.project_id
    SENTRY_DSN              = var.sentry_dsn
    SUPERADMIN_EMAILS       = join(",", var.superadmin_emails)
    SENTRY_ENVIRONMENT      = "production"
    INVOKER_SERVICE_ACCOUNT = google_service_account.invoker.email
    LIBRARY_URL             = local.run_url["library"]
    GENERATION_URL          = local.run_url["generation"]
    ROUNDS_URL              = local.run_url["rounds"]
    COMPANIES_URL           = local.run_url["companies"]
    BILLING_URL             = local.run_url["billing"]
    NOTIFICATIONS_URL       = local.run_url["notifications"]
  }

  # And each service its own; INVOKER_AUDIENCE is the service's address, which Google's signed
  # tokens are issued for.
  service_env = {
    frontend = {
      API_URL  = "https://${var.domain}"
      SITE_URL = "https://${var.domain}"
    }
    library = {
      INVOKER_AUDIENCE = local.run_url["library"]
    }
    generation = {
      INVOKER_AUDIENCE       = local.run_url["generation"]
      DAILY_GENERATION_LIMIT = tostring(var.daily_generation_limit)
      WORKER_URL             = local.run_url["generation-worker"]
      TASKS_QUEUE            = google_cloud_tasks_queue.generation.id
    }
    generation-worker = {
      INVOKER_AUDIENCE = local.run_url["generation-worker"]
      WORKER_URL       = local.run_url["generation-worker"]
      TASKS_QUEUE      = google_cloud_tasks_queue.generation.id
    }
    rounds = {
      INVOKER_AUDIENCE = local.run_url["rounds"]
    }
    companies = {
      INVOKER_AUDIENCE = local.run_url["companies"]
    }
    billing = merge(
      {
        INVOKER_AUDIENCE    = local.run_url["billing"]
        PADDLE_ENVIRONMENT  = var.paddle_environment
        PADDLE_CLIENT_TOKEN = var.paddle_client_token
      },
      { for key, price in var.paddle_prices : "PADDLE_PRICE_${upper(key)}" => price },
    )
    notifications = {
      INVOKER_AUDIENCE = local.run_url["notifications"]
      SITE_URL         = "https://${var.domain}"
      MAIL_FROM        = var.mail_from
    }
    notifications-stream = {
      INVOKER_AUDIENCE = local.run_url["notifications-stream"]
      SITE_URL         = "https://${var.domain}"
    }
  }
}
