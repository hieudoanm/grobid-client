"""grobid-cli."""

from .cli import convert_pdf_to_md, main
from .render import convert_tei_to_md

__version__ = "0.0.1"
__all__ = ["convert_pdf_to_md", "convert_tei_to_md", "main"]
