# A private network for the services' outgoing traffic. Calls between services go through it, so
# they arrive as internal although the services only take outside traffic from the load
# balancer; everything else reaches the internet through Cloud NAT.
resource "google_compute_network" "main" {
  name                    = "prepza"
  auto_create_subnetworks = false

  depends_on = [google_project_service.apis]
}

resource "google_compute_subnetwork" "run" {
  name                     = "prepza-run"
  region                   = var.region
  network                  = google_compute_network.main.id
  ip_cidr_range            = "10.8.0.0/24"
  private_ip_google_access = true
}

resource "google_compute_router" "main" {
  name    = "prepza"
  region  = var.region
  network = google_compute_network.main.id
}

# Each instance gets NAT ports as it needs them: 64 at first, up to 4096. A fixed 64 would cap an
# instance at about 64 connections to one address (Upstash, OpenAI, Resend).
resource "google_compute_router_nat" "main" {
  name                                = "prepza"
  router                              = google_compute_router.main.name
  region                              = var.region
  nat_ip_allocate_option              = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat  = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  enable_dynamic_port_allocation      = true
  enable_endpoint_independent_mapping = false
  min_ports_per_vm                    = 64
  max_ports_per_vm                    = 4096
}
