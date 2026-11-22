ARG JAVA_VERSION=21
FROM groovy:4-jdk${JAVA_VERSION}

USER root
ENV GRADLE_USER_HOME=/gradle-cache

RUN mkdir -p /workspace /out /gradle-cache \
    && chmod 0777 /out

WORKDIR /workspace
COPY . /workspace

RUN chmod -R a+rwX /workspace /gradle-cache /out

USER groovy
CMD ["groovy", "--version"]
