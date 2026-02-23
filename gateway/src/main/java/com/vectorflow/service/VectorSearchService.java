package com.vectorflow.service;

import com.vectorflow.model.dto.Metadata;

import java.io.Serializable;
import java.util.List;
import java.util.Map;

/**
 * Contract for vector search operations delegated to the AI/ML backend.
 * Implementations may call a remote service (e.g. PythonServiceClient)
 * or be stubbed for testing.
 */
public interface VectorSearchService {

    IngestResult ingest(String title, String content, Metadata metadata);

    BulkIngestResult bulkIngest(List<BulkIngestDocument> documents);

    SearchResponse search(String query, Integer limit, Map<String, Object> filters);

    AskResult ask(String question, Integer maxSources);

    DeleteResult deleteDocument(String documentId);

    boolean healthCheck();

    // Response DTOs shared across implementations
    record IngestResult(
            String document_id,
            String title,
            Integer chunk_count,
            String status,
            String message
    ) implements Serializable {}

    record SearchResponse(
            List<SearchResultDto> results,
            Integer total_count,
            String query
    ) implements Serializable {}

    record SearchResultDto(
            String id,
            String document_id,
            String title,
            String snippet,
            Double score,
            Map<String, Object> metadata
    ) implements Serializable {}

    record AskResult(
            String answer,
            List<SourceDto> sources,
            Double confidence,
            String question
    ) implements Serializable {}

    record SourceDto(
            String document_id,
            String title,
            String snippet,
            Double relevance
    ) implements Serializable {}

    record DeleteResult(
            String message
    ) implements Serializable {}

    record BulkIngestDocument(
            String title,
            String content,
            Map<String, Object> metadata
    ) implements Serializable {}

    record BulkIngestResult(
            int total,
            int successful,
            int failed,
            List<IngestResult> results
    ) implements Serializable {}
}
