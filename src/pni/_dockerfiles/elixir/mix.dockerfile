ARG ELIXIR_VERSION=1.17
FROM elixir:${ELIXIR_VERSION}-slim

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive \
    MIX_HOME="/opt/mix" \
    HEX_HOME="/opt/hex" \
    MIX_ENV=test

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates git ${EXTRA_APT_PACKAGES} \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out /opt/mix /opt/hex \
    && mix local.hex --force \
    && mix local.rebar --force \
    && chown -R pni:pni /workspace /out /opt/mix /opt/hex \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

# Pre-fetch Hex dependencies and compile test environment so Stage 2/3 can run with --network=none
RUN if [ -f mix.exs ]; then \
      mix deps.get || true; \
      mix compile || true; \
    fi \
    && chown -R pni:pni /workspace /opt/mix /opt/hex \
    && chmod -R a+rwX /workspace /opt/mix /opt/hex /out

USER pni
CMD ["elixir", "--version"]
