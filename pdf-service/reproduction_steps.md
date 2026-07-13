# Reproduction Steps: PDF Generation Service

This guide provides the exact step-by-step process to reproduce this Hexagonal Architecture, containerized Java PDF/A generation service using **Gradle** and **iText 8**.

---

## Prerequisites
*   Java Development Kit (JDK) 21 (e.g. Eclipse Temurin 21)
*   Gradle 9.x (included via gradle wrapper)
*   Docker (for container builds)

---

## Step 1: Bootstrap the Project Structure

Create the project base directory and fetch the Spring Boot Gradle bootstrap config:

```bash
mkdir -p pdf-service && cd pdf-service

# Download Spring Initializr project zip (targeting Gradle, Java 21, Web, Validation, Actuator)
curl -o starter.zip https://start.spring.io/starter.zip \
  -d dependencies=web,validation,actuator \
  -d type=gradle-project \
  -d javaVersion=21 \
  -d groupId=com.pdfservice \
  -d artifactId=pdf-service \
  -d name=pdf-service \
  -d baseDir=.

unzip starter.zip && rm starter.zip
```

---

## Step 2: Configure Dependencies (`build.gradle`)

Replace the default `dependencies` block in `build.gradle` to pull in Thymeleaf and iText 8 core modules (`html2pdf` and `pdfa`):

```groovy
dependencies {
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-thymeleaf'
    implementation 'org.springframework.boot:spring-boot-starter-validation'
    implementation 'org.springframework.boot:spring-boot-starter-actuator'

    // iText 8 PDF/A & HTML-to-PDF
    implementation 'com.itextpdf:html2pdf:5.0.5'
    implementation 'com.itextpdf:pdfa:8.0.5'

    testImplementation 'org.springframework.boot:spring-boot-starter-test'
    testImplementation 'org.springframework.boot:spring-boot-starter-webmvc-test'
    testImplementation 'org.springframework.boot:spring-boot-starter-validation-test'
    testRuntimeOnly 'org.junit.platform:junit-platform-launcher'
}
```

---

## Step 3: Bundle Compliance Assets (Fonts & ICC Profile)

PDF/A-2b compliance mandates embedded fonts and colorspaces. Retrieve and package these files under `src/main/resources`:

```bash
mkdir -p src/main/resources/profiles src/main/resources/fonts

# Copy the standard sRGB ICC profile from macOS System Profiles
cp "/System/Library/ColorSync/Profiles/sRGB Profile.icc" src/main/resources/profiles/sRGB-v2.icc

# Copy the standard Arial TrueType font from macOS Supplemental Fonts
cp /System/Library/Fonts/Supplemental/Arial.ttf src/main/resources/fonts/LiberationSans-Regular.ttf
```

---

## Step 4: Create package directory structure

Under `src/main/java/com/pdfservice/pdf_service`, create the subpackages for Hexagonal Architecture:

```bash
cd src/main/java/com/pdfservice/pdf_service
mkdir -p domain/model domain/service ports/inbound ports/outbound adapters/inbound/rest/dto adapters/outbound/pdf adapters/outbound/persistence adapters/outbound/queue adapters/outbound/storage config
```

---

## Step 5: Implement Domain Model and Use Case Ports

1.  **`domain/model/PdfJobStatus.java`**: Define states: `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`.
2.  **`domain/model/PdfJob.java`**: Define state machine (methods like `startProcessing()`, `complete(s3Url)`, `fail(errorMessage)`).
3.  **`ports/inbound/CreatePdfJobUseCase.java`** and **`GetPdfJobUseCase.java`**: Interfaces for Rest entrypoints.
4.  **`ports/outbound/`**: Define SPIs: `PdfGeneratorPort`, `JobRepositoryPort`, `FileStoragePort`, and `JobQueuePort`.

---

## Step 6: Implement Infrastructure Adapters

1.  **`adapters/outbound/pdf/ItextPdfGeneratorAdapter.java`**:
    *   Injects Thymeleaf `TemplateEngine`.
    *   Initializes `PdfADocument` using `PdfAConformanceLevel.PDF_A_2B`.
    *   Loads ICC profile via `ClassPathResource("profiles/sRGB-v2.icc")` as a `PdfOutputIntent`.
    *   Configures `ConverterProperties` with `FontProvider` containing `LiberationSans-Regular.ttf`.
    *   Calls `HtmlConverter.convertToPdf()`.
2.  **`adapters/outbound/queue/`**:
    *   `LocalJobQueueAdapter.java` publishes a `PdfJobEnqueuedEvent`.
    *   `JobEventListener.java` listens to `PdfJobEnqueuedEvent` and executes `pdfJobDomainService.processJob(jobId)` inside a thread pool (`@Async("pdfJobExecutor")`).
3.  **`adapters/outbound/persistence/InMemoryJobRepositoryAdapter.java`**: Standard local map persistence.
4.  **`adapters/outbound/storage/LocalFileStorageAdapter.java`**: Writes files locally under `output-pdfs/`.
5.  **`adapters/inbound/rest/PdfJobController.java`**: REST controller receiving HTTP POST, enqueuing, and returning `202 Accepted` status.

---

## Step 7: Configure Dependency Injection & Thread Pools

Define beans in **`config/SpringAppConfig.java`**:
*   Annotated with `@EnableAsync`.
*   Instantiates `PdfJobDomainService` with outbound ports.
*   Exposes a task executor bean named `"pdfJobExecutor"` with set thread pool constraints.

---

## Step 8: Build the Thymeleaf Templates

Create files under `src/main/resources/templates`:
*   `snippets/header.html` / `snippets/footer.html` / `snippets/signature.html`: Contains visual blocks.
*   `forms/regulatory-compliance-report.html`: Main PDF document styling containing layout CSS, `th:each` loops for compliance checks, and structural tables.

---

## Step 9: Configure CI/CD and Containerization

1.  **`Dockerfile`**: Set up a multi-stage compilation:
    *   *Builder stage*: Runs `./gradlew bootJar -x test` on Java 21 JDK.
    *   *Runtime stage*: Runs JRE Alpine image under non-root permissions.
2.  **`.gitlab-ci.yml`**: Configure `test`, `build`, and `terraform` validation jobs.

---

## Step 10: Place IaC Templates (`terraform/`)

Create configurations inside `terraform/` folder:
*   `main.tf` / `variables.tf`: S3 bucket allocations (Assets/Archive).
*   `sqs.tf`: Buffering queues and Dead Letter Queue.
*   `dynamodb.tf`: pay-per-request job state storage.
*   `lambda.tf` / `eks.tf`: Docker-packaged Lambda configuration and EKS IAM role mappings (IRSA).

---

## Step 11: Execute & Verify

Verify the integration tests by running:

```bash
chmod +x gradlew
./gradlew test
```

Inspect generated compliant documents locally inside the `output-pdfs/` directory.
