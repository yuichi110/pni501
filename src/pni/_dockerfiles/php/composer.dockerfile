ARG PHP_VERSION=8.3
FROM composer:2 AS composer_bin
FROM php:${PHP_VERSION}-cli-bookworm

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive \
    COMPOSER_ALLOW_SUPERUSER=1 \
    COMPOSER_NO_INTERACTION=1 \
    PATH="/workspace/vendor/bin:/opt/pni-php/vendor/bin:$PATH"

COPY --from=composer_bin /usr/bin/composer /usr/bin/composer

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git unzip libzip-dev libsqlite3-dev ${EXTRA_APT_PACKAGES} \
    && docker-php-ext-install zip pdo_sqlite \
    && pecl install pcov \
    && docker-php-ext-enable pcov \
    && rm -rf /var/lib/apt/lists/* /tmp/pear \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out /opt/pni-php \
    && chown -R pni:pni /workspace /out /opt/pni-php \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

RUN if [ -f composer.json ]; then \
      composer install --no-interaction --no-progress --prefer-dist --no-scripts \
      || composer update --no-interaction --no-progress --prefer-dist --no-scripts \
      || true; \
      composer dump-autoload --optimize --no-scripts || true; \
    fi \
    && if [ ! -x /workspace/vendor/bin/phpunit ] && [ ! -x /workspace/vendor/bin/pest ]; then \
      composer --working-dir=/opt/pni-php require --no-interaction --no-progress phpunit/phpunit:^10.5 || true; \
    fi \
    && chown -R pni:pni /workspace /opt/pni-php \
    && chmod -R a+rwX /workspace /opt/pni-php

USER pni
CMD ["php", "-v"]
