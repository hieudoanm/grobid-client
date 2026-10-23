"""GROBID client."""

import subprocess
import time
from shutil import which
from urllib.error import URLError

from .config import (
    GROBID_CONTAINER,
    GROBID_IMAGE,
    GROBID_PORT,
    GROBID_URL,
    HEALTH_URL,
)
from .utils import log


def is_grobid_alive() -> bool:
    try:
        import urllib.request

        req = urllib.request.Request(HEALTH_URL, method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except URLError:
        return False


def start_grobid() -> bool:
    if is_grobid_alive():
        log.info("GROBID already running at %s", GROBID_URL)
        return True
    if not which("docker"):
        log.warn("Docker not found. Start GROBID manually at %s", GROBID_URL)
        return is_grobid_alive()
    try:
        subprocess.run(
            ["docker", "rm", "-f", GROBID_CONTAINER],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "--rm",
                "--init",
                "--ulimit",
                "core=0",
                "-p",
                f"{GROBID_PORT}:8070",
                "--name",
                GROBID_CONTAINER,
                GROBID_IMAGE,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        log.info("Starting GROBID container %s...", GROBID_CONTAINER)
        for i in range(120):
            if is_grobid_alive():
                log.info("GROBID ready after %ds", i + 1)
                return True
            time.sleep(1)
        log.error("GROBID did not become ready in time")
        return False
    except (subprocess.SubprocessError, OSError) as exc:
        log.error("Failed to start GROBID: %s", exc)
        return False


def pdf_to_tei(client, pdf_path, tei_path_fn):
    import time

    from .config import GROBID_CONSOLIDATE_HEADER, GROBID_SERVICE

    started = time.time()
    _, status, tei = client.process_pdf(
        GROBID_SERVICE,
        str(pdf_path),
        consolidate_header=GROBID_CONSOLIDATE_HEADER,
    )
    elapsed = time.time() - started
    if status != 200 or not tei:
        return status, None, elapsed
    out_path = tei_path_fn(pdf_path)
    out_path.write_text(tei, encoding="utf-8")
    return status, out_path, elapsed
