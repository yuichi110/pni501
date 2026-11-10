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

# Sanitize non-standard packageManager fields (e.g. nub) and prepare hooks (e.g. husky)
RUN if [ -f package.json ]; then \
        node -e 'const fs=require("fs");try{const p=JSON.parse(fs.readFileSync("package.json","utf8"));if(p.packageManager&&!/^(npm|pnpm|yarn)@/.test(p.packageManager)){delete p.packageManager;}if(p.scripts&&p.scripts.prepare){delete p.scripts.prepare;}fs.writeFileSync("package.json",JSON.stringify(p,null,2)+"\n");}catch(_){}' || true; \
    fi

# Install dependencies during image build so Stage 2/3 can execute with --network=none
RUN if [ -f pnpm-lock.yaml ]; then \
        pnpm install --frozen-lockfile --ignore-scripts || pnpm install --ignore-scripts || pnpm install; \
    elif [ -f yarn.lock ]; then \
        yarn install --frozen-lockfile --ignore-scripts || yarn install --ignore-scripts || yarn install; \
    elif [ -f package-lock.json ]; then \
        npm ci --ignore-scripts || npm install --ignore-scripts || npm install; \
    elif [ -f package.json ]; then \
        npm install --ignore-scripts || npm install; \
    fi

# Auto-provision Playwright Chromium + OS shared libraries when browser test runners are declared
RUN if [ -f package.json ] && \
       node -e 'const p=require("./package.json");const d=Object.assign({},p.dependencies,p.devDependencies);process.exit((d["playwright"]||d["@playwright/test"]||d["@web/test-runner-playwright"]||d["puppeteer"])?0:1)' 2>/dev/null; then \
        npx playwright install --with-deps chromium || true; \
    fi

# Auto-provision @vitest/coverage-v8 matching installed vitest major.minor when missing
RUN if [ -f node_modules/vitest/package.json ] && \
       [ ! -d node_modules/@vitest/coverage-v8 ] && \
       [ ! -d node_modules/@vitest/coverage-istanbul ]; then \
        VITEST_MM=$(node -e 'try{const v=require("./node_modules/vitest/package.json").version.split(".");process.stdout.write(v[0]+"."+v[1]+".0");}catch(_){}'); \
        if [ -n "$VITEST_MM" ]; then \
            if [ -f pnpm-lock.yaml ]; then \
                pnpm add -D -w --ignore-scripts "@vitest/coverage-v8@^${VITEST_MM}" || true; \
            elif [ -f yarn.lock ]; then \
                yarn add -D -W --ignore-scripts "@vitest/coverage-v8@^${VITEST_MM}" || true; \
            else \
                npm install --no-save --legacy-peer-deps --ignore-scripts "@vitest/coverage-v8@^${VITEST_MM}" || true; \
            fi; \
        fi; \
    fi && \
    chmod -R a+rwX /workspace /out /ms-playwright

USER pni

CMD ["node", "--version"]

