package com.pdfservice.pdf_service.adapters.inbound.rest.dto;

import com.pdfservice.pdf_service.domain.model.PdfJob;

public class JobStatusResponse {
    private String id;
    private String templateId;
    private String status;
    private String s3Url;
    private String errorMessage;
    private String createdAt;
    private String completedAt;

    public static JobStatusResponse fromDomain(PdfJob job) {
        JobStatusResponse response = new JobStatusResponse();
        response.setId(job.getId());
        response.setTemplateId(job.getTemplateId());
        response.setStatus(job.getStatus().name());
        response.setS3Url(job.getS3Url());
        response.setErrorMessage(job.getErrorMessage());
        response.setCreatedAt(job.getCreatedAt().toString());
        response.setCompletedAt(job.getCompletedAt() != null ? job.getCompletedAt().toString() : null);
        return response;
    }

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getTemplateId() { return templateId; }
    public void setTemplateId(String templateId) { this.templateId = templateId; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getS3Url() { return s3Url; }
    public void setS3Url(String s3Url) { this.s3Url = s3Url; }

    public String getErrorMessage() { return errorMessage; }
    public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }

    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }

    public String getCompletedAt() { return completedAt; }
    public void setCompletedAt(String completedAt) { this.completedAt = completedAt; }
}
