ARG JAVA_VERSION=21
FROM maven:3.9-eclipse-temurin-${JAVA_VERSION}

ARG JACOCO_VERSION=0.8.12
ENV JACOCO_VERSION=${JACOCO_VERSION} \
    MAVEN_CONFIG="/tmp/.m2" \
    MAVEN_OPTS="-Dmaven.repo.local=/m2repo"

RUN useradd --uid 10001 --create-home --shell /bin/bash pni \
    && mkdir -p /workspace /out /m2repo \
    && chmod 0777 /out

WORKDIR /workspace
COPY . /workspace

RUN if [ -f pom.xml ]; then \
      mvn -B -Dmaven.repo.local=/m2repo \
        org.jacoco:jacoco-maven-plugin:${JACOCO_VERSION}:prepare-agent \
        test \
        -DfailIfNoTests=false \
        -Dmaven.test.failure.ignore=true \
        org.jacoco:jacoco-maven-plugin:${JACOCO_VERSION}:report || true; \
      rm -rf target/surefire-reports target/site target/jacoco.exec; \
    fi \
    && chown -R pni:pni /workspace /m2repo \
    && chmod -R a+rwX /workspace /m2repo /out

USER pni
CMD ["mvn", "-B", "-o", "-Dmaven.repo.local=/m2repo", "test"]
