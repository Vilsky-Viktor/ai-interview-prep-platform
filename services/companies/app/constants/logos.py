# Company logos: PNG, JPEG or WebP up to this size, recognised by their first bytes. SVG isn't
# accepted: it can carry scripts.
MAX_LOGO_BYTES = 500_000
LOGO_SIGNATURES = (
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
)
WEBP_TYPE = "image/webp"
# Where the site serves a logo (through the gateway); `v` changes with every upload.
LOGO_PATH = "/api/companies/companies/{company_id}/logo?v={version}"
# A versioned logo never changes, so browsers and email clients keep it.
LOGO_CACHE = "public, max-age=31536000, immutable"
