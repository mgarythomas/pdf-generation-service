package com.pdfservice.pdf_service.adapters.inbound.rest;

import com.pdfservice.pdf_service.adapters.inbound.rest.dto.CreateJobRequest;
import com.pdfservice.pdf_service.adapters.inbound.rest.dto.JobStatusResponse;
import com.pdfservice.pdf_service.domain.model.PdfJob;
import com.pdfservice.pdf_service.ports.inbound.CreatePdfJobUseCase;
import com.pdfservice.pdf_service.ports.inbound.GetPdfJobUseCase;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import java.net.URI;

@RestController
@RequestMapping("/v1/pdf-jobs")
public class PdfJobController {

    private final CreatePdfJobUseCase createPdfJobUseCase;
    private final GetPdfJobUseCase getPdfJobUseCase;

    public PdfJobController(CreatePdfJobUseCase createPdfJobUseCase, GetPdfJobUseCase getPdfJobUseCase) {
        this.createPdfJobUseCase = createPdfJobUseCase;
        this.getPdfJobUseCase = getPdfJobUseCase;
    }

    @PostMapping
    public ResponseEntity<JobStatusResponse> createJob(@Valid @RequestBody CreateJobRequest request) {
        PdfJob job = createPdfJobUseCase.createJob(request.getTemplateId(), request.getPayload());
        
        URI location = ServletUriComponentsBuilder.fromCurrentRequest()
                .path("/{id}")
                .buildAndExpand(job.getId())
                .toUri();

        return ResponseEntity.accepted()
                .location(location)
                .body(JobStatusResponse.fromDomain(job));
    }

    @GetMapping("/{id}")
    public ResponseEntity<JobStatusResponse> getJob(@PathVariable String id) {
        return getPdfJobUseCase.getJob(id)
                .map(job -> ResponseEntity.ok(JobStatusResponse.fromDomain(job)))
                .orElse(ResponseEntity.notFound().build());
    }
}
