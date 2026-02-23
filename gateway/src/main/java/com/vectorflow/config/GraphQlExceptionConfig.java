package com.vectorflow.config;

import graphql.ErrorClassification;
import graphql.GraphQLError;
import graphql.schema.DataFetchingEnvironment;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.graphql.execution.DataFetcherExceptionResolverAdapter;
import org.springframework.security.access.AccessDeniedException;

@Configuration
public class GraphQlExceptionConfig {

    @Bean
    public DataFetcherExceptionResolverAdapter authExceptionResolver() {
        return new DataFetcherExceptionResolverAdapter() {
            @Override
            protected GraphQLError resolveToSingleError(Throwable ex, DataFetchingEnvironment env) {
                if (ex instanceof AccessDeniedException) {
                    return GraphQLError.newError()
                            .message(ex.getMessage())
                            .errorType(ErrorClassification.errorClassification("UNAUTHORIZED"))
                            .path(env.getExecutionStepInfo().getPath())
                            .location(env.getField().getSourceLocation())
                            .build();
                }
                return null;
            }
        };
    }
}
