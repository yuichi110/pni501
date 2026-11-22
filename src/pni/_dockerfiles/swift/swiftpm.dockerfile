ARG SWIFT_VERSION=6.0
FROM swift:${SWIFT_VERSION}-bookworm

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive \
    SWIFT_CACHE_PATH="/opt/pni-swift-cache"

RUN if [ -n "${EXTRA_APT_PACKAGES}" ]; then \
      apt-get update \
      && apt-get install -y --no-install-recommends ${EXTRA_APT_PACKAGES} \
      && rm -rf /var/lib/apt/lists/*; \
    fi \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out /opt/pni-swift-cache \
    && chown -R pni:pni /workspace /out /opt/pni-swift-cache \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

# Pre-resolve packages and pre-compile test targets; clear root-owned /tmp lock files for non-root Stage 2/3
RUN if [ -f Package.swift ]; then \
      swift package resolve || true; \
      swift build --build-tests || swift build || true; \
    fi \
    && rm -rf /tmp/_workspace_* /tmp/*.lock \
    && chown -R pni:pni /workspace /opt/pni-swift-cache \
    && chmod -R a+rwX /workspace /opt/pni-swift-cache /out

USER pni
CMD ["swift", "--version"]
