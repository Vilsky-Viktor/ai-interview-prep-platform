# One global address and HTTPS certificate for the domain. Google's edge ends connections close
# to each user and carries requests to the region on its own network.
resource "google_compute_global_address" "site" {
  name       = "prepza"
  depends_on = [google_project_service.apis]
}

resource "google_compute_managed_ssl_certificate" "site" {
  name = "prepza"

  managed {
    domains = [var.domain]
  }
}

locals {
  public_services = { for name, service in local.services : name => service if service.public }
}

resource "google_compute_region_network_endpoint_group" "service" {
  for_each              = local.public_services
  name                  = each.key
  region                = var.region
  network_endpoint_type = "SERVERLESS"

  cloud_run {
    service = google_cloud_run_v2_service.service[each.key].name
  }
}

# Blocks service-to-service routes at the edge, as the nginx gateway does locally; the services
# check those callers' tokens as well.
resource "google_compute_security_policy" "edge" {
  name = "prepza-edge"

  rule {
    action      = "deny(404)"
    priority    = 1000
    description = "No /internal routes from the internet"

    match {
      expr {
        expression = "request.path.matches('^/api/[^/]+/internal/')"
      }
    }
  }

  # The FAQ page's help chat is open to visitors; each IP gets 20 questions per 10 minutes, so
  # one visitor can't run up its model costs. The service also caps accounts and the daily total.
  rule {
    action      = "throttle"
    priority    = 1100
    description = "Help chat questions per visitor"

    match {
      expr {
        expression = "request.path == '/api/rounds/help/chat'"
      }
    }

    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      enforce_on_key = "IP"

      rate_limit_threshold {
        count        = 20
        interval_sec = 600
      }
    }
  }

  rule {
    action   = "allow"
    priority = 2147483647

    match {
      versioned_expr = "SRC_IPS_V1"

      config {
        src_ip_ranges = ["*"]
      }
    }
  }
}

resource "google_compute_backend_service" "service" {
  for_each              = local.public_services
  name                  = each.key
  load_balancing_scheme = "EXTERNAL_MANAGED"
  protocol              = "HTTPS"
  security_policy       = google_compute_security_policy.edge.id
  # The frontend's static files (scripts, styles, fonts) are cached at Google's edge.
  enable_cdn = each.key == "frontend"

  dynamic "cdn_policy" {
    for_each = each.key == "frontend" ? [1] : []

    content {
      cache_mode = "USE_ORIGIN_HEADERS"
    }
  }

  backend {
    group = google_compute_region_network_endpoint_group.service[each.key].id
  }
}

# /api/<path>/... goes to that service without the prefix, as the nginx gateway does locally;
# everything else to the frontend.
resource "google_compute_url_map" "site" {
  name            = "prepza"
  default_service = google_compute_backend_service.service["frontend"].id

  host_rule {
    hosts        = ["*"]
    path_matcher = "routes"
  }

  path_matcher {
    name            = "routes"
    default_service = google_compute_backend_service.service["frontend"].id

    dynamic "route_rules" {
      for_each = { for name, service in local.public_services : name => service if service.path != null }

      content {
        priority = index(keys(local.public_services), route_rules.key) + 1
        service  = google_compute_backend_service.service[route_rules.key].id

        match_rules {
          prefix_match = "/api/${route_rules.value.path}/"
        }

        route_action {
          url_rewrite {
            path_prefix_rewrite = "/"
          }
        }
      }
    }
  }
}

resource "google_compute_target_https_proxy" "site" {
  name             = "prepza"
  url_map          = google_compute_url_map.site.id
  ssl_certificates = [google_compute_managed_ssl_certificate.site.id]
}

resource "google_compute_global_forwarding_rule" "https" {
  name                  = "prepza-https"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  ip_address            = google_compute_global_address.site.id
  port_range            = "443"
  target                = google_compute_target_https_proxy.site.id
}

# Plain HTTP redirects to HTTPS.
resource "google_compute_url_map" "redirect" {
  name = "prepza-redirect"

  default_url_redirect {
    https_redirect         = true
    strip_query            = false
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
  }
}

resource "google_compute_target_http_proxy" "redirect" {
  name    = "prepza-redirect"
  url_map = google_compute_url_map.redirect.id
}

resource "google_compute_global_forwarding_rule" "http" {
  name                  = "prepza-http"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  ip_address            = google_compute_global_address.site.id
  port_range            = "80"
  target                = google_compute_target_http_proxy.redirect.id
}
