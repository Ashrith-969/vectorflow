package com.vectorflow.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SearchResult {
    private String id;
    private String documentId;
    private String title;
    private String snippet;
    private Double score;
    private Map<String, Object> metadata;
}

