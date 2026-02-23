package com.vectorflow;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

@SpringBootApplication
@EnableCaching
public class VectorFlowApplication {

    public static void main(String[] args) {
        SpringApplication.run(VectorFlowApplication.class, args);
    }
}

