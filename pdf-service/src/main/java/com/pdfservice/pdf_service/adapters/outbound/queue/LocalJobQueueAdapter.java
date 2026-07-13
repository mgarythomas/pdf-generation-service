package com.pdfservice.pdf_service.adapters.outbound.queue;

import com.pdfservice.pdf_service.domain.model.PdfJob;
import com.pdfservice.pdf_service.ports.outbound.JobQueuePort;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Component;

@Component
public class LocalJobQueueAdapter implements JobQueuePort {
    private final ApplicationEventPublisher eventPublisher;

    public LocalJobQueueAdapter(ApplicationEventPublisher eventPublisher) {
        this.eventPublisher = eventPublisher;
    }

    @Override
    public void enqueue(PdfJob job) {
        eventPublisher.publishEvent(new PdfJobEnqueuedEvent(job.getId()));
    }
}
