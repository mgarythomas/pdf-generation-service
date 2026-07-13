package com.pdfservice.pdf_service.adapters.outbound.queue;

import com.pdfservice.pdf_service.domain.service.PdfJobDomainService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.context.event.EventListener;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

@Component
public class JobEventListener {
    private static final Logger log = LoggerFactory.getLogger(JobEventListener.class);
    
    private final PdfJobDomainService pdfJobDomainService;

    public JobEventListener(PdfJobDomainService pdfJobDomainService) {
        this.pdfJobDomainService = pdfJobDomainService;
    }

    @Async("pdfJobExecutor")
    @EventListener
    public void handleJobEnqueued(PdfJobEnqueuedEvent event) {
        log.info("Received job event for ID: {}", event.getJobId());
        try {
            pdfJobDomainService.processJob(event.getJobId());
        } catch (Exception e) {
            log.error("Failed to process job {} from event: {}", event.getJobId(), e.getMessage(), e);
        }
    }
}
