ARG PHP_VERSION=8.3
FROM php:${PHP_VERSION}-cli-bookworm

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libsqlite3-dev ${EXTRA_APT_PACKAGES} \
    && docker-php-ext-install mysqli pdo_sqlite \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out \
    && chown -R pni:pni /workspace /out \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace
RUN chown -R pni:pni /workspace && chmod -R a+rwX /workspace

USER pni
CMD ["php", "-v"]
