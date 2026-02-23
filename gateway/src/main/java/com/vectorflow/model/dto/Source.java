package com.vectorflow.model.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Source {
    private String documentId;
    private String title;
    private String snippet;
    private Double relevance;
}

