"""
rag.py
Retrieval-Augmented Generation: given a user question, find the most
relevant chunks from the RBI knowledge base to ground the LLM's answer.

Two retrieval strategies are provided:

1. semantic_retrieve() -- the "real" approach: embeds chunks and the
   query into vectors using a sentence-transformer model, stores them in
   ChromaDB, and finds nearest neighbors by meaning, not exact words.
   Needs `sentence-transformers` and `chromadb` installed.

   MODEL CHOICE: uses "all-MiniLM-L6-v2" (~80MB), not a larger model like
   BAAI/bge-large (~1.3GB). Streamlit Community Cloud's free tier gives
   roughly 1GB RAM total -- a 1.3GB model alone would likely crash the
   app. MiniLM is smaller and faster, with a well-established track
   record for retrieval quality at this scale; the accuracy tradeoff vs.
   a larger model is real but modest for a knowledge base this size (a
   handful of policy documents, not millions).

   AUTO-BUILD: semantic_retrieve() builds the vector store automatically
   on first call if it doesn't exist yet, and reuses it afterward -- no
   separate manual "indexing step" required.

2. tfidf_retrieve() -- a keyword-based fallback using scikit-learn's
   TF-IDF + cosine similarity. Works with zero extra installs (sklearn is
   already a dependency), and is TESTED below on the real knowledge base.
   It won't catch synonyms/paraphrasing the way semantic search does
   (e.g. searching "rate cut" won't match text that only says "reduced
   the repo rate" as well as embeddings would).

retrieve() at the bottom is the function other modules (agent.py) should
actually call -- it tries semantic first and falls back to TF-IDF if the
embedding libraries aren't installed, so the rest of the app doesn't need
to know or care which one ran.
"""

from ingest import build_chunk_index, Chunk

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # ~80MB, fits free-tier hosting


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
    Safe to call repeatedly -- upsert overwrites existing entries rather
    than duplicating them, so re-running this after adding a new document
    to the knowledge base just adds the new chunks."""
    import chromadb
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(collection_name)

    texts = [c.text for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=False).tolist()
    ids = [f"{c.source}-{c.chunk_id}" for c in chunks]
    metadatas = [{"source": c.source, "chunk_id": c.chunk_id} for c in chunks]

    collection.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    return collection


def semantic_retrieve(query: str, collection_name: str = "rbi_policy", persist_dir: str = "./chroma_db", top_k: int = 3):
    """Embed the query and find the top_k nearest chunks by meaning.
    Auto-builds the vector store on first call if it doesn't exist yet or
    is empty (e.g. a new document was added to the knowledge base)."""
    import chromadb
    from sentence_transformers import SentenceTransformer

    client = chromadb.PersistentClient(path=persist_dir)
    collection = client.get_or_create_collection(collection_name)

    if collection.count() == 0:
        chunks = build_chunk_index()
        collection = build_vector_store(chunks, collection_name, persist_dir)

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    query_embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=top_k)

    # Reshape to look like tfidf_retrieve's output: list of (Chunk, score)
    output = []
    for doc, meta, distance in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        chunk = Chunk(text=doc, source=meta["source"], chunk_id=meta["chunk_id"])
        similarity = 1 - distance  # Chroma returns distance; convert to a similarity-like score
        output.append((chunk, similarity))
    return output


# ---------------------------------------------------------------------------
# Unified entry point -- use this from other modules
# ---------------------------------------------------------------------------
def retrieve(query: str, chunks: list[Chunk] = None, top_k: int = 3):
    """Tries semantic retrieval first; falls back to TF-IDF if the
    embedding libraries aren't installed. Callers don't need to know
    which one actually ran -- check the returned `mode` if you want to
    display it (see agent.py)."""
    try:
        results = semantic_retrieve(query, top_k=top_k)
        return results, "semantic"
    except (ImportError, ModuleNotFoundError):
        if chunks is None:
            chunks = build_chunk_index()
        results = tfidf_retrieve(query, chunks, top_k=top_k)
        return results, "tfidf"


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
        results, mode = retrieve(q, chunks, top_k=2)
        print(f"  (retrieval mode used: {mode})")
        for chunk, score in results:
            preview = chunk.text.replace("\n", " ")[:150]
            print(f"  [score={score:.3f}] ({chunk.source} #{chunk.chunk_id}) {preview}...")
        print()
   
