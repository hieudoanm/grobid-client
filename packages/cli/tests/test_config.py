"""Tests for grobid.config."""

import os
from pathlib import Path

from grobid.config import (
    GROBID_CONTAINER,
    GROBID_IMAGE,
    GROBID_PORT,
    GROBID_SERVICE,
    GROBID_URL,
    HEALTH_URL,
    META_FIELDS,
    NS,
    get_data_dir,
)


def test_config_constants():
    assert GROBID_SERVICE == "processFulltextDocument"
    assert NS == {"tei": "http://www.tei-c.org/ns/1.0"}
    assert META_FIELDS == (
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
    assert GROBID_PORT == int(os.environ.get("GROBID_PORT", "8070"))
    assert GROBID_URL == f"http://localhost:{GROBID_PORT}"
    assert HEALTH_URL == f"{GROBID_URL}/api/isalive"
    assert GROBID_IMAGE == os.environ.get("GROBID_IMAGE", "grobid/grobid:0.9.1-crf")
    assert GROBID_CONTAINER == os.environ.get("GROBID_CONTAINER", "grobid-cli")


def test_get_data_dir_from_env(monkeypatch):
    monkeypatch.setenv("GROBID_DATA_DIR", "/custom/data")
    assert get_data_dir() == Path("/custom/data")


def test_get_data_dir_from_articles_env(monkeypatch):
    monkeypatch.delenv("GROBID_DATA_DIR", raising=False)
    monkeypatch.setenv("ARTICLES_DATA_DIR", "/articles/data")
    assert get_data_dir() == Path("/articles/data")


def test_get_data_dir_default(monkeypatch):
    monkeypatch.delenv("GROBID_DATA_DIR", raising=False)
    monkeypatch.delenv("ARTICLES_DATA_DIR", raising=False)
    assert get_data_dir() == Path.cwd()
