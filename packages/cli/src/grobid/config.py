"""Configuration."""

import os
from pathlib import Path

NS = {"tei": "http://www.tei-c.org/ns/1.0"}
META_FIELDS = (
    "title",
    "authors",
    "year",
    "journal",
    "volume",
    "issue",
    "pages",
    "doi",
    "doi_link",
)

GROBID_SERVICE = "processFulltextDocument"
GROBID_CONSOLIDATE_HEADER = True
GROBID_PORT = int(os.environ.get("GROBID_PORT", "8070"))
GROBID_URL = f"http://localhost:{GROBID_PORT}"
HEALTH_URL = f"{GROBID_URL}/api/isalive"
GROBID_IMAGE = os.environ.get("GROBID_IMAGE", "grobid/grobid:0.9.1-crf")
GROBID_CONTAINER = os.environ.get("GROBID_CONTAINER", "grobid-cli")


def get_data_dir() -> Path:
    if data_dir := os.environ.get("GROBID_DATA_DIR") or os.environ.get(
        "ARTICLES_DATA_DIR"
    ):
        return Path(data_dir)
    return Path.cwd()
