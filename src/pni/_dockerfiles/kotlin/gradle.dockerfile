ARG JAVA_VERSION=21
FROM gradle:8.10-jdk${JAVA_VERSION}

USER root
ENV GRADLE_USER_HOME=/gradle-cache

RUN mkdir -p /workspace /out /gradle-cache /opt/pni \
    && printf '%s\n' \
       'allprojects {' \
       '  apply plugin: "jacoco"' \
       '  tasks.matching { it.name == "jacocoTestReport" }.configureEach {' \
       '    reports { xml.required = true }' \
       '  }' \
       '}' > /opt/pni/jacoco.init.gradle \
    && chmod 0777 /out

WORKDIR /workspace
COPY . /workspace

# Pre-warm Kotlin/Gradle test runtime and JaCoCo plugin caches so Stage 2/3 can run with --network=none
RUN if [ -f build.gradle ] || [ -f build.gradle.kts ]; then \
      gradle --no-daemon -g /gradle-cache -I /opt/pni/jacoco.init.gradle test jacocoTestReport --continue \
      || gradle --no-daemon -g /gradle-cache -I /opt/pni/jacoco.init.gradle testClasses \
      || true; \
      rm -rf build/test-results build/reports/jacoco /gradle-cache/daemon; \
    fi \
    && rm -rf /gradle-cache/daemon \
    && chmod -R a+rwX /workspace /gradle-cache /opt/pni /out

USER gradle
CMD ["gradle", "--version"]
