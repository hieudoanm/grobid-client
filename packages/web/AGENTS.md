# AGENTS.md - @grobid/web

## Overview

This is the Next.js web application for the grobid-cli project. It provides a
web interface to upload PDFs and convert them to Markdown via a self-hosted
GROBID instance.

## Architecture

### Tech Stack

- **Framework**: Next.js 16 with App Router
- **Runtime**: React 19
- **Language**: TypeScript 6 (strict mode)
- **Testing**: Vitest with jsdom and React Testing Library
- **Package Manager**: pnpm 12 (monorepo workspace)

### Codebase Structure

```
packages/web/
├── app/                    # Next.js App Router pages and layouts
├── components/             # Reusable React components
├── lib/                    # Utility functions and API clients
├── __tests__/              # Test files (or colocated *.test.tsx)
├── vitest.config.ts        # Vitest configuration
├── vitest.setup.ts         # Test setup and global imports
└── next.config.ts          # Next.js configuration
```

## Development Guidelines

### Code Style

- Use TypeScript strict mode
- Follow Next.js App Router conventions
- Use functional components with hooks
- Prefer server components when possible, use client components only when
  necessary
- Keep components small and focused

### API Integration

- GROBID service runs on port 8070 by default
- Use environment variables for configuration (`GROBID_URL`)
- Handle errors gracefully and provide user feedback
- Respect GROBID API limits and timeouts

### Testing

- Write tests for components, utilities, and API routes
- Use React Testing Library for component tests
- Use Vitest for unit and integration tests
- Test setup includes `@testing-library/jest-dom` matchers
- Run tests with `pnpm test` (watch) or `pnpm test:run` (single run)

### Type Checking

- Run `pnpm typecheck` before committing
- All code must pass strict TypeScript checks

### Linting

- Run `pnpm lint` to check for issues
- Follow the project's ESLint configuration

## Commands

| Command           | Purpose                                    |
| ----------------- | ------------------------------------------ |
| `pnpm dev`        | Start development server on localhost:3000 |
| `pnpm build`      | Build for production                       |
| `pnpm start`      | Start production server                    |
| `pnpm lint`       | Run ESLint                                 |
| `pnpm typecheck`  | Run TypeScript type checking               |
| `pnpm test`       | Run tests in watch mode                    |
| `pnpm test:run`   | Run tests once                             |
| `pnpm test:watch` | Run tests in watch mode (alias)            |

## Environment Variables

Create `.env.local` for local development:

```env
GROBID_URL=http://localhost:8070
```

## Dependencies

### Runtime

- `next` - Next.js framework
- `react`, `react-dom` - React library
- `archiver` - File compression/archiving
- `fast-xml-parser` - XML parsing for TEI responses

### Development

- `vitest` - Test runner
- `@vitejs/plugin-react` - React support for Vitest
- `jsdom` - DOM environment for tests
- `@testing-library/react` - React component testing utilities
- `@testing-library/jest-dom` - Custom Jest matchers
- `typescript` - Type checking
- `eslint` - Linting

## Related Documentation

- [Root AGENTS.md](../../AGENTS.md) - Overall project documentation
- [GROBID API](https://grobid.readthedocs.io/en/latest/Grobid-service/) -
  Service API reference
- [Next.js Docs](https://nextjs.org/docs) - Framework documentation
