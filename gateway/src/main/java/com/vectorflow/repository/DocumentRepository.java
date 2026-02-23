package com.vectorflow.repository;

import com.vectorflow.model.Document;
import com.vectorflow.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface DocumentRepository extends JpaRepository<Document, UUID> {
    
    List<Document> findByUser(User user);
    
    List<Document> findByStatus(String status);
}

