package com.vectorflow.graphql;

import com.vectorflow.model.Document;
import com.vectorflow.model.Role;
import com.vectorflow.model.User;
import com.vectorflow.model.dto.Metadata;
import com.vectorflow.repository.DocumentRepository;
import com.vectorflow.security.GraphQlAuthGuard;
import com.vectorflow.service.AuthService;
import com.vectorflow.service.VectorSearchService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.graphql.data.method.annotation.Argument;
import org.springframework.graphql.data.method.annotation.MutationMapping;
import org.springframework.stereotype.Controller;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Controller
@RequiredArgsConstructor
@Slf4j
public class MutationResolver {

    private final VectorSearchService vectorSearchService;
    private final DocumentRepository documentRepository;
    private final GraphQlAuthGuard authGuard;
    private final AuthService authService;

    @MutationMapping
    public IngestResponse ingest(@Argument IngestInput input) {
        User user = authGuard.requireAnyRole(Role.EDITOR, Role.ADMIN);
        log.info("GraphQL ingest document: {} by user: {} (role: {})", input.title(), user.getEmail(), user.getRole());

        Metadata metadata = null;
        if (input.metadata() != null) {
            metadata = Metadata.builder()
                    .category(input.metadata().category())
                    .tags(input.metadata().tags())
                    .build();
        }

        var result = vectorSearchService.ingest(input.title(), input.content(), metadata);

        Map<String, Object> metadataMap = null;
        if (input.metadata() != null) {
            metadataMap = Map.of(
                    "category", input.metadata().category() != null ? input.metadata().category() : "",
                    "tags", input.metadata().tags() != null ? input.metadata().tags() : List.of()
            );
        }

        Document document = Document.builder()
                .id(UUID.fromString(result.document_id()))
                .user(user)
                .title(result.title())
                .chunkCount(result.chunk_count())
                .status(result.status().toLowerCase())
                .metadata(metadataMap)
                .build();
        documentRepository.save(document);

        log.info("Document saved: id={}, user_id={}", result.document_id(), user.getId());

        return new IngestResponse(
                result.document_id(),
                result.title(),
                result.chunk_count(),
                DocumentStatus.valueOf(result.status().toUpperCase()),
                result.message()
        );
    }

    @MutationMapping
    public DeleteResponse deleteDocument(@Argument String documentId) {
        User user = authGuard.requireAnyRole(Role.EDITOR, Role.ADMIN);
        log.info("GraphQL delete document: {} by user: {} (role: {})", documentId, user.getEmail(), user.getRole());

        try {
            vectorSearchService.deleteDocument(documentId);
            documentRepository.deleteById(UUID.fromString(documentId));
            return new DeleteResponse(true, "Document deleted successfully");
        } catch (Exception e) {
            log.error("Failed to delete document", e);
            return new DeleteResponse(false, "Failed to delete document");
        }
    }

    @MutationMapping
    public AuthResponse register(@Argument RegisterInput input) {
        log.info("GraphQL register user: {}", input.email());

        var result = authService.register(input.email(), input.password());

        return new AuthResponse(
                result.token(),
                new UserOutput(
                        result.user().getId().toString(),
                        result.user().getEmail(),
                        result.user().getRole().name(),
                        result.user().getCreatedAt().toString()
                )
        );
    }

    @MutationMapping
    public AuthResponse login(@Argument LoginInput input) {
        log.info("GraphQL login user: {}", input.email());

        var result = authService.login(input.email(), input.password());

        return new AuthResponse(
                result.token(),
                new UserOutput(
                        result.user().getId().toString(),
                        result.user().getEmail(),
                        result.user().getRole().name(),
                        result.user().getCreatedAt().toString()
                )
        );
    }

    @MutationMapping
    public BulkIngestResponse bulkIngest(@Argument BulkIngestInput input) {
        User user = authGuard.requireAnyRole(Role.EDITOR, Role.ADMIN);
        log.info("GraphQL bulk ingest: {} documents by user: {} (role: {})",
                input.documents().size(), user.getEmail(), user.getRole());

        List<VectorSearchService.BulkIngestDocument> docs = input.documents().stream()
                .map(doc -> new VectorSearchService.BulkIngestDocument(
                        doc.title(),
                        doc.content(),
                        doc.metadata() != null ? Map.of(
                                "category", doc.metadata().category() != null ? doc.metadata().category() : "",
                                "tags", doc.metadata().tags() != null ? doc.metadata().tags() : List.of()
                        ) : Map.of()
                ))
                .toList();

        var bulkResult = vectorSearchService.bulkIngest(docs);

        List<IngestResponse> responses = new ArrayList<>();
        for (var result : bulkResult.results()) {
            if ("completed".equalsIgnoreCase(result.status())) {
                Document document = Document.builder()
                        .id(UUID.fromString(result.document_id()))
                        .user(user)
                        .title(result.title())
                        .chunkCount(result.chunk_count())
                        .status(result.status().toLowerCase())
                        .build();
                documentRepository.save(document);
                log.info("Bulk ingest document saved: id={}, user_id={}", result.document_id(), user.getId());
            }

            responses.add(new IngestResponse(
                    result.document_id(),
                    result.title(),
                    result.chunk_count(),
                    DocumentStatus.valueOf(result.status().toUpperCase()),
                    result.message()
            ));
        }

        return new BulkIngestResponse(
                bulkResult.total(),
                bulkResult.successful(),
                bulkResult.failed(),
                responses
        );
    }

    @MutationMapping
    public AssignRoleResponse assignRole(@Argument AssignRoleInput input) {
        User admin = authGuard.requireRole(Role.ADMIN);
        log.info("Admin {} assigning role {} to user {}", admin.getEmail(), input.role(), input.userId());

        var result = authService.assignRole(input.userId(), input.role());
        return new AssignRoleResponse(
                true,
                "Role updated to " + result.getRole().name() + " for user " + result.getEmail(),
                new UserOutput(
                        result.getId().toString(),
                        result.getEmail(),
                        result.getRole().name(),
                        result.getCreatedAt().toString()
                )
        );
    }

    // GraphQL Input/Output types
    public record IngestInput(String title, String content, MetadataInput metadata) {}
    public record MetadataInput(String category, List<String> tags) {}
    public record RegisterInput(String email, String password) {}
    public record LoginInput(String email, String password) {}
    public record BulkIngestInput(List<IngestInput> documents) {}
    public record AssignRoleInput(String userId, String role) {}
    public record IngestResponse(String documentId, String title, Integer chunkCount, DocumentStatus status, String message) {}
    public record BulkIngestResponse(int total, int successful, int failed, List<IngestResponse> results) {}
    public record DeleteResponse(boolean success, String message) {}
    public record AuthResponse(String token, UserOutput user) {}
    public record AssignRoleResponse(boolean success, String message, UserOutput user) {}
    public record UserOutput(String id, String email, String role, String createdAt) {}
    public enum DocumentStatus { PROCESSING, COMPLETED, FAILED }
}
