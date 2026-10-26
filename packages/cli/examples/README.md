# Examples

This directory contains example files demonstrating the grobid-cli PDF → TEI → Markdown conversion pipeline.

## Directory Structure

```
examples/
├── pdf/   # Input PDF files
├── tei/   # Intermediate TEI XML output (generated)
├── md/    # Final Markdown output (generated)
├── examples.sh  # Test script
└── README.md    # This file
```

## Example Files

- **pdf/** - Contains a sample research paper PDF
  - `Predicting language outcome after stroke using machine learning - in search of the big data benefit.pdf`

- **tei/** - TEI XML output generated from the PDF
  - `Predicting language outcome after stroke using machine learning - in search of the big data benefit.tei.xml`

- **md/** - Markdown output generated from TEI with frontmatter metadata
  - `Predicting language outcome after stroke using machine learning - in search of the big data benefit.md`

## Running the Example

### Using the test script

```bash
./examples.sh
```

This script:

1. Checks if the `grobid` binary exists in `dist/grobid`
2. Runs `make build` if the binary doesn't exist
3. Executes the binary on the `examples/pdf/` directory

### Manual execution

```bash
# From project root
make build
./dist/grobid examples/pdf
```

## Output

The conversion produces:

1. **TEI XML** in `examples/tei/` - GROBID's structured XML representation
2. **Markdown** in `examples/md/` - Human-readable format with YAML frontmatter containing:
   - Title
   - Authors
   - Year
   - Journal
   - Volume/Issue/Pages
   - DOI
   - Abstract
   - Keywords

## Requirements

- Docker (for running GROBID server)
- Python 3.10+ (for development)
- Or the pre-built binary from `make build`
