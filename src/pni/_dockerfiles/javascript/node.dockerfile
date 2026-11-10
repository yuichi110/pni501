ARG NODE_VERSION=20
FROM node:${NODE_VERSION}-bookworm

WORKDIR /workspace

ENV CI=true \
    NODE_ENV=test

RUN corepack enable || true

COPY . /workspace

# Install dependencies during image build so Stage 2/3 can execute with --network=none
RUN if [ -f pnpm-lock.yaml ]; then \
        pnpm install --frozen-lockfile || pnpm install; \
    elif [ -f yarn.lock ]; then \
        yarn install --frozen-lockfile || yarn install; \
    elif [ -f package-lock.json ]; then \
        npm ci || npm install; \
    elif [ -f package.json ]; then \
        npm install; \
    fi

CMD ["node", "--version"]
