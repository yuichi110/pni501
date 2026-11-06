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

RUN gradle --no-daemon -I /opt/pni/jacoco.init.gradle testClasses \
    && chmod -R a+rwX /workspace /gradle-cache /opt/pni /out

USER gradle
CMD ["gradle", "--no-daemon", "--offline", "-I", "/opt/pni/jacoco.init.gradle", "test", "jacocoTestReport"]
