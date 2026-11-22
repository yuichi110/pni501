FROM debian:bookworm-slim

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive \
    CABAL_DIR="/opt/cabal"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ghc cabal-install ${EXTRA_APT_PACKAGES} \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out /opt/cabal \
    && chown -R pni:pni /workspace /out /opt/cabal \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

RUN if ls *.cabal >/dev/null 2>&1; then \
      cabal update || true; \
      cabal build all --enable-tests || true; \
    fi \
    && chown -R pni:pni /workspace /opt/cabal \
    && chmod -R a+rwX /workspace /opt/cabal /out

USER pni
CMD ["ghc", "--version"]
