package com.pdfservice.pdf_service.domain.model;

import java.time.LocalDateTime;
import java.util.Map;

public class PdfJob {
    private final String id;
    private final String templateId;
    private final Map<String, Object> payload;
    private PdfJobStatus status;
    private String s3Url;
    private String errorMessage;
    private final LocalDateTime createdAt;
    private LocalDateTime completedAt;

    public PdfJob(String id, String templateId, Map<String, Object> payload) {
        this.id = id;
        this.templateId = templateId;
        this.payload = payload;
        this.status = PdfJobStatus.PENDING;
        this.createdAt = LocalDateTime.now();
    }

    public PdfJob(String id, String templateId, Map<String, Object> payload, PdfJobStatus status,
                  String s3Url, String errorMessage, LocalDateTime createdAt, LocalDateTime completedAt) {
        this.id = id;
        this.templateId = templateId;
        this.payload = payload;
        this.status = status;
        this.s3Url = s3Url;
        this.errorMessage = errorMessage;
        this.createdAt = createdAt;
        this.completedAt = completedAt;
    }

    public void startProcessing() {
        if (this.status != PdfJobStatus.PENDING) {
            throw new IllegalStateException("Job can only be started from PENDING state. Current state: " + this.status);
        }
        this.status = PdfJobStatus.PROCESSING;
    }

    public void complete(String s3Url) {
        if (this.status != PdfJobStatus.PROCESSING) {
            throw new IllegalStateException("Job can only be completed from PROCESSING state. Current state: " + this.status);
        }
        this.status = PdfJobStatus.COMPLETED;
        this.s3Url = s3Url;
        this.completedAt = LocalDateTime.now();
    }

    public void fail(String errorMessage) {
        this.status = PdfJobStatus.FAILED;
        this.errorMessage = errorMessage;
        this.completedAt = LocalDateTime.now();
    }

    // Getters
    public String getId() { return id; }
    public String getTemplateId() { return templateId; }
    public Map<String, Object> getPayload() { return payload; }
    public PdfJobStatus getStatus() { return status; }
    public String getS3Url() { return s3Url; }
    public String getErrorMessage() { return errorMessage; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getCompletedAt() { return completedAt; }
}
