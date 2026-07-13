# =========================================================================
# Stage 1: Build the JAR package
# =========================================================================
FROM eclipse-temurin:21-jdk-alpine AS builder
WORKDIR /app

# Copy gradle files and download dependencies (cached layer)
COPY gradle gradle
COPY gradlew build.gradle settings.gradle ./
RUN chmod +x gradlew && ./gradlew dependencies --no-daemon

# Copy source code and build package (skipping tests for container compilation step)
COPY src ./src
RUN ./gradlew bootJar -x test --no-daemon

# =========================================================================
# Stage 2: Final Runtime Image
# =========================================================================
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

# Run as non-root user for security compliance
RUN addgroup -S pdfgroup && adduser -S pdfuser -G pdfgroup
USER pdfuser

# Copy built artifact from builder stage (Gradle target is build/libs/)
COPY --from=builder /app/build/libs/pdf-service-0.0.1-SNAPSHOT.jar pdf-service.jar

# Expose HTTP port
EXPOSE 8080

# Configure JVM flags for container optimization
ENV JAVA_OPTS="-XX:+UseG1GC -XX:+UseStringDeduplication -XX:MaxRAMPercentage=75.0"

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar pdf-service.jar"]
