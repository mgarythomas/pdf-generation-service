package com.pdfservice.pdf_service.domain.service;

import com.pdfservice.pdf_service.domain.model.PdfJob;
import com.pdfservice.pdf_service.domain.model.PdfJobStatus;
import com.pdfservice.pdf_service.ports.inbound.CreatePdfJobUseCase;
import com.pdfservice.pdf_service.ports.inbound.GetPdfJobUseCase;
import com.pdfservice.pdf_service.ports.outbound.*;

import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PdfJobDomainService implements CreatePdfJobUseCase, GetPdfJobUseCase {
    private static final Logger log = LoggerFactory.getLogger(PdfJobDomainService.class);

    private final JobRepositoryPort repository;
    private final PdfGeneratorPort generator;
    private final FileStoragePort storage;
    private final JobQueuePort queue;

    public PdfJobDomainService(JobRepositoryPort repository, PdfGeneratorPort generator,
                               FileStoragePort storage, JobQueuePort queue) {
        this.repository = repository;
        this.generator = generator;
        this.storage = storage;
        this.queue = queue;
    }

    @Override
    public PdfJob createJob(String templateId, Map<String, Object> payload) {
        String jobId = UUID.randomUUID().toString();
        PdfJob job = new PdfJob(jobId, templateId, payload);
        repository.save(job);
        queue.enqueue(job);
        log.info("Job {} enqueued for template {}", jobId, templateId);
        return job;
    }

    @Override
    public Optional<PdfJob> getJob(String jobId) {
        return repository.findById(jobId);
    }

    public void processJob(String jobId) {
        log.info("Starting processing for job {}", jobId);
        Optional<PdfJob> jobOpt = repository.findById(jobId);
        if (jobOpt.isEmpty()) {
            log.error("Job {} not found for processing", jobId);
            return;
        }

        PdfJob job = jobOpt.get();
        try {
            job.startProcessing();
            repository.save(job);

            // 1. Render PDF using Generator Port
            byte[] pdfBytes = generator.generatePdf(job.getTemplateId(), job.getPayload());

            // 2. Save PDF to S3/Local Storage using Storage Port
            String filename = "regulatory-" + job.getId() + ".pdf";
            String s3Url = storage.storeFile(filename, pdfBytes);

            // 3. Mark completed
            job.complete(s3Url);
            repository.save(job);
            log.info("Job {} completed successfully. Saved to {}", jobId, s3Url);
        } catch (Exception e) {
            log.error("Job {} failed during execution: {}", jobId, e.getMessage(), e);
            job.fail(e.getMessage());
            repository.save(job);
        }
    }
}
