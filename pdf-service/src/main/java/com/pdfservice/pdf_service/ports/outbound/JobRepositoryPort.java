package com.pdfservice.pdf_service.ports.outbound;

import com.pdfservice.pdf_service.domain.model.PdfJob;
import java.util.Optional;

public interface JobRepositoryPort {
    PdfJob save(PdfJob job);
    Optional<PdfJob> findById(String id);
}
