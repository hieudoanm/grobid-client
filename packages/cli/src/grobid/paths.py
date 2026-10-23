"""Paths."""

from pathlib import Path

from .config import get_data_dir


def resolve_paths():
    base = get_data_dir()
    return base / "pdf", base / "tei", base / "md"


PDF_DIR, TEI_DIR, MD_DIR = resolve_paths()


def tei_path(pdf_path: Path) -> Path:
    return TEI_DIR / f"{pdf_path.stem}.tei.xml"


def md_path(tei_path: Path) -> Path:
    return MD_DIR / f"{tei_path.name.removesuffix('.tei.xml')}.md"


def pdfs() -> list[Path]:
    if not PDF_DIR.is_dir():
        return []
    return sorted(PDF_DIR.glob("*.pdf"))
