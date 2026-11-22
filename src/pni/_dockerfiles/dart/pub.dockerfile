ARG DART_VERSION=stable
FROM dart:${DART_VERSION}

ENV PUB_CACHE="/opt/pub-cache"

RUN useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out /opt/pub-cache \
    && chown -R pni:pni /workspace /out /opt/pub-cache \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

# Pre-fetch Pub dependencies so Stage 2/3 can run cleanly with --network=none
RUN if [ -f pubspec.yaml ]; then \
      dart pub get || true; \
    fi \
    && chown -R pni:pni /workspace /opt/pub-cache \
    && chmod -R a+rwX /workspace /opt/pub-cache /out

USER pni
CMD ["dart", "--version"]
