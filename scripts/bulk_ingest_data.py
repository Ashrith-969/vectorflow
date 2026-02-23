"""Bulk ingestion script for VectorFlow sample data."""

import asyncio
import httpx
import json
from typing import List, Dict

# Sample technical documentation data
DOCUMENTS = [
    {
        "title": "Python Async Programming",
        "content": "Asynchronous programming in Python uses async and await keywords for concurrent execution. Asyncio is the built-in library for writing asynchronous code. Coroutines are functions defined with async def that can be paused and resumed. The await keyword pauses execution until the awaited coroutine completes. Event loops manage the execution of asynchronous tasks. asyncio.gather() runs multiple coroutines concurrently and waits for all to complete. asyncio.create_task() schedules coroutines for concurrent execution. Async context managers use async with syntax. Async iterators use async for loops. Use asyncio.create_task() to schedule coroutines without immediately awaiting them. Semaphores and locks provide synchronization primitives. Async is ideal for I/O-bound operations like API calls, database queries, and file operations. It's not beneficial for CPU-bound tasks which should use multiprocessing instead. Proper exception handling with try-except blocks is crucial in async code.",
        "metadata": {
            "category": "programming",
            "tags": ["python", "async", "concurrency"]
        }
    },
    {
        "title": "REST API Design Principles",
        "content": "REST stands for Representational State Transfer, an architectural style for distributed systems. RESTful APIs use HTTP methods semantically: GET for retrieval, POST for creation, PUT for full updates, PATCH for partial updates, DELETE for removal. Use proper HTTP status codes: 200 for success, 201 for created resources, 204 for successful deletion, 400 for bad requests, 401 for unauthorized, 403 for forbidden, 404 for not found, 500 for server errors. API versioning can be done via URL path (/v1/users), headers, or query parameters. Pagination for large result sets uses limit and offset parameters. Implement consistent error response formats with error codes and messages. Authentication methods include JWT tokens, OAuth 2.0, or API keys. Rate limiting prevents API abuse using headers like X-RateLimit-Limit. CORS headers allow cross-origin requests from browsers. Comprehensive documentation using OpenAPI/Swagger specifications is essential. Use HTTPS for all API endpoints to ensure security.",
        "metadata": {
            "category": "api-design",
            "tags": ["rest", "api", "http", "web"]
        }
    },
    {
        "title": "PostgreSQL Database Fundamentals",
        "content": "PostgreSQL is a powerful open-source relational database system with strong ACID compliance. It supports complex queries, foreign keys, triggers, views, and stored procedures. Use CREATE TABLE to define database schemas with data types like INTEGER, VARCHAR, TIMESTAMP, JSONB. Primary keys uniquely identify rows. Indexes improve query performance with CREATE INDEX commands. B-tree indexes are default, while GiST and GIN indexes support full-text search. Foreign keys maintain referential integrity between tables. Joins combine data: INNER JOIN for matching rows, LEFT JOIN for all left table rows, RIGHT JOIN for all right table rows. WHERE clauses filter query results. GROUP BY aggregates data with functions like COUNT, SUM, AVG. HAVING filters grouped results. Transactions ensure data consistency with BEGIN, COMMIT, and ROLLBACK commands. Connection pooling with tools like PgBouncer improves performance under load. VACUUM maintains database health by reclaiming storage.",
        "metadata": {
            "category": "database",
            "tags": ["postgresql", "sql", "relational"]
        }
    },
    {
        "title": "Redis Caching Strategies",
        "content": "Redis is an in-memory data structure store used as database, cache, and message broker. It supports data types including strings, hashes, lists, sets, sorted sets, bitmaps, and streams. SET and GET commands handle simple key-value operations. EXPIRE sets time-to-live for automatic key expiration. Cache-aside pattern loads data from database on cache miss then stores in cache. Write-through strategy updates both cache and database simultaneously. Write-behind queues writes for asynchronous database updates. Use Redis for session storage with automatic expiration. Rate limiting implements sliding window algorithms with sorted sets. Pub/sub messaging enables real-time communication between services. Redis persistence uses RDB snapshots or AOF (Append-Only File) logs for durability. Redis Cluster provides horizontal scaling through sharding. Redis Sentinel offers high availability with automatic failover. Pipeline commands to reduce round-trip latency. Use Lua scripts for atomic multi-command operations.",
        "metadata": {
            "category": "caching",
            "tags": ["redis", "cache", "performance"]
        }
    },
    {
        "title": "JWT Authentication Explained",
        "content": "JSON Web Tokens (JWT) are compact, URL-safe tokens for secure authentication and authorization. JWTs consist of three Base64-encoded parts separated by dots: header, payload, and signature. The header specifies the signing algorithm (HS256, RS256) and token type. The payload contains claims like user ID (sub), issued at (iat), expiration (exp), and custom claims. The signature verifies token integrity using a secret key or public/private key pair. Tokens are stateless—servers don't store session data. Clients send JWTs in the Authorization header with Bearer scheme. Use HTTPS to prevent token interception. Set appropriate expiration times: short for access tokens (15 minutes), long for refresh tokens (7 days). Refresh tokens enable obtaining new access tokens without re-authentication. Validate tokens on every protected request by verifying signature and expiration. Store tokens securely: httpOnly cookies for web apps, secure storage for mobile apps. Never store sensitive data in JWT payloads as they're readable by anyone.",
        "metadata": {
            "category": "security",
            "tags": ["jwt", "authentication", "security"]
        }
    }
]


async def bulk_ingest_via_api(documents: List[Dict], api_url: str = "http://localhost:8000"):
    """Send bulk ingestion request to the Python service API."""
    
    print(f"🚀 Starting bulk ingestion of {len(documents)} documents...")
    print(f"   Target API: {api_url}")
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{api_url}/api/bulk-ingest",
                json={"documents": documents}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Bulk Ingestion Complete!")
                print(f"   Total Documents: {result['total']}")
                print(f"   Successful: {result['successful']}")
                print(f"   Failed: {result['failed']}")
                
                print("\n📄 Individual Results:")
                for res in result['results']:
                    status_emoji = "✅" if res['status'] == 'COMPLETED' else "❌"
                    print(f"   {status_emoji} {res['title']}")
                    print(f"      → {res['chunk_count']} chunks | {res['message']}")
                
                # Summary
                total_chunks = sum(r['chunk_count'] for r in result['results'])
                print(f"\n📊 Summary:")
                print(f"   Total Chunks Indexed: {total_chunks}")
                print(f"   Average Chunks per Document: {total_chunks / result['total']:.1f}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
    except httpx.ConnectError:
        print(f"❌ Failed to connect to {api_url}")
        print("   Make sure the Python service is running!")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


async def main():
    """Main entry point."""
    print("=" * 60)
    print("VectorFlow Bulk Ingestion Script")
    print("=" * 60)
    
    await bulk_ingest_via_api(DOCUMENTS)
    
    print("\n" + "=" * 60)
    print("✨ Ingestion complete! You can now search and ask questions.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

