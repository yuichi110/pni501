FROM debian:bookworm-slim

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential cmake ninja-build pkg-config lcov ${EXTRA_APT_PACKAGES} \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out \
    && chown -R pni:pni /workspace /out \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

RUN if [ -f CMakeLists.txt ]; then \
      cmake -S . -B /workspace/build -DCMAKE_BUILD_TYPE=Debug || true; \
      cmake --build /workspace/build --parallel || true; \
    elif [ -f Makefile ] || [ -f GNUmakefile ]; then \
      make || true; \
    fi \
    && chown -R pni:pni /workspace \
    && chmod -R a+rwX /workspace /out

USER pni
CMD ["c++", "--version"]
