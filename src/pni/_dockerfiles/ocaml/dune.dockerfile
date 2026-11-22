FROM debian:bookworm-slim

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ocaml ocaml-dune ${EXTRA_APT_PACKAGES} \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out \
    && chown -R pni:pni /workspace /out \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

RUN if [ -f dune-project ] && find . -maxdepth 3 -name 'dune' | grep -q .; then \
      dune build || true; \
    fi \
    && chown -R pni:pni /workspace \
    && chmod -R a+rwX /workspace /out

USER pni
CMD ["ocamlc", "-version"]
