package com.pdfservice.pdf_service.ports.outbound;

import com.pdfservice.pdf_service.domain.model.PdfJob;

public interface JobQueuePort {
    void enqueue(PdfJob job);
}
