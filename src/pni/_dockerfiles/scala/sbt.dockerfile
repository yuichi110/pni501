ARG JAVA_VERSION=21
FROM eclipse-temurin:${JAVA_VERSION}-jdk-jammy

ARG SBT_VERSION=1.10.7
ARG EXTRA_APT_PACKAGES=""
ENV DEBIAN_FRONTEND=noninteractive \
    SBT_GLOBAL_BASE="/opt/sbt-cache/global" \
    COURSIER_CACHE="/opt/sbt-cache/coursier" \
    IVY_HOME="/opt/sbt-cache/ivy2" \
    SBT_OPTS="-Dsbt.server.autostart=false -Dsbt.ivy.home=/opt/sbt-cache/ivy2 -Divy.home=/opt/sbt-cache/ivy2 -Dcoursier.cache=/opt/sbt-cache/coursier -Dsbt.global.base=/opt/sbt-cache/global -Dsbt.boot.directory=/opt/sbt-cache/boot -Xmx1536m"

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates ${EXTRA_APT_PACKAGES} \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/sbt /opt/sbt-cache/global /opt/sbt-cache/coursier /opt/sbt-cache/ivy2 /opt/sbt-cache/boot \
    && curl -fsSL "https://github.com/sbt/sbt/releases/download/v${SBT_VERSION}/sbt-${SBT_VERSION}.tgz" \
       | tar -xz --strip-components=1 -C /opt/sbt \
    && ln -s /opt/sbt/bin/sbt /usr/local/bin/sbt \
    && useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out \
    && chown -R pni:pni /workspace /out /opt/sbt-cache \
    && chmod 0777 /out

WORKDIR /workspace
COPY --chown=pni:pni . /workspace

# Pre-warm sbt launcher, Scala compiler, and test runtime classpath so Stage 2/3 can run with --network=none
RUN if [ -f build.sbt ]; then \
      sbt --batch -Dsbt.server.autostart=false test || sbt --batch -Dsbt.server.autostart=false Test/compile || true; \
      rm -rf target project/target /tmp/.sbt*; \
    fi \
    && chown -R pni:pni /workspace /opt/sbt-cache \
    && chmod -R a+rwX /workspace /opt/sbt-cache /out

USER pni
CMD ["sbt", "--version"]
