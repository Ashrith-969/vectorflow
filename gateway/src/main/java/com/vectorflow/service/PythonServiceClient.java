package com.vectorflow.service;

import com.vectorflow.model.dto.Metadata;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.util.List;
import java.util.Map;

@Service
@Slf4j
public class PythonServiceClient implements VectorSearchService {

    private final WebClient webClient;

    public PythonServiceClient(@Value("${app.python-service.url}") String pythonServiceUrl) {
        this.webClient = WebClient.builder()
                .baseUrl(pythonServiceUrl)
                .build();
    }

    @Override
    public IngestResult ingest(String title, String content, Metadata metadata) {
        Map<String, Object> request = Map.of(
                "title", title,
                "content", content,
                "metadata", metadata != null ? Map.of(
                        "category", metadata.getCategory() != null ? metadata.getCategory() : "",
                        "tags", metadata.getTags() != null ? metadata.getTags() : List.of()
                ) : Map.of()
        );

        return webClient.post()
                .uri("/api/ingest")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(IngestResult.class)
                .block();
    }

    @Override
    public BulkIngestResult bulkIngest(List<BulkIngestDocument> documents) {
        Map<String, Object> request = Map.of("documents", documents);

        return webClient.post()
                .uri("/api/bulk-ingest")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(BulkIngestResult.class)
                .block();
    }

    @Override
    @Cacheable(value = "searchResults", key = "#query + '_' + #limit")
    public SearchResponse search(String query, Integer limit, Map<String, Object> filters) {
        Map<String, Object> request = new java.util.HashMap<>();
        request.put("query", query);
        request.put("limit", limit != null ? limit : 5);

        if (filters != null && !filters.isEmpty()) {
            request.put("filters", filters);
        }

        log.debug("Searching with query: {}, limit: {}", query, limit);

        return webClient.post()
                .uri("/api/search")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(SearchResponse.class)
                .block();
    }

    @Override
    public AskResult ask(String question, Integer maxSources) {
        Map<String, Object> request = Map.of(
                "question", question,
                "max_sources", maxSources != null ? maxSources : 5
        );

        log.debug("Asking question: {}", question);

        return webClient.post()
                .uri("/api/ask")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(AskResult.class)
                .block();
    }

    @Override
    public DeleteResult deleteDocument(String documentId) {
        return webClient.delete()
                .uri("/api/documents/{id}", documentId)
                .retrieve()
                .bodyToMono(DeleteResult.class)
                .block();
    }

    @Override
    public VectorSearchService.DocumentListResult listDocuments(int page, int pageSize) {
        return webClient.get()
                .uri(uriBuilder -> uriBuilder
                        .path("/api/documents")
                        .queryParam("page", page)
                        .queryParam("page_size", pageSize)
                        .build())
                .retrieve()
                .bodyToMono(VectorSearchService.DocumentListResult.class)
                .block();
    }

    @Override
    public VectorSearchService.DocumentDetailResult getDocument(String documentId) {
        return webClient.get()
                .uri("/api/documents/{id}", documentId)
                .retrieve()
                .bodyToMono(VectorSearchService.DocumentDetailResult.class)
                .block();
    }

    @Override
    public boolean healthCheck() {
        try {
            webClient.get()
                    .uri("/health")
                    .retrieve()
                    .bodyToMono(Map.class)
                    .block();
            return true;
        } catch (Exception e) {
            log.error("Python service health check failed", e);
            return false;
        }
    }
}
