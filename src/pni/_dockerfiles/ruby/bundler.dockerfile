ARG RUBY_VERSION=3.3
FROM ruby:${RUBY_VERSION}-bookworm

ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive \
    BUNDLE_PATH="/opt/pni-bundle" \
    GEM_HOME="/opt/pni-gems" \
    PATH="/opt/pni-bundle/bin:/opt/pni-gems/bin:$PATH"

RUN if [ -n "${EXTRA_APT_PACKAGES}" ]; then \
      apt-get update \
      && apt-get install -y --no-install-recommends ${EXTRA_APT_PACKAGES} \
      && rm -rf /var/lib/apt/lists/*; \
    fi \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out /opt/pni-bundle /opt/pni-gems \
    && gem install --no-document rspec minitest \
    && chown -R pni:pni /workspace /out /opt/pni-bundle /opt/pni-gems \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

# Install Gemfile dependencies during image build so Stage 2/3 can execute with --network=none
RUN if [ -f Gemfile ]; then \
      bundle config set --local path /opt/pni-bundle || true; \
      bundle install --jobs=4 --retry=2 || true; \
    fi \
    && chown -R pni:pni /workspace /opt/pni-bundle /opt/pni-gems \
    && chmod -R a+rwX /workspace /opt/pni-bundle /opt/pni-gems /out

USER pni
CMD ["ruby", "-v"]
