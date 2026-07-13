package com.pdfservice.pdf_service.ports.inbound;

import com.pdfservice.pdf_service.domain.model.PdfJob;
import java.util.Optional;

public interface GetPdfJobUseCase {
    Optional<PdfJob> getJob(String jobId);
}
