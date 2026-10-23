# AGENTS.md

## Overview

Rust CLI to convert PDFs to Markdown via GROBID TEI XML.

## Structure

- `src/cli.rs` - Main conversion logic
- `src/grobid_client.rs` - GROBID HTTP client + Docker container management
- `src/render.rs` - TEI XML to Markdown rendering
- `src/metadata.rs` - Metadata extraction and YAML frontmatter
- `src/paths.rs` - Path resolution for pdf/tei/md directories
- `src/config.rs` - Configuration and constants
- `src/utils.rs` - Logging and helpers
- `src/version.rs` - Version from file mtime

## Build

```bash
cargo build --release
```

## Test

```bash
cargo test
```

## Environment

- `GROBID_DATA_DIR` or `ARTICLES_DATA_DIR`: base directory for pdf/tei/md
- `GROBID_PORT`: GROBID port (default 8070)
- `GROBID_IMAGE`: Docker image (default grobid/grobid:0.9.1-crf)
- `GROBID_CONTAINER`: Container name (default grobid-cli)
