ARG PHP_VERSION=8.3
FROM php:${PHP_VERSION}-cli-bookworm

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libsqlite3-dev ${EXTRA_APT_PACKAGES} \
    && docker-php-ext-install mysqli pdo_sqlite \
    && printf '<?php\nif (function_exists("mysqli_report")) { mysqli_report(MYSQLI_REPORT_OFF); }\n' > /opt/pni-compat.php \
    && printf 'auto_prepend_file=/opt/pni-compat.php\n' > /usr/local/etc/php/conf.d/99-pni-compat.ini \
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
