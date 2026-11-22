ARG R_VERSION=4.4.2
FROM r-base:${R_VERSION}

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive \
    R_LIBS_USER="/opt/pni-r-libs"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       r-cran-testthat ${EXTRA_APT_PACKAGES} \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out /opt/pni-r-libs \
    && chown -R pni:pni /workspace /out /opt/pni-r-libs \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

RUN chown -R pni:pni /workspace /opt/pni-r-libs \
    && chmod -R a+rwX /workspace /opt/pni-r-libs /out

USER pni
CMD ["Rscript", "--version"]
