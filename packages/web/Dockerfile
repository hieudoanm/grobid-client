# Stage 1: Build
FROM node:26.13.0-alpine AS builder

WORKDIR /app

RUN corepack enable && corepack prepare pnpm@12.15.0 --activate

COPY package.json ./

RUN pnpm install

COPY tsconfig.json next.config.ts ./
COPY src ./src

RUN pnpm run build

# Stage 2: Runtime
FROM node:26.13.0-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/.next/standalone/packages/web/ ./

USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
