#!/usr/bin/env bash
set -euo pipefail

# Directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BINARY_PATH="$PROJECT_ROOT/target/release/grobid"
PDF_DIR="$SCRIPT_DIR/pdf"

# Check if binary exists, if not build it
if [[ ! -f "$BINARY_PATH" ]]; then
    echo "Binary not found at $BINARY_PATH"
    echo "Building..."
    cd "$PROJECT_ROOT"
    cargo build --release
fi

# Verify binary exists after build
if [[ ! -f "$BINARY_PATH" ]]; then
    echo "ERROR: Binary still not found after build"
    exit 1
fi

# Run the binary on the PDF directory
echo "Running grobid on PDFs in $PDF_DIR"
export GROBID_DATA_DIR="$SCRIPT_DIR"
cd "$SCRIPT_DIR"
"$BINARY_PATH" -v
"$BINARY_PATH"
