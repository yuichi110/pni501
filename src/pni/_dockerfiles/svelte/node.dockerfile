ARG NODE_VERSION=20
FROM node:${NODE_VERSION}-bookworm

WORKDIR /workspace

ENV CI=true \
    NODE_ENV=test \
    COREPACK_ENABLE_STRICT=0 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

RUN useradd -m -u 10001 -s /bin/sh pni || true && \
    mkdir -p /out /ms-playwright && \
    corepack enable || true

COPY . /workspace

# Sanitize non-standard packageManager fields and prepare hooks (e.g. husky)
RUN if [ -f package.json ]; then \
        node -e 'const fs=require("fs");try{const p=JSON.parse(fs.readFileSync("package.json","utf8"));if(p.packageManager&&!/^(npm|pnpm|yarn)@/.test(p.packageManager)){delete p.packageManager;}if(p.scripts&&p.scripts.prepare){delete p.scripts.prepare;}fs.writeFileSync("package.json",JSON.stringify(p,null,2)+"\n");}catch(_){}' || true; \
    fi

# Install dependencies during image build so Stage 2/3 can execute with --network=none
RUN if [ -f pnpm-lock.yaml ]; then \
        pnpm install --frozen-lockfile --ignore-scripts || pnpm install --ignore-scripts || pnpm install || true; \
    elif [ -f yarn.lock ]; then \
        yarn install --frozen-lockfile --ignore-scripts || yarn install --ignore-scripts || yarn install || true; \
    elif [ -f package-lock.json ]; then \
        npm ci --ignore-scripts || npm install --ignore-scripts || npm install || true; \
    elif [ -f package.json ]; then \
        npm install --ignore-scripts || npm install || true; \
    fi

RUN chmod -R a+rwX /workspace /out /ms-playwright

USER pni
CMD ["node", "--version"]
