package com.pdfservice.pdf_service.adapters.outbound.queue;

public class PdfJobEnqueuedEvent {
    private final String jobId;

    public PdfJobEnqueuedEvent(String jobId) {
        this.jobId = jobId;
    }

    public String getJobId() {
        return jobId;
    }
}
