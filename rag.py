"""
rag.py
Retrieval-Augmented Generation: given a user question, find the most
relevant chunks from the RBI knowledge base to ground the LLM's answer.

Two retrieval strategies are provided:

1. semantic_retrieve() -- the "real" approach: embeds chunks and the
   query into vectors using a sentence-transformer model, stores them in
   ChromaDB, and finds nearest neighbors by meaning, not exact words.
   Needs `sentence-transformers` and `chromadb` installed.

2. tfidf_retrieve() -- a keyword-based fallback using scikit-learn's
   TF-IDF + cosine similarity. Works with zero extra installs (sklearn is
   already a dependency), and is TESTED below on the real knowledge base.
   It won't catch synonyms/paraphrasing the way semantic search does
   (e.g. searching "rate cut" won't match text that only says "reduced
   the repo rate" as well as embeddings would), but for a small, keyword-
   rich knowledge base like policy statements, it's a genuinely useful
   fallback -- and a good way to *see* retrieval working before adding
   the embedding-model dependency.
"""

from ingest import build_chunk_index, Chunk


# ---------------------------------------------------------------------------
# TESTED: TF-IDF retrieval (sklearn only)
# ---------------------------------------------------------------------------
def tfidf_retrieve(query: str, chunks: list[Chunk], top_k: int = 3):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    texts = [c.text for c in chunks]
    vectorizer = TfidfVectorizer(stop_words="english")
    chunk_vectors = vectorizer.fit_transform(texts)
    query_vector = vectorizer.transform([query])

    similarities = cosine_similarity(query_vector, chunk_vectors)[0]
    ranked = sorted(zip(chunks, similarities), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]


# ---------------------------------------------------------------------------
# REAL: Semantic retrieval (needs sentence-transformers + chromadb)
# ---------------------------------------------------------------------------
def build_vector_store(chunks: list[Chunk], collection_name: str = "rbi_policy", persist_dir: str = "./chroma_db"):
    """Embed all chunks and store them in a persistent ChromaDB collection.
    Run once (or whenever the knowledge base changes) -- not on every query."""
    import chromadb
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("BAAI/bge-large-en-v1.5")  # free, runs locally
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(collection_name)

    texts = [c.text for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=False).tolist()
    ids = [f"{c.source}-{c.chunk_id}" for c in chunks]
    metadatas = [{"source": c.source, "chunk_id": c.chunk_id} for c in chunks]

    collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    return collection


def semantic_retrieve(query: str, collection_name: str = "rbi_policy", persist_dir: str = "./chroma_db", top_k: int = 3):
    """Embed the query and find the top_k nearest chunks by meaning."""
    import chromadb
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_collection(collection_name)

    query_embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)
    return list(zip(results["documents"][0], results["metadatas"][0], results["distances"][0]))


if __name__ == "__main__":
    chunks = build_chunk_index()
    print(f"Indexed {len(chunks)} chunks from knowledge base\n")

    test_queries = [
        "Why did the RBI raise its inflation forecast?",
        "What did the RBI do to support the rupee?",
        "What is the current repo rate?",
    ]

    for q in test_queries:
        print("=" * 70)
        print(f"QUERY: {q}")
        print("=" * 70)
        results = tfidf_retrieve(q, chunks, top_k=2)
        for chunk, score in results:
            preview = chunk.text.replace("\n", " ")[:150]
            print(f"  [score={score:.3f}] ({chunk.source} #{chunk.chunk_id}) {preview}...")
        print()
