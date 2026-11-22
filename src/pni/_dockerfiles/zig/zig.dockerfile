FROM alpine:3.21

ENV ZIG_GLOBAL_CACHE_DIR="/opt/zig-cache" \
    ZIG_LOCAL_CACHE_DIR="/tmp/zig-local-cache"

RUN apk add --no-cache zig bash \
    && adduser -D -u 10001 pni \
    && mkdir -p /workspace /out /opt/zig-cache \
    && chown -R pni:pni /workspace /out /opt/zig-cache \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

RUN chown -R pni:pni /workspace /opt/zig-cache \
    && chmod -R a+rwX /workspace /opt/zig-cache /out

USER pni
CMD ["zig", "version"]
