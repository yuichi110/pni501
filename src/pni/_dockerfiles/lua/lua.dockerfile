FROM debian:bookworm-slim

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       lua5.4 ${EXTRA_APT_PACKAGES} \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out \
    && chown -R pni:pni /workspace /out \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

RUN chown -R pni:pni /workspace \
    && chmod -R a+rwX /workspace /out

USER pni
CMD ["lua5.4", "-v"]
