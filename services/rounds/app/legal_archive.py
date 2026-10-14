"""Run after giving a changed legal document its new version: `python -m app.legal_archive`."""

from app.helpers.legal import archive

if __name__ == "__main__":
    archive()
