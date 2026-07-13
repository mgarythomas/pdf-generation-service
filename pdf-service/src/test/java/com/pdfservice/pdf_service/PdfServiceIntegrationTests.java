package com.pdfservice.pdf_service;

import tools.jackson.databind.ObjectMapper;
import com.itextpdf.kernel.pdf.PdfArray;
import com.itextpdf.kernel.pdf.PdfDictionary;
import com.itextpdf.kernel.pdf.PdfDocument;
import com.itextpdf.kernel.pdf.PdfName;
import com.itextpdf.kernel.pdf.PdfReader;
import com.pdfservice.pdf_service.adapters.inbound.rest.dto.CreateJobRequest;
import com.pdfservice.pdf_service.adapters.inbound.rest.dto.JobStatusResponse;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.io.File;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
public class PdfServiceIntegrationTests {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    public void testFullPdfGenerationLifecycle() throws Exception {
        // 1. Create a request payload matching our Thymeleaf model
        Map<String, Object> payload = new HashMap<>();
        payload.put("organizationName", "Test Corp");
        payload.put("reportingPeriod", "Q2 2026");
        payload.put("assessorName", "Jane Assessor");
        payload.put("overallScore", 95);
        payload.put("requiresFiling", true);
        payload.put("filingRationale", "Critical infractions found in the test system.");

        // Compliance checks list
        Map<String, String> check1 = new HashMap<>();
        check1.put("systemName", "Access Control");
        check1.put("auditDate", "2026-07-01");
        check1.put("observations", "Passed all security tests.");
        check1.put("result", "PASSED");

        Map<String, String> check2 = new HashMap<>();
        check2.put("systemName", "Database Encryption");
        check2.put("auditDate", "2026-07-02");
        check2.put("observations", "No issues identified.");
        check2.put("result", "PASSED");

        payload.put("complianceChecks", List.of(check1, check2));

        CreateJobRequest request = new CreateJobRequest();
        request.setTemplateId("regulatory-compliance-report");
        request.setPayload(payload);

        // 2. Submit the job (POST /v1/pdf-jobs)
        MvcResult postResult = mockMvc.perform(post("/v1/pdf-jobs")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isAccepted())
                .andReturn();

        String postResponseString = postResult.getResponse().getContentAsString();
        JobStatusResponse postResponse = objectMapper.readValue(postResponseString, JobStatusResponse.class);
        assertThat(postResponse.getId()).isNotNull();
        assertThat(postResponse.getStatus()).isIn("PENDING", "PROCESSING");

        // 3. Poll GET /v1/pdf-jobs/{id} until it transitions to COMPLETED (or fails)
        String jobId = postResponse.getId();
        JobStatusResponse pollResponse = null;
        int maxRetries = 15;
        int retryIntervalMs = 500;

        for (int i = 0; i < maxRetries; i++) {
            Thread.sleep(retryIntervalMs);
            MvcResult getResult = mockMvc.perform(get("/v1/pdf-jobs/" + jobId))
                    .andExpect(status().isOk())
                    .andReturn();

            String getResponseString = getResult.getResponse().getContentAsString();
            pollResponse = objectMapper.readValue(getResponseString, JobStatusResponse.class);
            if (!"PENDING".equals(pollResponse.getStatus()) && !"PROCESSING".equals(pollResponse.getStatus())) {
                break;
            }
        }

        // Verify it finished successfully
        assertThat(pollResponse).isNotNull();
        assertThat(pollResponse.getStatus()).isEqualTo("COMPLETED");
        assertThat(pollResponse.getS3Url()).startsWith("s3://");

        // 4. Verify local file exists in output-pdfs directory
        String expectedFilename = "output-pdfs/regulatory-" + jobId + ".pdf";
        File generatedFile = new File(expectedFilename);
        assertThat(generatedFile.exists()).isTrue();

        // 5. Parse output PDF via iText 8 and verify conformance characteristics
        try (PdfReader reader = new PdfReader(generatedFile);
             PdfDocument pdfDoc = new PdfDocument(reader)) {
            
            // Check if tagged (PDF/A requirement)
            assertThat(pdfDoc.isTagged()).isTrue();
            
            // Validate it has output intents in the catalog dictionary
            PdfDictionary catalog = pdfDoc.getCatalog().getPdfObject();
            PdfArray outputIntents = catalog.getAsArray(PdfName.OutputIntents);
            assertThat(outputIntents).isNotNull();
            assertThat(outputIntents.size()).isGreaterThan(0);
        }
    }
}
