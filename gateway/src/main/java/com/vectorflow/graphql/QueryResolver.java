package com.vectorflow.graphql;

import com.vectorflow.model.Role;
import com.vectorflow.model.User;
import com.vectorflow.repository.UserRepository;
import com.vectorflow.security.GraphQlAuthGuard;
import com.vectorflow.service.VectorSearchService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.QueryMapping;
import org.springframework.stereotype.Controller;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Controller
@RequiredArgsConstructor
@Slf4j
public class QueryResolver {

    private final VectorSearchService vectorSearchService;
    private final GraphQlAuthGuard authGuard;
    private final UserRepository userRepository;

    /**
     * Search for documents using vector similarity.
     */
    @QueryMapping
    public SearchResponse search(
            @Argument String query,
            @Argument Integer limit,
            @Argument FilterInput filters
    ) {
        authGuard.requireAuth();
        log.info("GraphQL search query: {}", query);

        // Convert filters to map
        Map<String, Object> filterMap = null;
        if (filters != null) {
            filterMap = new HashMap<>();
            if (filters.category() != null) {
                filterMap.put("category", filters.category());
            }
            if (filters.tags() != null) {
                filterMap.put("tags", filters.tags());
            }
        }

        var result = vectorSearchService.search(query, limit, filterMap);

        // Convert to GraphQL response
        List<SearchResultOutput> results = result.results().stream()
                .map(r -> new SearchResultOutput(
                        r.id(),
                        r.document_id(),
                        r.title(),
                        r.snippet(),
                        r.score(),
                        convertMetadata(r.metadata())
                ))
                .collect(Collectors.toList());

        return new SearchResponse(results, result.total_count(), result.query());
    }

    /**
     * Ask a question and get an AI-generated answer.
     */
    @QueryMapping
    public AskResponse ask(
            @Argument String question,
            @Argument Integer maxSources
    ) {
        authGuard.requireAuth();
        log.info("GraphQL ask question: {}", question);

        var result = vectorSearchService.ask(question, maxSources);

        // Convert sources
        List<SourceOutput> sources = result.sources().stream()
                .map(s -> new SourceOutput(
                        s.document_id(),
                        s.title(),
                        s.snippet(),
                        s.relevance()
                ))
                .collect(Collectors.toList());

        return new AskResponse(result.answer(), sources, result.confidence(), result.question());
    }

    /**
     * Get current user info. Returns null for unauthenticated requests.
     */
    @QueryMapping
    public UserOutput me() {
        User user = authGuard.optionalAuth();
        if (user == null) {
            return null;
        }
        return new UserOutput(
                user.getId().toString(),
                user.getEmail(),
                user.getRole().name(),
                user.getCreatedAt().toString()
        );
    }

    @QueryMapping
    public List<UserOutput> users() {
        authGuard.requireRole(Role.ADMIN);
        return userRepository.findAll().stream()
                .map(u -> new UserOutput(
                        u.getId().toString(),
                        u.getEmail(),
                        u.getRole().name(),
                        u.getCreatedAt().toString()
                ))
                .collect(Collectors.toList());
    }

    /**
     * List ingested documents with pagination. Requires EDITOR or ADMIN.
     */
    @QueryMapping
    public DocumentListResponse documents(
            @Argument Integer page,
            @Argument Integer pageSize
    ) {
        authGuard.requireAnyRole(Role.EDITOR, Role.ADMIN);
        int p = page != null && page >= 1 ? page : 1;
        int ps = pageSize != null && pageSize >= 1 && pageSize <= 100 ? pageSize : 20;
        var result = vectorSearchService.listDocuments(p, ps);
        List<DocumentInfoOutput> docs = result.documents().stream()
                .map(d -> new DocumentInfoOutput(
                        d.document_id(),
                        d.title(),
                        d.chunk_count(),
                        d.created_at(),
                        convertMetadata(d.metadata())
                ))
                .collect(Collectors.toList());
        return new DocumentListResponse(docs, result.total_count(), result.page(), result.page_size());
    }

    /**
     * Get a single document by ID with full chunk content. Requires EDITOR or ADMIN.
     */
    @QueryMapping
    public DocumentDetailOutput document(@Argument String documentId) {
        authGuard.requireAnyRole(Role.EDITOR, Role.ADMIN);
        var result = vectorSearchService.getDocument(documentId);
        List<DocumentChunkOutput> chunks = result.chunks().stream()
                .map(c -> new DocumentChunkOutput(
                        c.chunk_id(),
                        c.chunk_index(),
                        c.text(),
                        c.created_at(),
                        convertMetadata(c.metadata())
                ))
                .collect(Collectors.toList());
        return new DocumentDetailOutput(
                result.document_id(),
                result.title(),
                chunks,
                result.total_chunks()
        );
    }

    // Helper method to convert metadata
    private MetadataOutput convertMetadata(Map<String, Object> metadata) {
        if (metadata == null) {
            return null;
        }
        String category = metadata.get("category") != null ? metadata.get("category").toString() : null;
        @SuppressWarnings("unchecked")
        List<String> tags = metadata.get("tags") != null ? (List<String>) metadata.get("tags") : null;
        return new MetadataOutput(category, tags);
    }

    // GraphQL Input/Output types
    public record FilterInput(String category, List<String> tags) {}
    public record SearchResponse(List<SearchResultOutput> results, Integer totalCount, String query) {}
    public record SearchResultOutput(String id, String documentId, String title, String snippet, Double score, MetadataOutput metadata) {}
    public record MetadataOutput(String category, List<String> tags) {}
    public record AskResponse(String answer, List<SourceOutput> sources, Double confidence, String question) {}
    public record SourceOutput(String documentId, String title, String snippet, Double relevance) {}
    public record UserOutput(String id, String email, String role, String createdAt) {}
    public record DocumentInfoOutput(String documentId, String title, int chunkCount, String createdAt, MetadataOutput metadata) {}
    public record DocumentListResponse(List<DocumentInfoOutput> documents, int totalCount, int page, int pageSize) {}
    public record DocumentChunkOutput(String chunkId, int chunkIndex, String text, String createdAt, MetadataOutput metadata) {}
    public record DocumentDetailOutput(String documentId, String title, List<DocumentChunkOutput> chunks, int totalChunks) {}
}

