package com.pdfservice.pdf_service.adapters.outbound.pdf;

import com.itextpdf.html2pdf.ConverterProperties;
import com.itextpdf.html2pdf.HtmlConverter;
import com.itextpdf.kernel.pdf.*;
import com.itextpdf.layout.font.FontProvider;
import com.itextpdf.pdfa.PdfADocument;
import com.pdfservice.pdf_service.ports.outbound.PdfGeneratorPort;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;
import org.thymeleaf.TemplateEngine;
import org.thymeleaf.context.Context;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.Map;

@Component
public class ItextPdfGeneratorAdapter implements PdfGeneratorPort {

    private final TemplateEngine templateEngine;

    public ItextPdfGeneratorAdapter(TemplateEngine templateEngine) {
        this.templateEngine = templateEngine;
    }

    @Override
    public byte[] generatePdf(String templateId, Map<String, Object> payload) throws Exception {
        // 1. Process Thymeleaf HTML Template
        Context context = new Context();
        if (payload != null) {
            context.setVariables(payload);
        }
        // Map templateId to form templates, e.g., "forms/form-1"
        String templatePath = "forms/" + templateId;
        String htmlContent = templateEngine.process(templatePath, context);

        // 2. Set up PDF/A Output Stream
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        
        // Load ICC Profile from Resources
        byte[] iccBytes;
        try (InputStream is = new ClassPathResource("profiles/sRGB-v2.icc").getInputStream()) {
            iccBytes = is.readAllBytes();
        }
        
        // Initialize PDF/A writer and document
        PdfWriter writer = new PdfWriter(baos);
        
        // PDF/A-2b conformance level
        PdfADocument pdf = new PdfADocument(
            writer,
            PdfAConformanceLevel.PDF_A_2B,
            new PdfOutputIntent(
                "Custom", 
                "", 
                "http://www.color.org", 
                "sRGB IEC61966-2.1", 
                new ByteArrayInputStream(iccBytes)
            )
        );

        // Required for PDF/A
        pdf.setTagged();

        // 3. Configure Converter Properties (Font Embedding)
        ConverterProperties properties = new ConverterProperties();
        FontProvider fontProvider = new FontProvider();
        
        // Load Font from Resources
        byte[] fontBytes;
        try (InputStream is = new ClassPathResource("fonts/LiberationSans-Regular.ttf").getInputStream()) {
            fontBytes = is.readAllBytes();
        }
        
        // Add font program to provider
        fontProvider.addFont(fontBytes);
        properties.setFontProvider(fontProvider);

        // Convert HTML string to PDF
        HtmlConverter.convertToPdf(htmlContent, pdf, properties);
        
        // Close document
        pdf.close();

        return baos.toByteArray();
    }
}
