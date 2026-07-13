package com.pdfservice.pdf_service.adapters.inbound.rest.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.util.Map;

public class CreateJobRequest {
    @NotBlank(message = "templateId is required")
    private String templateId;

    @NotNull(message = "payload is required")
    private Map<String, Object> payload;

    // Getters and Setters
    public String getTemplateId() { return templateId; }
    public void setTemplateId(String templateId) { this.templateId = templateId; }
    
    public Map<String, Object> getPayload() { return payload; }
    public void setPayload(Map<String, Object> payload) { this.payload = payload; }
}
