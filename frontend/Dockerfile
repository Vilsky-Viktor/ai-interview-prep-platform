FROM node:24-alpine AS build

RUN corepack enable

WORKDIR /frontend

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

ARG NEXT_PUBLIC_FIREBASE_API_KEY
ARG NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
ARG NEXT_PUBLIC_FIREBASE_PROJECT_ID
ARG NEXT_PUBLIC_FIREBASE_AUTH_EMULATOR_URL
RUN pnpm build

# Development: docker-compose.yml mounts the source, and Next reloads on change.
FROM node:24-alpine AS dev

RUN corepack enable

WORKDIR /frontend

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile

ENV NODE_ENV=development HOSTNAME=0.0.0.0 PORT=3000 WATCHPACK_POLLING=true

EXPOSE 3000

CMD ["pnpm", "exec", "next", "dev", "--hostname", "0.0.0.0", "--port", "3000", "--webpack"]

# Production: the standalone server from the build stage. NEXT_PUBLIC_* values are baked in at
# build time, so pass them as build arguments.
FROM node:24-alpine AS prod

WORKDIR /frontend

ENV NODE_ENV=production HOSTNAME=0.0.0.0 PORT=3000

COPY --from=build /frontend/.next/standalone ./
COPY --from=build /frontend/.next/static ./.next/static
COPY --from=build /frontend/public ./public

EXPOSE 3000

CMD ["node", "server.js"]
