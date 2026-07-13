package com.pdfservice.pdf_service.adapters.outbound.storage;

import com.pdfservice.pdf_service.ports.outbound.FileStoragePort;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class LocalFileStorageAdapter implements FileStoragePort {
    private static final Logger log = LoggerFactory.getLogger(LocalFileStorageAdapter.class);
    private static final String STORAGE_DIR = "output-pdfs";

    @Override
    public String storeFile(String filename, byte[] content) throws Exception {
        Path targetDir = Paths.get(STORAGE_DIR).toAbsolutePath().normalize();
        if (!Files.exists(targetDir)) {
            Files.createDirectories(targetDir);
            log.info("Created local storage directory at: {}", targetDir);
        }

        Path targetFile = targetDir.resolve(filename);
        Files.write(targetFile, content);
        log.info("Stored file locally at: {}", targetFile);

        // Return a simulated S3 file URL
        return "s3://pdf-service-archive-bucket/pdfs/" + filename;
    }
}
