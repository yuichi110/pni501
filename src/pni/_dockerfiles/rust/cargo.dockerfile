ARG RUST_VERSION=1.85
FROM rust:${RUST_VERSION}-bookworm

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive \
    CARGO_HOME="/cargo" \
    CARGO_TARGET_DIR="/cargo-target" \
    RUST_BACKTRACE=1

RUN if [ -n "${EXTRA_APT_PACKAGES}" ]; then \
      apt-get update \
      && apt-get install -y --no-install-recommends ${EXTRA_APT_PACKAGES} \
      && rm -rf /var/lib/apt/lists/*; \
    fi \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out /cargo /cargo-target \
    && chown -R pni:pni /workspace /out /cargo /cargo-target \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

# Pre-download crates and warm test compilation cache so Stage 2/3 can run with --network=none
RUN if [ -f Cargo.toml ]; then \
      cargo fetch || true; \
      cargo test --no-run || cargo check --tests || true; \
    fi \
    && chown -R pni:pni /workspace /cargo /cargo-target \
    && chmod -R a+rwX /workspace /cargo /cargo-target /out

USER pni
CMD ["cargo", "--version"]
