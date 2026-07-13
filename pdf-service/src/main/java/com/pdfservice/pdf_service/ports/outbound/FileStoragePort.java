package com.pdfservice.pdf_service.ports.outbound;

public interface FileStoragePort {
    String storeFile(String filename, byte[] content) throws Exception;
}
