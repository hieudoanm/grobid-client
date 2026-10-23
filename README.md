# grobid-cli

**Convert PDF articles to Markdown via GROBID TEI XML — making PDFs AI-friendly on your own machine.**

grobid-cli is a local, full-stack document-conversion studio. Drop PDFs into a `pdf/` directory, run the `grobid` command, and get clean, structured Markdown with rich metadata in YAML frontmatter — plus TEI XML intermediates. GROBID starts automatically in Docker on port 8070, and an optional Next.js web app offers a UI for upload-and-convert. Everything runs locally via Docker Compose — no cloud account or infrastructure setup.

[📄 Documentation](docs/index.html) · [🚀 Quick Start](#get-started) · [🔍 See It In Action](#see-it-in-action)

![grobid-cli](assets/og/og.png)

## The Problem

AI models struggle to extract clean, structured content from PDFs. Raw PDFs are messy — headers, footers, citations, tables, and figures make it hard for LLMs to parse and reason about academic papers or documents. Raw text extraction loses structure, citations break context, and formatting confuses models.

A useful local conversion tool needs to make it possible to:

- Drop PDFs into a `pdf/` directory and convert them in one command.
- Auto-start GROBID in Docker if it is not already running.
- Extract title, authors, journal, year, volume, issue, pages, and DOI as YAML frontmatter.
- Preserve abstract, article sections, references, tables, lists, and formulas.
- Convert resumably: skip TEI and Markdown files that already exist.
- Run the whole system with Docker Compose: GROBID service plus optional web UI.

grobid-cli brings these workflows together in one coherent application.

## The Solution

grobid-cli provides a focused, local-first workflow: drop PDFs into `pdf/`, run `grobid`, review the Markdown in `md/` (with TEI XML in `tei/`). It uses GROBID's state-of-the-art PDF parsing to produce clean, structured Markdown that LLMs can understand and reason about effectively, behind one `pdf/` → `tei/` → `md/` pipeline, with metadata captured as YAML frontmatter. Everything runs locally via Docker Compose — no third-party services, no account creation.

## Features

- **PDF → TEI → Markdown** — Full conversion pipeline using GROBID's TEI XML extraction via `grobid-client-python` (`processFulltextDocument`).
- **Auto-starts GROBID** — Automatically launches the `grobid/grobid:0.9.1-crf` Docker container on port 8070 if not already running.
- **Rich metadata** — Extracts title, authors, journal, year, volume, issue, pages, DOI, and DOI link and adds them as YAML frontmatter.
- **Structured output** — Preserves abstract, article sections, references, tables, lists, and figures.
- **Simple CLI** — One command (`grobid`) converts all PDFs in `pdf/` to TEI in `tei/` and Markdown in `md/`.
- **Resumable** — Skips already-converted TEI/XML and Markdown files; auto-creates directories.

## Key Benefits

- **Local-first & private** — Convert on your own machine. Your documents never leave your environment.
- **PDFs to Markdown in minutes** — One command turns a folder of PDFs into LLM-ready Markdown with metadata.
- **Honest conversion** — GROBID's TEI XML is the intermediate format; Markdown renders TEI faithfully with no information loss layer.
- **Reproducible by design** — Every run records data directory, ports, image, container name, and library versions.
- **Developer-friendly** — Python 3.15 CLI (`uv`/`setuptools`), Next.js web UI, Docker Compose topology, `ruff`/`mypy`/`pytest` tooling.

## See It in Action

![Grobid CLI Demo](assets/demo/demo.png)

Or read the full walkthrough in [`docs/index.html`](docs/index.html).

## Get Started

The fastest way to run grobid-cli locally:

### Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) v2
- [Python 3.15.1](https://www.python.org/) (for source install)

### Run the stack

```sh
docker compose up --build
```

This starts GROBID on port 8070 and the optional web app on port 3000.

### Open the app

| Service   | URL                              |
| --------- | -------------------------------- |
| GROBID    | <http://127.0.0.1:8070>          |
| Web app   | <http://127.0.0.1:3000>          |

Stop and clean up:

```sh
docker compose down -v
```

### CLI usage

1. Put your PDFs in a `pdf/` directory
2. Run the converter
3. Get TEI XML in `tei/` and Markdown in `md/`

```sh
grobid
```

Or set a custom data directory:

```sh
GROBID_DATA_DIR=/path/to/data grobid
```

### Output Example

```markdown
---
title: "Paper Title"
authors: "Author One, Author Two"
year: 2024
journal: "Journal Name"
volume: "10"
doi: "10.1234/example"
doi_link: "https://doi.org/10.1234/example"
---

# Paper Title

**Authors:** Author One, Author Two

## Abstract
...

## Article
...

## References
...
```

### Directory Structure

```
your-project/
├── pdf/          # Input PDFs
├── tei/          # Generated TEI XML (intermediate)
└── md/           # Output Markdown files
```

### Installation

#### Option 1: Prebuilt binary

```bash
# Download the latest binary
curl -fsSL https://github.com/hieudoanm/grobid-cli/releases/download/latest/grobid -o /usr/local/bin/grobid
chmod +x /usr/local/bin/grobid
```

Or use the install script (checks for Docker and prompts to install if missing):

```bash
curl -fsSL https://raw.githubusercontent.com/hieudoanm/grobid-cli/master/packages/cli/scripts/install.sh | bash
```

#### Option 2: From source

```bash
pip install -e .
# or
uv pip install -e .
```

## Use Cases

- **Research paper ingestion** — Turn PDF corpora into LLM-ready Markdown with citation metadata.
- **Bibliography extraction** — Pull structured references and DOI links from academic PDFs.
- **Local document processing** — Keep sensitive documents on-device while converting to structured Markdown.
- **LLM-ready corpora** — Feed clean Markdown (not raw PDF text) into retrieval-augmented generation pipelines.

## Why This Project?

- **Focused scope** — Does one thing well: convert PDFs to Markdown via GROBID TEI XML. No AutoML bloat.
- **Transparent** — Clear pipeline (PDF → TEI → Markdown), TEI intermediates preserved, metadata as frontmatter.
- **Local-first** — Runs entirely on your machine via Docker Compose; no vendor lock-in or external dependencies.
- **Production-minded** — Real Python CLI + Next.js implementation with tests, linting, type-checking, and binary releases.

## Project Status and Trust

- **Maturity:** Software demonstration (beta). PDF → TEI → Markdown conversion is implemented, including auto-starting GROBID, resumable conversion, and YAML frontmatter metadata.
- **License:** [MIT License](LICENSE) — see the `LICENSE` file for full terms.
- **Tech stack:** Python 3.15.1, `uv`, `setuptools`, `grobid-client-python==0.2.1`, `lxml==6.1.3`, PyInstaller (binary builds), Next.js 16 (web UI), Docker Compose.
- **Testing:** `pytest`, `ruff` (lint + format), `mypy` (type checking), `pre-commit` hooks, GitHub Actions CI.

## Community and Contributions

Contributions, bug reports, and feature suggestions are welcome. See existing resources:

- [AGENTS.md](AGENTS.md) — project overview, architecture, environment variables, tech stack, build & test
- [packages/cli/README.md](packages/cli/README.md) — CLI tool for batch conversion
- [packages/web/README.md](packages/web/README.md) — Next.js web app for upload-and-convert

To report issues or propose changes, open an issue or pull request in this repository.

## Call to Action

**[Get Started](#get-started)** — Run grobid-cli locally in minutes and convert your first PDF.

## License

This project is licensed under the [MIT License](LICENSE).
