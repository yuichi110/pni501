ARG JULIA_VERSION=1.11
FROM julia:${JULIA_VERSION}-bookworm

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive \
    JULIA_DEPOT_PATH="/opt/julia-depot"

RUN if [ -n "${EXTRA_APT_PACKAGES}" ]; then \
      apt-get update \
      && apt-get install -y --no-install-recommends ${EXTRA_APT_PACKAGES} \
      && rm -rf /var/lib/apt/lists/*; \
    fi \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out /opt/julia-depot \
    && chown -R pni:pni /workspace /out /opt/julia-depot \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

RUN if [ -f Project.toml ]; then \
      julia --project=. -e 'using Pkg; try Pkg.instantiate() catch end' || true; \
    fi \
    && chown -R pni:pni /workspace /opt/julia-depot \
    && chmod -R a+rwX /workspace /opt/julia-depot /out

USER pni
CMD ["julia", "--version"]
