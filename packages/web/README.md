# @grobid/web

Next.js web app to upload PDFs and convert them to Markdown via self-hosted
GROBID.

## Features

- Upload PDF files for conversion
- Extract structured content via GROBID TEI XML
- Convert to clean Markdown with metadata in frontmatter
- Support for references, figures, tables, and lists

## Getting Started

### Prerequisites

- Node.js 26.12.1
- pnpm 12.15.0
- Self-hosted GROBID instance (see
  [GROBID documentation](https://grobid.readthedocs.io/))

### Installation

```bash
pnpm install
```

### Development

```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

### Build

```bash
pnpm build
pnpm start
```

### Testing

```bash
pnpm test      # Run tests in watch mode
pnpm test:run  # Run tests once
```

## Environment Variables

Configure connection to your GROBID instance:

| Variable     | Default                 | Description             |
| ------------ | ----------------------- | ----------------------- |
| `GROBID_URL` | `http://localhost:8070` | GROBID service endpoint |

## Tech Stack

- [Next.js 16](https://nextjs.org/) - React framework
- [React 19](https://react.dev/) - UI library
- [TypeScript 6](https://www.typescriptlang.org/) - Type safety
- [Vitest](https://vitest.dev/) - Testing framework
- [Tailwind CSS](https://tailwindcss.com/) (if used) - Styling

## Project Structure

```text
packages/web/
├── app/              # Next.js App Router
├── components/       # React components
├── lib/              # Utilities and helpers
├── public/           # Static assets
├── styles/           # Global styles
└── types/            # TypeScript type definitions
```

## Related

- [grobid-cli](../../) - CLI tool for batch conversion
- [GROBID](https://github.com/grobidOrg/grobid) - Machine learning library for
  extracting structured data from PDFs
