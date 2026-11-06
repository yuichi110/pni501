FROM maven:3.9.9-eclipse-temurin-21 AS builder
WORKDIR /build
COPY pom.xml ./
COPY src ./src
RUN mvn -B -DskipTests package

FROM eclipse-temurin:21.0.4_7-jre-jammy
WORKDIR /app
RUN groupadd -r spring && useradd -r -g spring -u 10001 spring
COPY --from=builder /build/target/inventory-service-1.1.0.jar /app/app.jar
RUN chown -R spring:spring /app

USER spring
EXPOSE 8080
ENTRYPOINT ["java", "-Dserver.address=127.0.0.1", "-jar", "/app/app.jar"]
