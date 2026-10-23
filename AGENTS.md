# AGENTS.md

## Project Overview

grobid-cli converts PDF articles to Markdown via GROBID TEI XML. Built upon [GROBID](https://github.com/grobidOrg). The CLI is designed to make PDFs AI-friendly by producing clean, structured Markdown with metadata in frontmatter.

**Problem:** AI models struggle with raw PDFs (messy structure, headers/footers, citations).  
**Solution:** Use GROBID to extract structured content and convert to clean Markdown.

## Architecture

### Source Structure

```
src/grobid/
├── __init__.py      # Public API, exports version
├── main.py          # Entry point
├── cli.py           # CLI logic (convert_pdf_to_md)
├── config.py        # Configuration (ports, images, paths, NS, META_FIELDS)
├── utils.py         # Logging (timestamped, levels: fatal/error/warn/info/debug/trace) & helpers
├── paths.py         # Path resolution (PDF_DIR, TEI_DIR, MD_DIR)
├── grobid_client.py # Docker GROBID management & PDF→TEI via grobid-client-python
├── metadata.py      # Metadata extraction from TEI
├── render.py        # TEI → Markdown conversion (inline, blocks, tables, lists, figures)
└── version.py       # Dynamic version from file mtime (build timestamp for binaries)
```

### Pipeline

1. **Auto-start GROBID**: If not running, starts `grobid/grobid:0.9.1-crf` in Docker on port 8070
2. **PDF → TEI**: Uses `grobid-client-python` to call `processFulltextDocument` service
3. **TEI → Markdown**: Parses TEI XML with lxml, extracts metadata/title/authors/abstract/body/references, renders to Markdown with YAML frontmatter

### Single Entry Point

- Command: `grobid` (via `pyproject.toml` scripts: `grobid = "grobid.main:main"`)
- Behavior: Converts all PDFs in `pdf/` dir to TEI in `tei/` and Markdown in `md/`
- Resumable: Skips existing TEI and Markdown files
- Auto-creates directories

### Version Management

- **Package version**: Defined in `pyproject.toml` as `0.0.1`
- **Runtime version**: `src/grobid/version.py` provides dynamic `__version__` based on file modification time (or binary mtime when frozen with PyInstaller)
- **Build-time version**: `Makefile` generates `src/grobid/_version.py` with timestamp during binary build
- **Public API**: `__version__` exported from `src/grobid/__init__.py` (currently hardcoded to `0.1.0`, should align with dynamic version)

## Environment Variables

- `GROBID_DATA_DIR` or `ARTICLES_DATA_DIR`: Data directory (default: cwd)
- `GROBID_PORT`: GROBID port (default: 8070)
- `GROBID_IMAGE`: Docker image (default: `grobid/grobid:0.9.1-crf`)
- `GROBID_CONTAINER`: Container name (default: `grobid-cli`)

## Tech Stack

### Runtime

- **Python** 3.15.1 (`.python-version`, `pyproject.toml: requires-python = "==3.15.1"`)
- **Build**: `setuptools==84.2.1` (PEP 517)
- **Virtual env**: `uv` with `.venv`

### Core Dependencies

| Package                | Version   | Purpose                       |
| ---------------------- | --------- | ----------------------------- |
| `grobid-client-python` | `==0.2.1` | GROBID TEI XML service client |
| `lxml`                 | `==6.1.3` | XML parsing (TEI → Markdown)  |

### Dev Dependencies (from uv.lock)

| Package       | Version   | Purpose                   |
| ------------- | --------- | ------------------------- |
| `pytest`      | `9.1.1`   | Testing                   |
| `ruff`        | `0.17.2`  | Linting + formatting      |
| `mypy`        | `2.4.0`   | Static type checking      |
| `pyinstaller` | `6.22.3`  | Binary builds             |
| `pre-commit`  | `==4.7.0` | Git hooks (lint + format) |
| `pytest-cov`  | `6.2.1`   | Test coverage             |

### Tooling

- **Package manager**: `uv` (or `pip`)
- **Lint/Format**: `ruff` (replaces `black`)
- **Pre-commit**: local hooks → `make lint`, `make format` (`.pre-commit-config.yaml`)
- **CI/CD**: GitHub Actions (`.github/workflows/ci.yaml`)
- **Release**: `softprops/action-gh-release` → GitHub Releases tagged `latest`

### External Services

- **GROBID**: Docker image `grobid/grobid:0.9.1-crf` on port 8070
- **Docker**: required for GROBID container management

## Dependencies

- `lxml==6.1.3` - XML parsing
- `grobid-client-python==0.2.1` - PDF processing (GROBID TEI service)
- `pyinstaller==6.22.3` (dev) - Binary builds
- `pytest==9.1.1`, `ruff==0.17.2`, `mypy==2.4.0`, `pre-commit==4.7.0`, `pytest-cov==6.2.1` (dev) - Testing/linting/type-checking

## Build & Test

```bash
make lint    # ruff check src tests
make format  # ruff format + ruff check --fix
make test    # pytest with coverage
make build   # Generates _version.py with timestamp, then pyinstaller --onefile --name grobid src/grobid/main.py
```

Pre-commit hooks (`.pre-commit-config.yaml`):

```bash
pre-commit install
pre-commit run --all-files
```

### Pre-commit Configuration (`.pre-commit-config.yaml`)

```yaml
repos:
  - repo: local
    hooks:
      - id: lint
        name: Run lint
        entry: make lint
        language: system
        pass_filenames: false

      - id: format
        name: Run format
        entry: make format
        language: system
        pass_filenames: false
```

## GitHub Actions (`.github/workflows/ci.yaml`)

CI workflow runs on push/PR to master:
1. **Lint**: `ruff check src tests` + `black --check src tests`
2. **Test**: `pytest tests -v --cov=src/grobid --cov-report=term-missing`
3. **Build**: `pyinstaller --onefile --name grobid src/grobid/main.py`
4. **Upload artifact**: Binary uploaded for release job

On push to master, the release job:
- Deletes old "latest" release and tag
- Creates new "latest" release with binary using `softprops/action-gh-release@v3.0.3`

## Docker Compose (`docker-compose.yaml`)

```yaml
services:
  grobid:
    image: grobid/grobid:0.9.1-crf
    container_name: grobid
    restart: unless-stopped
    init: true
    ports:
      - "8070:8070"
    environment:
      JAVA_TOOL_OPTIONS: "-Xms1g -Xmx4g"
    ulimits:
      core: 0
```

## Installation Script (`scripts/install.sh`)

Downloads latest binary from GitHub Releases, installs to `~/.local/bin`, checks for Docker and prompts to install if missing.

## Code Style

- Python 3.15.1
- Type hints where appropriate
- Timestamped logging with levels (fatal, error, warn, info, debug, trace)
- Keep files under ~200 lines
- Minimal, focused implementation
- Formatting via `ruff format` (not `black`)