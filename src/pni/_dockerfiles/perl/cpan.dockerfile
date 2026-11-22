ARG PERL_VERSION=5.40
FROM perl:${PERL_VERSION}-bookworm

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive \
    PERL5LIB="/opt/pni-perl/lib/perl5:/workspace/lib" \
    PATH="/opt/pni-perl/bin:$PATH"

RUN if [ -n "${EXTRA_APT_PACKAGES}" ]; then \
      apt-get update \
      && apt-get install -y --no-install-recommends ${EXTRA_APT_PACKAGES} \
      && rm -rf /var/lib/apt/lists/*; \
    fi \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out /opt/pni-perl \
    && chown -R pni:pni /workspace /out /opt/pni-perl \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

# Pre-install CPAN dependencies into /opt/pni-perl so Stage 2/3 can run with --network=none
RUN if [ -f cpanfile ] || [ -f Makefile.PL ] || [ -f Build.PL ]; then \
      cpanm --notest --local-lib=/opt/pni-perl --installdeps . || true; \
    fi \
    && chown -R pni:pni /workspace /opt/pni-perl \
    && chmod -R a+rwX /workspace /opt/pni-perl /out

USER pni
CMD ["perl", "-v"]
