"""Tests for grobid.grobid_client."""

import subprocess
from unittest.mock import MagicMock, patch

from grobid.grobid_client import is_grobid_alive, pdf_to_tei, start_grobid


def test_is_grobid_alive_true():
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_resp
        assert is_grobid_alive() is True


def test_is_grobid_alive_false():
    from urllib.error import URLError

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = URLError("Connection refused")
        assert is_grobid_alive() is False


def test_is_grobid_alive_status_not_200():
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.status = 500
        mock_urlopen.return_value.__enter__.return_value = mock_resp
        assert is_grobid_alive() is False


def test_start_grobid_already_alive():
    with (
        patch("grobid.grobid_client.is_grobid_alive", return_value=True),
        patch("grobid.grobid_client.log") as mock_log,
    ):
        result = start_grobid()
        assert result is True
        mock_log.info.assert_called()


def test_start_grobid_no_docker():
    with (
        patch("grobid.grobid_client.is_grobid_alive", return_value=False),
        patch("grobid.grobid_client.which", return_value=None),
        patch("grobid.grobid_client.log") as mock_log,
    ):
        result = start_grobid()
        assert result is False
        mock_log.warn.assert_called()


def test_start_grobid_docker_success():
    with (
        patch("grobid.grobid_client.is_grobid_alive", side_effect=[False, True]),
        patch("grobid.grobid_client.which", return_value="/usr/bin/docker"),
        patch("subprocess.run") as mock_run,
        patch("grobid.grobid_client.log") as mock_log,
    ):
        result = start_grobid()
        assert result is True
        assert mock_run.call_count == 2
        mock_log.info.assert_called()


def test_start_grobid_docker_fails():
    with (
        patch("grobid.grobid_client.is_grobid_alive", return_value=False),
        patch("grobid.grobid_client.which", return_value="/usr/bin/docker"),
        patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "docker")),
        patch("grobid.grobid_client.log") as mock_log,
    ):
        result = start_grobid()
        assert result is False
        mock_log.error.assert_called()


def test_start_grobid_timeout():
    # Test that after starting docker, if GROBID becomes ready after a few checks, it succeeds
    call_count = [0]

    def mock_is_alive() -> bool:
        call_count[0] += 1
        return call_count[0] >= 3

    with (
        patch("grobid.grobid_client.is_grobid_alive", side_effect=mock_is_alive),
        patch("grobid.grobid_client.which", return_value="/usr/bin/docker"),
        patch("subprocess.run"),
        patch("grobid.grobid_client.time.sleep"),
        patch("grobid.grobid_client.log") as mock_log,
    ):
        result = start_grobid()
        assert result is True
        assert call_count[0] == 3
        mock_log.info.assert_any_call("GROBID ready after %ds", 2)


def test_pdf_to_tei_success(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("pdf content")

    mock_client = MagicMock()
    mock_client.process_pdf.return_value = (None, 200, "<TEI>content</TEI>")

    def tei_path_fn(p):
        return tmp_path / f"{p.stem}.tei.xml"

    status, out_path, _elapsed = pdf_to_tei(mock_client, pdf_path, tei_path_fn)

    assert status == 200
    assert out_path is not None
    assert out_path.exists()
    assert out_path.read_text() == "<TEI>content</TEI>"
    assert _elapsed >= 0


def test_pdf_to_tei_failure():
    pdf_path = MagicMock()
    mock_client = MagicMock()
    mock_client.process_pdf.return_value = (None, 500, "")

    def tei_path_fn(p):
        return MagicMock()

    status, out_path, _elapsed = pdf_to_tei(mock_client, pdf_path, tei_path_fn)

    assert status == 500
    assert out_path is None
    assert _elapsed >= 0


def test_pdf_to_tei_empty_response():
    pdf_path = MagicMock()
    mock_client = MagicMock()
    mock_client.process_pdf.return_value = (None, 200, None)

    def tei_path_fn(p):
        return MagicMock()

    status, out_path, _elapsed = pdf_to_tei(mock_client, pdf_path, tei_path_fn)

    assert status == 200
    assert out_path is None
