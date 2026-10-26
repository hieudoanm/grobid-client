"""Tests for grobid.utils."""

from unittest.mock import patch

from lxml import etree

from grobid.utils import Logger, normalize, text_content, yaml_string


def test_normalize():
    assert normalize("Hello, World!") == "hello world"
    assert normalize("  Test   Case  ") == "test case"
    assert normalize("Special@#$Chars") == "special chars"
    assert normalize("") == ""
    assert normalize("UPPERCASE") == "uppercase"


def test_yaml_string():
    assert yaml_string('hello"world') == '"hello\\"world"'
    assert yaml_string("simple") == '"simple"'
    assert yaml_string("with\\backslash") == '"with\\\\backslash"'
    assert yaml_string("") == '""'
    assert yaml_string("multi\nline") == '"multi\nline"'


def test_text_content():
    xml = """<p xmlns="http://www.tei-c.org/ns/1.0">Hello   <hi rend="italic">world</hi> <ref target="http://example.com">link</ref></p>"""
    etree.XMLParser(resolve_entities=False, no_network=True)
    root = etree.fromstring(xml)
    result = text_content(root)
    assert "Hello" in result
    assert "world" in result
    assert "link" in result


def test_logger_init():
    logger = Logger("info")
    assert logger.level == 3
    logger = Logger("DEBUG")
    assert logger.level == 4
    logger = Logger("unknown")
    assert logger.level == 3


def test_logger_fatal(capsys):
    logger = Logger("fatal")
    with patch("sys.exit") as mock_exit:
        logger.fatal("test message")
        mock_exit.assert_called_once_with(1)
    captured = capsys.readouterr()
    assert "FATAL" in captured.err
    assert "test message" in captured.err


def test_logger_error(capsys):
    logger = Logger("error")
    logger.error("test error")
    captured = capsys.readouterr()
    assert "ERROR" in captured.err
    assert "test error" in captured.err


def test_logger_warn(capsys):
    logger = Logger("warn")
    logger.warning("test warn")
    captured = capsys.readouterr()
    assert "WARN" in captured.out
    assert "test warn" in captured.out


def test_logger_info(capsys):
    logger = Logger("info")
    logger.info("test info")
    captured = capsys.readouterr()
    assert "INFO" in captured.out
    assert "test info" in captured.out


def test_logger_debug_not_shown(capsys):
    logger = Logger("info")
    logger.debug("test debug")
    captured = capsys.readouterr()
    assert "test debug" not in captured.out


def test_logger_debug_shown(capsys):
    logger = Logger("debug")
    logger.debug("test debug")
    captured = capsys.readouterr()
    assert "DEBUG" in captured.out
    assert "test debug" in captured.out


def test_logger_trace(capsys):
    logger = Logger("trace")
    logger.trace("test trace")
    captured = capsys.readouterr()
    assert "TRACE" in captured.out
    assert "test trace" in captured.out


def test_logger_formatting(capsys):
    logger = Logger("info")
    logger.info("Hello %s", "World")
    captured = capsys.readouterr()
    assert "Hello World" in captured.out


def test_logger_timestamp(capsys):
    logger = Logger("info")
    logger.info("test")
    captured = capsys.readouterr()
    # Check timestamp format YYYY-MM-DD HH:MM:SS
    import re

    assert re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", captured.out)
