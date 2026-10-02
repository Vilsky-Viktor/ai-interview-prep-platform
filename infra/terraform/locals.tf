locals {
  registry = "${var.region}-docker.pkg.dev/${var.project_id}/prepza"

  # Cloud Run's deterministic address of a service, known before it exists, so services can
  # point at each other without a cycle.
  run_url = { for name in keys(local.services) : name => "https://${name}-${data.google_project.this.number}.${var.region}.run.app" }

  # Every service. `public` ones are reached through the load balancer at /api/<path>/ (or / for
  # the frontend); the others only by Google (Cloud Tasks, Scheduler, Pub/Sub) as the invoker.
  # `connections` is what one instance may open to Postgres (a pool of 5 plus 5 extra; the worker
  # 4 more for LangGraph), and `max` instances keep their total within the database's budget
  # (see database.tf). Each instance takes 80 requests at once.
  services = {
    frontend          = { image = "frontend", public = true, path = null, port = 3000, min = 1, max = 10, connections = 0, cpu = "1", memory = "1Gi", timeout = 60, concurrency = 80, database = null, command = null }
    library           = { image = "library", public = true, path = "library", port = 8000, min = 0, max = 4, connections = 10, cpu = "1", memory = "512Mi", timeout = 150, concurrency = 80, database = "library", command = null }
    generation        = { image = "generation", public = true, path = "generate", port = 8000, min = 0, max = 2, connections = 10, cpu = "1", memory = "1Gi", timeout = 150, concurrency = 80, database = "generation", command = null }
    rounds            = { image = "rounds", public = true, path = "rounds", port = 8000, min = 1, max = 4, connections = 10, cpu = "1", memory = "512Mi", timeout = 60, concurrency = 80, database = "rounds", command = null }
    companies         = { image = "companies", public = true, path = "companies", port = 8000, min = 0, max = 2, connections = 10, cpu = "1", memory = "512Mi", timeout = 150, concurrency = 80, database = "companies", command = null }
    billing           = { image = "billing", public = true, path = "billing", port = 8000, min = 0, max = 1, connections = 10, cpu = "1", memory = "512Mi", timeout = 60, concurrency = 80, database = "billing", command = null }
    notifications     = { image = "notifications", public = true, path = "notifications", port = 8000, min = 0, max = 5, connections = 0, cpu = "1", memory = "512Mi", timeout = 60, concurrency = 40, database = null, command = null }
    generation-worker = { image = "generation", public = false, path = null, port = 8000, min = 0, max = 3, connections = 14, cpu = "1", memory = "2Gi", timeout = 1800, concurrency = 8, database = "generation", command = ["uv", "run", "--no-sync", "uvicorn", "app.worker_main:app", "--host", "0.0.0.0", "--port", "8000"] }
  }

  databases = ["library", "generation", "rounds", "companies", "billing"]

  # Which services each one calls; it gets their keys, to sign tokens for them.
  calls = {
    frontend          = []
    library           = ["rounds", "generation", "companies", "billing"]
    generation        = ["library", "billing"]
    generation-worker = ["library", "billing"]
    rounds            = ["library"]
    companies         = ["generation", "library", "rounds", "billing"]
    billing           = []
    notifications     = ["companies", "library"]
  }

  # Each service's own key checks calls to it. The worker shares generation's settings, so it
  # gets generation's key too, though only Google calls it.
  own_key = {
    library           = "library"
    generation        = "generation"
    generation-worker = "generation"
    rounds            = "rounds"
    companies         = "companies"
    billing           = "billing"
  }

  # Secrets each service reads (Secret Manager name => environment variable).
  base_secrets = {
    frontend          = {}
    library           = { redis-url = "REDIS_URL" }
    generation        = { redis-url = "REDIS_URL", openai-api-key = "OPENAI_API_KEY" }
    generation-worker = { redis-url = "REDIS_URL", openai-api-key = "OPENAI_API_KEY" }
    rounds            = { redis-url = "REDIS_URL", openai-api-key = "OPENAI_API_KEY" }
    companies         = { redis-url = "REDIS_URL" }
    billing           = { paddle-webhook-secret = "PADDLE_WEBHOOK_SECRET" }
    notifications     = { resend-api-key = "RESEND_API_KEY", resend-webhook-secret = "RESEND_WEBHOOK_SECRET" }
  }

  secrets = {
    for name, base in local.base_secrets : name => merge(
      base,
      { for callee in local.calls[name] : "service-secret-${callee}" => "${upper(callee)}_SERVICE_SECRET" },
      contains(keys(local.own_key), name) ? { "service-secret-${local.own_key[name]}" = "SERVICE_SECRET" } : {},
    )
  }
}
