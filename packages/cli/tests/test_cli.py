"""Tests for grobid.cli."""

from unittest.mock import MagicMock, patch

from grobid.cli import convert_pdf_to_md, main


def test_main_no_args():
    with patch("grobid.cli.convert_pdf_to_md", return_value=0) as mock_convert:
        import sys

        original_argv = sys.argv
        sys.argv = ["grobid"]
        try:
            result = main()
        finally:
            sys.argv = original_argv
        assert result == 0
        mock_convert.assert_called_once()


def test_main_with_args():
    with patch("grobid.cli.convert_pdf_to_md", return_value=0):
        import sys

        original_argv = sys.argv
        sys.argv = ["grobid", "--help"]
        try:
            main()
        except SystemExit:
            pass
        finally:
            sys.argv = original_argv


def test_convert_pdf_to_md_no_pdfs(tmp_path, monkeypatch):
    from grobid import paths

    original_pdf_dir = paths.PDF_DIR
    original_tei_dir = paths.TEI_DIR
    original_md_dir = paths.MD_DIR

    paths.PDF_DIR = tmp_path / "pdf"
    paths.TEI_DIR = tmp_path / "tei"
    paths.MD_DIR = tmp_path / "md"

    try:
        with patch("grobid.cli.log") as mock_log:
            result = convert_pdf_to_md()
            assert result == 0
            mock_log.warn.assert_called()
    finally:
        paths.PDF_DIR = original_pdf_dir
        paths.TEI_DIR = original_tei_dir
        paths.MD_DIR = original_md_dir


def test_convert_pdf_to_md_grobid_unavailable(tmp_path, monkeypatch):
    from grobid import paths

    original_pdf_dir = paths.PDF_DIR
    original_tei_dir = paths.TEI_DIR
    original_md_dir = paths.MD_DIR

    paths.PDF_DIR = tmp_path / "pdf"
    paths.TEI_DIR = tmp_path / "tei"
    paths.MD_DIR = tmp_path / "md"
    paths.PDF_DIR.mkdir(parents=True)
    (paths.PDF_DIR / "test.pdf").write_text("content")

    try:
        with (
            patch("grobid.cli.start_grobid", return_value=False),
            patch("grobid.cli.is_grobid_alive", return_value=False),
            patch("grobid.cli.log") as mock_log,
        ):
            result = convert_pdf_to_md()
            assert result == 1
            mock_log.error.assert_called_with("GROBID is not available")
    finally:
        paths.PDF_DIR = original_pdf_dir
        paths.TEI_DIR = original_tei_dir
        paths.MD_DIR = original_md_dir


def test_convert_pdf_to_md_grobid_client_fails(tmp_path, monkeypatch):
    from grobid import paths

    original_pdf_dir = paths.PDF_DIR
    original_tei_dir = paths.TEI_DIR
    original_md_dir = paths.MD_DIR

    paths.PDF_DIR = tmp_path / "pdf"
    paths.TEI_DIR = tmp_path / "tei"
    paths.MD_DIR = tmp_path / "md"
    paths.PDF_DIR.mkdir(parents=True)
    (paths.PDF_DIR / "test.pdf").write_text("content")

    try:
        with (
            patch("grobid.cli.start_grobid", return_value=True),
            patch("grobid.cli.is_grobid_alive", return_value=True),
            patch(
                "grobid_client.grobid_client.GrobidClient",
                side_effect=ImportError("Connection failed"),
            ),
            patch("grobid.cli.log") as mock_log,
        ):
            result = convert_pdf_to_md()
            assert result == 1
            mock_log.error.assert_called()
    finally:
        paths.PDF_DIR = original_pdf_dir
        paths.TEI_DIR = original_tei_dir
        paths.MD_DIR = original_md_dir


def test_convert_pdf_to_md_success(tmp_path, monkeypatch):
    from grobid import paths

    original_pdf_dir = paths.PDF_DIR
    original_tei_dir = paths.TEI_DIR
    original_md_dir = paths.MD_DIR

    paths.PDF_DIR = tmp_path / "pdf"
    paths.TEI_DIR = tmp_path / "tei"
    paths.MD_DIR = tmp_path / "md"
    paths.PDF_DIR.mkdir(parents=True)
    paths.TEI_DIR.mkdir(parents=True)
    paths.MD_DIR.mkdir(parents=True)
    (paths.PDF_DIR / "test.pdf").write_text("content")

    try:
        with (
            patch("grobid.cli.start_grobid", return_value=True),
            patch("grobid.cli.is_grobid_alive", return_value=True),
            patch(
                "grobid_client.grobid_client.GrobidClient",
                return_value=MagicMock(
                    process_pdf=lambda *a, **kw: (None, 200, "<TEI>test</TEI>")
                ),
            ),
            patch("grobid.cli.convert_tei_to_md", return_value="# Test\n\nContent"),
            patch("grobid.cli.log") as mock_log,
        ):
            result = convert_pdf_to_md()
            assert result == 0
            mock_log.info.assert_called()
    finally:
        paths.PDF_DIR = original_pdf_dir
        paths.TEI_DIR = original_tei_dir
        paths.MD_DIR = original_md_dir


def test_convert_pdf_to_md_uses_existing_tei(tmp_path, monkeypatch):
    from grobid import paths

    original_pdf_dir = paths.PDF_DIR
    original_tei_dir = paths.TEI_DIR
    original_md_dir = paths.MD_DIR

    paths.PDF_DIR = tmp_path / "pdf"
    paths.TEI_DIR = tmp_path / "tei"
    paths.MD_DIR = tmp_path / "md"
    paths.PDF_DIR.mkdir(parents=True)
    paths.TEI_DIR.mkdir(parents=True)
    paths.MD_DIR.mkdir(parents=True)
    (paths.PDF_DIR / "test.pdf").write_text("content")
    (paths.TEI_DIR / "test.tei.xml").write_text("<TEI>existing</TEI>")

    try:
        with (
            patch("grobid.cli.start_grobid", return_value=True),
            patch("grobid.cli.is_grobid_alive", return_value=True),
            patch(
                "grobid_client.grobid_client.GrobidClient",
                return_value=MagicMock(),
            ),
            patch(
                "grobid.cli.convert_tei_to_md", return_value="# Test\n\nContent"
            ) as mock_convert,
            patch("grobid.cli.log"),
        ):
            result = convert_pdf_to_md()
            assert result == 0
            mock_convert.assert_called_once()
    finally:
        paths.PDF_DIR = original_pdf_dir
        paths.TEI_DIR = original_tei_dir
        paths.MD_DIR = original_md_dir


def test_convert_pdf_to_md_uses_existing_md(tmp_path, monkeypatch):
    from grobid import paths

    original_pdf_dir = paths.PDF_DIR
    original_tei_dir = paths.TEI_DIR
    original_md_dir = paths.MD_DIR

    paths.PDF_DIR = tmp_path / "pdf"
    paths.TEI_DIR = tmp_path / "tei"
    paths.MD_DIR = tmp_path / "md"
    paths.PDF_DIR.mkdir(parents=True)
    paths.TEI_DIR.mkdir(parents=True)
    paths.MD_DIR.mkdir(parents=True)
    (paths.PDF_DIR / "test.pdf").write_text("content")
    (paths.TEI_DIR / "test.tei.xml").write_text("<TEI>existing</TEI>")
    (paths.MD_DIR / "test.md").write_text("# Existing MD")

    try:
        with (
            patch("grobid.cli.start_grobid", return_value=True),
            patch("grobid.cli.is_grobid_alive", return_value=True),
            patch(
                "grobid_client.grobid_client.GrobidClient",
                return_value=MagicMock(),
            ),
            patch("grobid.cli.convert_tei_to_md") as mock_convert,
            patch("grobid.cli.log"),
        ):
            result = convert_pdf_to_md()
            assert result == 0
            mock_convert.assert_not_called()
    finally:
        paths.PDF_DIR = original_pdf_dir
        paths.TEI_DIR = original_tei_dir
        paths.MD_DIR = original_md_dir


def test_convert_pdf_to_md_pdf_to_tei_fails(tmp_path, monkeypatch):
    from grobid import paths

    original_pdf_dir = paths.PDF_DIR
    original_tei_dir = paths.TEI_DIR
    original_md_dir = paths.MD_DIR

    paths.PDF_DIR = tmp_path / "pdf"
    paths.TEI_DIR = tmp_path / "tei"
    paths.MD_DIR = tmp_path / "md"
    paths.PDF_DIR.mkdir(parents=True)
    paths.TEI_DIR.mkdir(parents=True)
    paths.MD_DIR.mkdir(parents=True)
    (paths.PDF_DIR / "test.pdf").write_text("content")

    try:
        with (
            patch("grobid.cli.start_grobid", return_value=True),
            patch("grobid.cli.is_grobid_alive", return_value=True),
            patch(
                "grobid_client.grobid_client.GrobidClient",
                return_value=MagicMock(process_pdf=lambda *a, **kw: (None, 500, "")),
            ),
            patch("grobid.cli.log") as mock_log,
        ):
            result = convert_pdf_to_md()
            assert result == 0  # Still returns 0, just logs error
            mock_log.error.assert_called()
    finally:
        paths.PDF_DIR = original_pdf_dir
        paths.TEI_DIR = original_tei_dir
        paths.MD_DIR = original_md_dir


def test_convert_pdf_to_md_tei_to_md_fails(tmp_path, monkeypatch):
    from grobid import paths

    original_pdf_dir = paths.PDF_DIR
    original_tei_dir = paths.TEI_DIR
    original_md_dir = paths.MD_DIR

    paths.PDF_DIR = tmp_path / "pdf"
    paths.TEI_DIR = tmp_path / "tei"
    paths.MD_DIR = tmp_path / "md"
    paths.PDF_DIR.mkdir(parents=True)
    paths.TEI_DIR.mkdir(parents=True)
    paths.MD_DIR.mkdir(parents=True)
    (paths.PDF_DIR / "test.pdf").write_text("content")

    try:
        with (
            patch("grobid.cli.start_grobid", return_value=True),
            patch("grobid.cli.is_grobid_alive", return_value=True),
            patch(
                "grobid_client.grobid_client.GrobidClient",
                return_value=MagicMock(
                    process_pdf=lambda *a, **kw: (None, 200, "<TEI>test</TEI>")
                ),
            ),
            patch(
                "grobid.cli.convert_tei_to_md",
                side_effect=OSError("Conversion failed"),
            ),
            patch("grobid.cli.log") as mock_log,
        ):
            result = convert_pdf_to_md()
            assert result == 0
            mock_log.error.assert_called()
    finally:
        paths.PDF_DIR = original_pdf_dir
        paths.TEI_DIR = original_tei_dir
        paths.MD_DIR = original_md_dir
