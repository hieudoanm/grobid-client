"""Tests for grobid.paths."""

from pathlib import Path

from grobid.paths import md_path, pdfs, resolve_paths, tei_path


def test_resolve_paths():
    from grobid.config import get_data_dir

    base = get_data_dir()
    pdf_dir, tei_dir, md_dir = resolve_paths()
    assert pdf_dir == base / "pdf"
    assert tei_dir == base / "tei"
    assert md_dir == base / "md"


def test_tei_path():
    pdf = Path("/test/paper.pdf")
    # Need to set TEI_DIR first
    import grobid.paths as p

    original_tei_dir = p.TEI_DIR
    p.TEI_DIR = Path("/test/tei")
    try:
        result = tei_path(pdf)
        assert result == Path("/test/tei/paper.tei.xml")
    finally:
        p.TEI_DIR = original_tei_dir


def test_md_path():
    import grobid.paths as p

    original_md_dir = p.MD_DIR
    p.MD_DIR = Path("/test/md")
    try:
        result = md_path(Path("/test/tei/paper.tei.xml"))
        assert result == Path("/test/md/paper.md")
    finally:
        p.MD_DIR = original_md_dir


def test_pdfs_empty(tmp_path, monkeypatch):
    import grobid.paths as p

    original_pdf_dir = p.PDF_DIR
    p.PDF_DIR = tmp_path / "pdf"
    try:
        assert pdfs() == []
    finally:
        p.PDF_DIR = original_pdf_dir


def test_pdfs_with_files(tmp_path, monkeypatch):
    import grobid.paths as p

    original_pdf_dir = p.PDF_DIR
    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir()
    (pdf_dir / "a.pdf").write_text("content")
    (pdf_dir / "b.pdf").write_text("content")
    p.PDF_DIR = pdf_dir
    try:
        result = pdfs()
        assert len(result) == 2
        assert result[0].name == "a.pdf"
        assert result[1].name == "b.pdf"
    finally:
        p.PDF_DIR = original_pdf_dir


def test_pdfs_sorted(tmp_path, monkeypatch):
    import grobid.paths as p

    original_pdf_dir = p.PDF_DIR
    pdf_dir = tmp_path / "pdf"
    pdf_dir.mkdir()
    (pdf_dir / "z.pdf").write_text("content")
    (pdf_dir / "a.pdf").write_text("content")
    (pdf_dir / "m.pdf").write_text("content")
    p.PDF_DIR = pdf_dir
    try:
        result = pdfs()
        assert [r.name for r in result] == ["a.pdf", "m.pdf", "z.pdf"]
    finally:
        p.PDF_DIR = original_pdf_dir
