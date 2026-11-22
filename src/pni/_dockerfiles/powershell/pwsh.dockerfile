ARG PWSH_VERSION=7.4
FROM mcr.microsoft.com/powershell:${PWSH_VERSION}-debian-12

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive \
    POWERSHELL_TELEMETRY_OPTOUT=1

RUN if [ -n "${EXTRA_APT_PACKAGES}" ]; then \
      apt-get update \
      && apt-get install -y --no-install-recommends ${EXTRA_APT_PACKAGES} \
      && rm -rf /var/lib/apt/lists/*; \
    fi \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out \
    && chown -R pni:pni /workspace /out \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

RUN chown -R pni:pni /workspace \
    && chmod -R a+rwX /workspace /out

USER pni
CMD ["pwsh", "--version"]
