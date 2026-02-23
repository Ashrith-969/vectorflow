# VectorFlow

**Distributed Vector Search & LLM-Orchestrated Retrieval Engine**

A production-ready RAG (Retrieval-Augmented Generation) backend that transforms unstructured documents into conversational search by integrating distributed ingestion, vector indexing, and LLM-powered query routing.

---

## 🎯 What This Project Does

VectorFlow enables you to:
1. **Ingest** documents → Automatically chunk → Generate embeddings → Store in vector database
2. **Search** documents using semantic similarity (understands meaning, not just keywords)
3. **Ask** natural language questions and get AI-generated answers with source citations

### Example Use Case
```
User: "What are the benefits of microservices architecture?"

VectorFlow:
1. Converts question to 1536-dimensional vector
2. Finds most similar document chunks in Qdrant
3. Sends chunks + question to GPT-3.5-turbo
4. Returns: "Microservices provide... [based on your documents]"
   Sources: [Architecture Guide - 95% relevance, Design Patterns - 89% relevance]
```

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **API Gateway** | Spring Boot + GraphQL | Unified API, JWT auth, caching |
| **AI Service** | Python + FastAPI | Embeddings, RAG, LLM orchestration |
| **Vector DB** | Qdrant | Similarity search, vector storage |
| **Relational DB** | PostgreSQL | Users, document metadata |
| **Cache** | Redis | Search result caching |
| **Containerization** | Docker Compose | Multi-service orchestration |
| **AI/ML** | OpenAI API | text-embedding-ada-002, GPT-3.5-turbo |

---

## 🏗 Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                  │
│                    (Postman / Frontend / Mobile)                        │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ GraphQL Requests
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    SPRING BOOT GATEWAY (Port 8080)                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────────────┐ │
│  │  GraphQL   │  │    JWT     │  │   Redis    │  │    PostgreSQL      │ │
│  │ Resolvers  │  │   Auth     │  │   Cache    │  │  (User Storage)    │ │
│  └────────────┘  └────────────┘  └────────────┘  └────────────────────┘ │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTP REST (Internal)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    PYTHON SERVICE (Port 8000)                           │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐            │
│  │   Embedding    │  │    Qdrant      │  │      LLM       │            │
│  │    Service     │  │    Service     │  │    Service     │            │
│  │  (Chunking +   │  │  (Vector CRUD  │  │  (RAG Pipeline │            │
│  │   Embeddings)  │  │   + Search)    │  │   + Answers)   │            │
│  └────────────────┘  └────────────────┘  └────────────────┘            │
└───────────┬───────────────────┬───────────────────┬─────────────────────┘
            │                   │                   │
            ▼                   ▼                   ▼
     ┌──────────┐        ┌──────────┐        ┌──────────┐
     │  OpenAI  │        │  Qdrant  │        │ PostgreSQL│
     │   API    │        │  (6333)  │        │  (5432)   │
     └──────────┘        └──────────┘        └──────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **Spring Boot Gateway** | API exposure, authentication, caching, request routing |
| **Python Service** | AI/ML operations, document processing, vector operations |
| **Qdrant** | Vector storage, similarity search with filtering |
| **PostgreSQL** | User accounts, document metadata, audit trails |
| **Redis** | Cache search results to reduce API calls and latency |
| **OpenAI** | Generate embeddings (ada-002) and answers (GPT-3.5) |

---

## 🔄 How It Works - Data Flows

### Flow 1: Document Ingestion

When you ingest a document, here's what happens:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        DOCUMENT INGESTION FLOW                           │
└──────────────────────────────────────────────────────────────────────────┘

1. CLIENT                    2. GATEWAY                   3. PYTHON SERVICE
   │                            │                              │
   │  GraphQL: ingest()         │                              │
   │ ─────────────────────────► │                              │
   │  {title, content,          │     HTTP POST /api/ingest    │
   │   metadata}                │ ────────────────────────────►│
   │                            │                              │
   │                            │                    ┌─────────┴─────────┐
   │                            │                    │ 4. CHUNK DOCUMENT │
   │                            │                    │  • Tokenize text  │
   │                            │                    │  • Split: 500     │
   │                            │                    │    tokens each    │
   │                            │                    │  • Overlap: 50    │
   │                            │                    │    tokens         │
   │                            │                    │  • Add title      │
   │                            │                    │    prefix         │
   │                            │                    └─────────┬─────────┘
   │                            │                              │
   │                            │                    ┌─────────┴─────────┐
   │                            │                    │ 5. GENERATE       │
   │                            │                    │    EMBEDDINGS     │
   │                            │                    │  • Batch API call │
   │                            │                    │  • text-embedding │
   │                            │                    │    -ada-002       │
   │                            │                    │  • 1536 dims each │
   │                            │                    └─────────┬─────────┘
   │                            │                              │
   │                            │                              ▼
   │                            │                         ┌─────────┐
   │                            │                         │ QDRANT  │
   │                            │                         │ • Store │
   │                            │                         │ vectors │
   │                            │                         │ • Store │
   │                            │                         │ payload │
   │                            │                         └─────────┘
   │                            │                              │
   │  {documentId, chunkCount}  │    {document_id, chunks}     │
   │ ◄───────────────────────── │ ◄────────────────────────────│
```

**What's stored in Qdrant per chunk:**
```json
{
  "id": "uuid-of-chunk",
  "vector": [0.123, -0.456, ...],  // 1536 floats
  "payload": {
    "text": "[Document: Title]\nActual chunk content...",
    "document_id": "uuid-of-document",
    "title": "Document Title",
    "chunk_index": 0,
    "created_at": "2024-01-15T10:30:00Z",
    "metadata": {"category": "tech", "tags": ["ai"]}
  }
}
```

### Flow 2: Semantic Search

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          SEARCH FLOW                                     │
└──────────────────────────────────────────────────────────────────────────┘

1. User Query: "How does vector similarity work?"
                    │
                    ▼
2. Generate Query Embedding
   ┌────────────────────────────────────────┐
   │  OpenAI API: text-embedding-ada-002    │
   │  Input: "How does vector similarity..."│
   │  Output: [0.034, -0.891, 0.223, ...]   │
   │          (1536 dimensions)             │
   └────────────────────────────────────────┘
                    │
                    ▼
3. Cosine Similarity Search in Qdrant
   ┌────────────────────────────────────────┐
   │  Compare query vector against all      │
   │  stored vectors using:                 │
   │                                        │
   │  similarity = (A · B) / (|A| × |B|)   │
   │                                        │
   │  Score range: 0.0 (unrelated)         │
   │               to 1.0 (identical)       │
   └────────────────────────────────────────┘
                    │
                    ▼
4. Return Top-K Results (ranked by score)
   ┌────────────────────────────────────────┐
   │  Result 1: score=0.92, "Vector DBs..." │
   │  Result 2: score=0.87, "Similarity..." │
   │  Result 3: score=0.81, "Embeddings..." │
   └────────────────────────────────────────┘
```

### Flow 3: RAG Question Answering

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    RAG (Retrieval-Augmented Generation) FLOW             │
└──────────────────────────────────────────────────────────────────────────┘

User Question: "What is a vector database and when should I use one?"
                              │
         ┌────────────────────┴────────────────────┐
         │           RETRIEVAL PHASE               │
         ▼                                         │
┌─────────────────────┐                           │
│ 1. Embed question   │                           │
│ 2. Search Qdrant    │                           │
│ 3. Get top-5 chunks │                           │
└─────────┬───────────┘                           │
          │                                        │
          ▼                                        │
┌─────────────────────────────────────────────────┐
│ Retrieved Context:                              │
│                                                 │
│ [Source 1: Qdrant Basics]                       │
│ "A vector database stores high-dimensional..."  │
│                                                 │
│ [Source 2: Database Selection Guide]            │
│ "Use vector DBs when you need semantic..."     │
│                                                 │
│ [Source 3: ML Infrastructure]                   │
│ "Vector databases excel at similarity..."      │
└─────────────────────┬───────────────────────────┘
                      │
         ┌────────────┴────────────────────┐
         │         GENERATION PHASE         │
         ▼                                  │
┌──────────────────────────────────────────────────────────────────────────┐
│                          OPENAI GPT-3.5-TURBO                            │
│                                                                          │
│  System: "You are a helpful AI assistant that answers based on context. │
│           Only use provided context. Cite sources. Be concise."          │
│                                                                          │
│  User: "Context: [Source 1]...[Source 2]...[Source 3]...                │
│         Question: What is a vector database and when should I use one?" │
│                                                                          │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │
                                     ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                              RESPONSE                                    │
│                                                                          │
│  Answer: "A vector database is a specialized database designed to       │
│           store and query high-dimensional vectors (embeddings).        │
│           You should use one when you need semantic similarity          │
│           search, such as for recommendation systems, image             │
│           search, or RAG applications like this one."                   │
│                                                                          │
│  Sources: [Qdrant Basics - 92% relevance]                               │
│           [Database Selection Guide - 87% relevance]                    │
│                                                                          │
│  Confidence: 0.90                                                        │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Concepts Explained

### What is RAG (Retrieval-Augmented Generation)?

RAG combines **retrieval** (finding relevant documents) with **generation** (producing answers). Instead of relying solely on the LLM's training data:

1. **Retrieve**: Find relevant chunks from YOUR documents
2. **Augment**: Add these chunks as context to the prompt
3. **Generate**: LLM produces answer grounded in your data

**Benefits:**
- ✅ Reduces hallucinations (grounded in real documents)
- ✅ Provides citations (traceable sources)
- ✅ Uses up-to-date information (your documents, not training data)
- ✅ Domain-specific knowledge (your company's data)

### What are Embeddings?

Embeddings are **numerical representations of text** that capture semantic meaning:

```
"King" → [0.2, 0.8, -0.3, ...]      (1536 numbers)
"Queen" → [0.19, 0.79, -0.31, ...]  (similar vector!)
"Apple" → [-0.5, 0.1, 0.9, ...]     (very different)
```

**Why it works:**
- Similar meanings = similar vectors
- Can compute "distance" between concepts
- "King - Man + Woman ≈ Queen" (vector arithmetic!)

### Why Chunking with Overlap?

Documents are split into smaller pieces because:
1. **Context window limits**: LLMs have token limits
2. **Precision**: Smaller chunks = more precise matches
3. **Overlap (50 tokens)**: Ensures important information at boundaries isn't lost

```
Original: "...end of paragraph. Start of new topic..."
                            ↑
                    Would be split here

With Overlap:
Chunk 1: "...end of paragraph. Start of new topic. First sentences..."
Chunk 2: "Start of new topic. First sentences. More content..."
                              ↑
                    Overlap ensures context preserved
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd vectorflow

# Copy environment template
cp env.sample .env

# Edit .env and add your OpenAI key
# OPENAI_API_KEY=sk-your-key-here
```

### 2. Start All Services

```bash
docker-compose up --build
```

Wait for all services to be healthy (about 30-60 seconds).

### 3. Access the Services

| Service | URL | Description |
|---------|-----|-------------|
| GraphQL API | http://localhost:8080/graphql | Main API endpoint |
| GraphiQL UI | http://localhost:8080/graphiql | Interactive GraphQL IDE |
| Python Docs | http://localhost:8000/docs | FastAPI Swagger UI |
| Python API | http://localhost:8000 | Direct Python service |

### 4. Test with Pre-seeded User

```graphql
mutation {
  login(input: {
    email: "test@vectorflow.dev"
    password: "password123"
  }) {
    token
    user { id email }
  }
}
```

---

## 📖 API Reference

### Authentication

**Register:**
```graphql
mutation {
  register(input: {
    email: "user@example.com"
    password: "securepassword"
  }) {
    token
    user { id email createdAt }
  }
}
```

**Login:**
```graphql
mutation {
  login(input: {
    email: "user@example.com"
    password: "securepassword"
  }) {
    token
  }
}
```

### Document Operations

**Ingest Document:**
```graphql
mutation {
  ingest(input: {
    title: "Introduction to Machine Learning"
    content: "Machine learning is a subset of artificial intelligence..."
    metadata: {
      category: "technology"
      tags: ["ai", "ml", "tutorial"]
    }
  }) {
    documentId
    chunkCount
    status
    message
  }
}
```

**Delete Document:**
```graphql
mutation {
  deleteDocument(documentId: "uuid-here") {
    success
    message
  }
}
```

### Search & Query

**Vector Search:**
```graphql
query {
  search(
    query: "How does neural network training work?"
    limit: 5
    filters: { category: "technology" }
  ) {
    results {
      id
      documentId
      title
      snippet
      score
      metadata { category tags }
    }
    totalCount
    query
  }
}
```

**Ask with RAG:**
```graphql
query {
  ask(
    question: "What are the key differences between SQL and NoSQL databases?"
    maxSources: 5
  ) {
    answer
    sources {
      documentId
      title
      snippet
      relevance
    }
    confidence
    question
  }
}
```

**Get Current User:**
```graphql
query {
  me {
    id
    email
    createdAt
  }
}
```

---

## 📁 Project Structure

```
vectorflow/
│
├── docker-compose.yml          # 🐳 Multi-container orchestration
├── env.sample                  # 📋 Environment variables template
├── README.md                   # 📖 This file
│
├── gateway/                    # ☕ Spring Boot GraphQL API Gateway
│   ├── Dockerfile
│   ├── pom.xml                 # Maven dependencies
│   └── src/main/
│       ├── java/com/vectorflow/
│       │   ├── VectorFlowApplication.java    # Entry point
│       │   ├── config/
│       │   │   ├── SecurityConfig.java       # JWT + CORS config
│       │   │   └── RedisConfig.java          # Cache configuration
│       │   ├── graphql/
│       │   │   ├── QueryResolver.java        # search, ask, me
│       │   │   └── MutationResolver.java     # ingest, login, register
│       │   ├── model/
│       │   │   ├── User.java                 # JPA entity
│       │   │   └── dto/                      # Data transfer objects
│       │   ├── repository/
│       │   │   ├── UserRepository.java       # Spring Data JPA
│       │   │   └── DocumentRepository.java
│       │   ├── security/
│       │   │   ├── JwtTokenProvider.java     # Token generation/validation
│       │   │   ├── JwtAuthFilter.java        # Request filter
│       │   │   └── CustomUserDetailsService.java
│       │   └── service/
│       │       └── PythonServiceClient.java  # WebClient for Python
│       └── resources/
│           ├── application.yml               # Spring configuration
│           └── graphql/
│               └── schema.graphqls           # GraphQL schema definition
│
├── python-service/             # 🐍 FastAPI AI/ML Service
│   ├── Dockerfile
│   ├── requirements.txt        # Python dependencies
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Pydantic settings
│   ├── models/
│   │   └── schemas.py          # Request/Response models
│   ├── routers/
│   │   ├── ingest.py           # POST /api/ingest
│   │   ├── bulk_ingest.py      # POST /api/bulk-ingest
│   │   ├── search.py           # POST /api/search
│   │   └── ask.py              # POST /api/ask
│   └── services/
│       ├── embedding_service.py  # Chunking + OpenAI embeddings
│       ├── qdrant_service.py     # Vector CRUD operations
│       └── llm_service.py        # RAG pipeline
│
├── scripts/
│   ├── init-db.sql             # PostgreSQL schema + seed data
│   └── bulk_ingest_data.py     # Async bulk ingestion script
│
├── sample-data/                # 📄 Demo documents for testing
│   ├── qdrant-basics.md
│   ├── python-fastapi.md
│   └── docker-intro.md
│
└── postman/
    └── VectorFlow.postman_collection.json  # API testing collection
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key for embeddings & LLM | - | ✅ Yes |
| `POSTGRES_DB` | PostgreSQL database name | vectorflow | No |
| `POSTGRES_USER` | PostgreSQL username | vectorflow | No |
| `POSTGRES_PASSWORD` | PostgreSQL password | vectorflow123 | No |
| `JWT_SECRET` | Secret for signing JWT tokens | auto-generated | No |
| `QDRANT_HOST` | Qdrant server hostname | qdrant | No |
| `QDRANT_PORT` | Qdrant server port | 6333 | No |

### Chunking Configuration

In `python-service/config.py`:
```python
chunk_size: int = 500      # tokens per chunk
chunk_overlap: int = 50    # overlap between chunks
embedding_model: str = "text-embedding-ada-002"
llm_model: str = "gpt-3.5-turbo"
```

---

## 🛠 Development

### Run Services Individually

**Python Service:**
```bash
cd python-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Spring Boot Gateway:**
```bash
cd gateway
./mvnw spring-boot:run
```

### Useful Docker Commands

```bash
# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f python-service

# Restart a service
docker-compose restart gateway

# Rebuild and restart
docker-compose up --build -d

# Stop everything
docker-compose down

# Stop and remove all data
docker-compose down -v
```

### Testing

**Import Postman Collection:**
1. Open Postman
2. Import `postman/VectorFlow.postman_collection.json`
3. Set `{{baseUrl}}` to `http://localhost:8080`
4. Run the collection

**Bulk Ingest Test Data:**
```bash
python scripts/bulk_ingest_data.py
```

---

## 🔧 Technical Decisions

| Decision | Rationale |
|----------|-----------|
| **GraphQL over REST** | Flexible queries, strong typing, single endpoint, introspection |
| **Microservices (Java + Python)** | Java for enterprise patterns (security, caching); Python for AI/ML ecosystem |
| **Qdrant over Pinecone** | Open-source, self-hostable, excellent filtering, Rust performance |
| **text-embedding-ada-002** | Best cost/quality ratio, 1536 dimensions, OpenAI reliability |
| **500 token chunks** | Balance between context preservation and search precision |
| **50 token overlap** | Prevents information loss at chunk boundaries |
| **Stateless JWT** | Horizontal scalability, no session storage needed |
| **Redis caching** | Reduces OpenAI API calls, faster repeated queries |
| **WebClient (reactive)** | Non-blocking HTTP for gateway→Python communication |

---

## 🐛 Troubleshooting

### Common Issues

**1. OpenAI API Errors**
```
Error: Invalid API key
```
→ Check that `OPENAI_API_KEY` is set correctly in `.env`

**2. Qdrant Connection Failed**
```
Error: Connection refused on port 6333
```
→ Wait for Qdrant to fully start, or check `docker-compose logs qdrant`

**3. PostgreSQL Health Check Failing**
```
postgres-1 | FATAL: password authentication failed
```
→ Remove volumes and restart: `docker-compose down -v && docker-compose up`

**4. Gateway Can't Connect to Python Service**
```
Error: Connection refused to python-service:8000
```
→ Check Python service logs: `docker-compose logs python-service`

### Health Checks

```bash
# Check all services
docker-compose ps

# Python service health
curl http://localhost:8000/health

# Gateway health
curl http://localhost:8080/actuator/health
```

---

## 📊 Performance Considerations

- **Embedding batch size**: OpenAI allows batching multiple texts in one API call
- **Qdrant HNSW index**: Provides O(log n) search complexity
- **Redis TTL**: Configure cache expiration based on data freshness needs
- **Chunk size tuning**: Larger chunks = more context but lower precision
- **Connection pooling**: WebClient reuses connections to Python service

---

## 🔒 Security Features

- **JWT Authentication**: Stateless tokens with 24-hour expiry
- **BCrypt Password Hashing**: Industry-standard password security
- **CORS Configuration**: Configurable allowed origins
- **CSRF Disabled**: Appropriate for stateless API-only service
- **Input Validation**: Pydantic models on Python, GraphQL types on Gateway

---

## 📄 License

MIT License - feel free to use this project for learning and building!

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Built with ❤️ using Spring Boot, FastAPI, Qdrant, and OpenAI**
