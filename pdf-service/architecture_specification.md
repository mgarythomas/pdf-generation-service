# Architecture Specification: PDF Generation Service

This document defines the architecture and concrete technology decisions for the scalable, template-driven, regulatory-compliant PDF generation service deployed on AWS.

---

## 1. System Requirements & Decisions Summary

*   **API Interface**: Asynchronous REST API (via AWS API Gateway + SQS + Lambda/EKS).
*   **Scale**: ~150,000 PDFs per year. Decoupled async job processing handles traffic peaks at reporting periods.
*   **Document Size**: 1 to 100 pages, with a mean size of ~50 pages.
*   **Compliance**: Strict **PDF/A-2b compliance** for regulatory archiving (embedded fonts, output intents, color profile).
*   **Storage**: Generated PDFs are stored in AWS S3 with lifecycle transitions to Glacier after 90 days.
*   **Compute**: AWS Lambda (serverless container) or AWS EKS (Kubernetes) running containerized Java JRE workers.
*   **Build Tool**: **Gradle 9.x** (with Gradle wrapper).
*   **Language/Framework**: **Java 21 (Eclipse Temurin) + Spring Boot 4.1.0**.
*   **Architecture Pattern**: **Hexagonal Architecture (Ports and Adapters)**.
*   **PDF Generation Engine**: **iText 8 Core + pdfHTML + pdfa** (Commercial License).

---

## 2. Core Architectural Design (Hexagonal Ports & Adapters)

The application domain is entirely decoupled from external frameworks, libraries (Spring Boot, iText), and AWS API dependencies.

```
com.pdfservice.pdf_service
│
├── domain/                      # Core Business Logic (Framework & iText free)
│   ├── model/
│   │   ├── PdfJob.java          # Job aggregate (ID, Status, Targets, Timestamps)
│   │   └── PdfJobStatus.java    # Enum (PENDING, PROCESSING, COMPLETED, FAILED)
│   └── service/
│       └── PdfJobDomainService.java # Business workflow orchestration
│
├── ports/                       # Interfaces separating Domain from Infrastructure
│   ├── inbound/                 # Driving Ports (Called by REST Controller)
│   │   ├── CreatePdfJobUseCase.java
│   │   └── GetPdfJobUseCase.java
│   └── outbound/                # Driven Ports (SPIs implemented by Adapters)
│       ├── PdfGeneratorPort.java
│       ├── JobRepositoryPort.java
│       ├── FileStoragePort.java
│       └── JobQueuePort.java
│
├── adapters/                    # Concrete technology integrations
│   ├── inbound/                 # REST Controller Adapter (PdfJobController)
│   └── outbound/
│       ├── pdf/                 # iText 8 + pdfHTML rendering implementation
│       ├── persistence/         # InMemory / DB implementation
│       ├── queue/               # SQS / EventListener implementation
│       └── storage/             # S3 / Local storage implementation
│
└── config/                      # Dependency injection and thread-pool configuration
```

---

## 3. Technology Decisions

### A. PDF Generation: iText 8 + `pdfHTML` (HTML-to-PDF/A)
To ensure both **PDF/A-2b compliance** and a **Copilot-friendly template editing workflow** for developers and business users:
1.  **Templating**: HTML5 + CSS3 templates rendered via **Thymeleaf**. This lets AI coding assistants (like Copilot) easily modify layout elements (grids, tables) and support reusable layouts/snippets (header, footer, signature blocks).
2.  **Conversion**: iText's `pdfHTML` module parses resolved XHTML.
3.  **PDF/A Compliance**: iText's `pdfa` module compiles the parsed HTML into a tagged PDF/A-2b container, embedding:
    *   **Colorspace Output Intent**: Standard sRGB IEC61966-2.1 ICC profile (`sRGB Profile.icc` from macOS system profiles, 3144 bytes).
    *   **Font Program**: Standard TrueType Font program (`Arial.ttf`, 773KB) registered in the `FontProvider` to guarantee complete font embedding.

### B. Asynchronous Job Processing
Due to AWS API Gateway's 29-second timeout limit, all PDF generation tasks are processed asynchronously:
1.  **Ingestion**: `POST /v1/pdf-jobs` validates input JSON, creates a job in `PENDING` state, enqueues a job ID, and immediately returns `202 Accepted` status.
2.  **Buffering**: An SQS queue buffers traffic spikes and feeds worker pools.
3.  **Execution**: Worker threads process jobs, write output PDFs to S3, and update DynamoDB.
4.  *Prototype Implementation*: Modeled internally via Spring Application Events and an asynchronous `@EventListener` thread-pool (`pdfJobExecutor`) to mimic SQS and Lambda/EKS workers locally without infrastructure overhead.

---

## 4. CI/CD and Infrastructure

*   **GitLab CI/CD (`.gitlab-ci.yml`)**: Automates Gradle testing, compiles the container, pushes to AWS ECR, and executes Terraform validations.
*   **Docker Containerization (`Dockerfile`)**: Implements a secure multi-stage build:
    1.  *Builder*: `eclipse-temurin:21-jdk-alpine` executing `./gradlew bootJar`.
    2.  *Runner*: `eclipse-temurin:21-jre-alpine` running the thin JAR under a non-root group (`pdfgroup`/`pdfuser`) with max RAM configuration.
*   **Infrastructure as Code (Terraform)**:
    *   `eks.tf`: Sets up IAM Roles for Service Accounts (IRSA annotation) to run pod workers inside EKS.
    *   `lambda.tf`: Configures container-packaged serverless Lambda workers triggered by SQS.
    *   `sqs.tf` / `dynamodb.tf` / `s3.tf`: Defines message queues (DLQ), PAY_PER_REQUEST job stores, and S3 asset/archive buckets.
