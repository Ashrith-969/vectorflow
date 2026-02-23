import asyncio
import aiohttp
import time

BASE_URL = "http://localhost:8000/api"
QUERIES = [
    "What is OpenAI?",
    "How does Codex work?",
    "What is Cursor editor?",
    "Explain vector embeddings",
    "What is RAG?",
]

async def search(session, query, req_id):
    start = time.time()
    async with session.post(f"{BASE_URL}/search", json={"query": query, "limit": 3}) as resp:
        await resp.read()
        elapsed = time.time() - start
        print(f"  Request {req_id} ({query[:25]}...): {elapsed:.3f}s  [HTTP {resp.status}]")
        return elapsed

async def main():
    print("=== Sequential (one at a time) ===")
    seq_start = time.time()
    async with aiohttp.ClientSession() as session:
        for i, q in enumerate(QUERIES):
            await search(session, q, i)
    seq_total = time.time() - seq_start
    print(f"  Total: {seq_total:.3f}s\n")

    print("=== Parallel (all at once) ===")
    par_start = time.time()
    async with aiohttp.ClientSession() as session:
        tasks = [search(session, q, i) for i, q in enumerate(QUERIES)]
        await asyncio.gather(*tasks)
    par_total = time.time() - par_start
    print(f"  Total: {par_total:.3f}s\n")

    speedup = seq_total / par_total
    print(f"Speedup: {speedup:.1f}x")
    if speedup > 2.0:
        print("Parallelism is working!")
    elif speedup > 1.3:
        print("Some parallelism detected, but limited.")
    else:
        print("WARNING: No significant speedup - check async implementation.")

asyncio.run(main())