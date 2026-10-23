"""CLI."""

import argparse
import sys

try:
    from .grobid_client import is_grobid_alive, pdf_to_tei, start_grobid
    from .paths import MD_DIR, PDF_DIR, TEI_DIR, md_path, pdfs, tei_path
    from .render import convert_tei_to_md
    from .utils import log
    from .version import get_version
except ImportError:
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from grobid_client import is_grobid_alive, pdf_to_tei, start_grobid
    from paths import MD_DIR, PDF_DIR, TEI_DIR, md_path, pdfs, tei_path
    from render import convert_tei_to_md
    from utils import log
    from version import get_version


def convert_pdf_to_md() -> int:
    TEI_DIR.mkdir(parents=True, exist_ok=True)
    MD_DIR.mkdir(parents=True, exist_ok=True)

    log.info("=" * 60)
    log.info("Converting PDFs to Markdown via GROBID")
    log.info("=" * 60)
    log.info("PDF dir: %s", PDF_DIR)
    log.info("TEI dir: %s", TEI_DIR)
    log.info("MD dir: %s", MD_DIR)

    all_pdfs = pdfs()
    if not all_pdfs:
        log.warn("No PDFs found in %s", PDF_DIR)
        return 0

    if not start_grobid() and not is_grobid_alive():
        log.error("GROBID is not available")
        return 1

    log.info("Connecting to GROBID...")
    try:
        from grobid_client.grobid_client import GrobidClient

        client = GrobidClient()
    except (ImportError, OSError) as exc:
        log.error("GROBID server unavailable: %s", exc)
        return 1

    for index, pdf_path in enumerate(all_pdfs, start=1):
        tpath = tei_path(pdf_path)
        if not tpath.exists():
            log.info("[%d/%d] PDF → TEI: %s", index, len(all_pdfs), pdf_path.name)
            status, out_path, elapsed = pdf_to_tei(client, pdf_path, tei_path)
            if out_path is None:
                log.error("  FAILED (status=%s) after %.1fs", status, elapsed)
                continue
            tpath = out_path
            log.info("  wrote %s (%d bytes)", out_path.name, out_path.stat().st_size)
        else:
            log.info("[%d/%d] Using existing TEI: %s", index, len(all_pdfs), tpath.name)

        mpath = md_path(tpath)
        if mpath.exists():
            log.info("[%d/%d] Using existing MD: %s", index, len(all_pdfs), mpath.name)
            continue

        try:
            log.info("[%d/%d] TEI → MD: %s", index, len(all_pdfs), tpath.name)
            mpath.write_text(convert_tei_to_md(tpath), encoding="utf-8")
            log.info("  wrote %s (%d bytes)", mpath.name, mpath.stat().st_size)
        except OSError as exc:
            log.error("  FAILED: %s", exc)
            continue

    log.info("=" * 60)
    log.info("Conversion completed")
    log.info("=" * 60)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert PDFs to Markdown via GROBID")
    parser.add_argument("-v", "--version", action="store_true", help="Show version")
    args = parser.parse_args()
    if args.version:
        print(get_version())
        return 0
    return convert_pdf_to_md()


if __name__ == "__main__":
    sys.exit(main())
