package com.pdfservice.pdf_service.adapters.outbound.persistence;

import com.pdfservice.pdf_service.domain.model.PdfJob;
import com.pdfservice.pdf_service.ports.outbound.JobRepositoryPort;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.stereotype.Repository;

@Repository
public class InMemoryJobRepositoryAdapter implements JobRepositoryPort {
    private final Map<String, PdfJob> db = new ConcurrentHashMap<>();

    @Override
    public PdfJob save(PdfJob job) {
        db.put(job.getId(), job);
        return job;
    }

    @Override
    public Optional<PdfJob> findById(String id) {
        return Optional.ofNullable(db.get(id));
    }
}
