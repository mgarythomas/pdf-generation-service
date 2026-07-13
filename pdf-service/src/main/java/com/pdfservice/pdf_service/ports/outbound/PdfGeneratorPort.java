package com.pdfservice.pdf_service.ports.outbound;

import java.util.Map;

public interface PdfGeneratorPort {
    byte[] generatePdf(String templateId, Map<String, Object> payload) throws Exception;
}
