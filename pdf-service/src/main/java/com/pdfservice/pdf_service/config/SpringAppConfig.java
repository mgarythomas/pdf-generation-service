package com.pdfservice.pdf_service.config;

import com.pdfservice.pdf_service.domain.service.PdfJobDomainService;
import com.pdfservice.pdf_service.ports.outbound.FileStoragePort;
import com.pdfservice.pdf_service.ports.outbound.JobQueuePort;
import com.pdfservice.pdf_service.ports.outbound.JobRepositoryPort;
import com.pdfservice.pdf_service.ports.outbound.PdfGeneratorPort;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.concurrent.Executor;

@Configuration
@EnableAsync
public class SpringAppConfig {

    @Bean
    public PdfJobDomainService pdfJobDomainService(
            JobRepositoryPort repository,
            PdfGeneratorPort generator,
            FileStoragePort storage,
            JobQueuePort queue) {
        return new PdfJobDomainService(repository, generator, storage, queue);
    }

    @Bean(name = "pdfJobExecutor")
    public Executor pdfJobExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(15);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("PdfWorker-");
        executor.initialize();
        return executor;
    }
}
