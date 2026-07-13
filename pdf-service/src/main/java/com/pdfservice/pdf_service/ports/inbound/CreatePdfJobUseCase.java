package com.pdfservice.pdf_service.ports.inbound;

import com.pdfservice.pdf_service.domain.model.PdfJob;
import java.util.Map;

public interface CreatePdfJobUseCase {
    PdfJob createJob(String templateId, Map<String, Object> payload);
}
