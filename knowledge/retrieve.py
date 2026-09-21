
import json
from pathlib import Path
import faiss
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "processed" / "financial_knowledge.index"
METADATA_FILE = BASE_DIR / "processed" / "financial_knowledge_metadata.json"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def load_retriever():
    index = faiss.read_index(str(INDEX_FILE))
    with METADATA_FILE.open("r", encoding="utf-8") as file:
        metadata = json.load(file)
    model = SentenceTransformer(MODEL_NAME)
    return index, metadata, model


def retrieve(query: str, top_k: int = 3):
    index, metadata, model = load_retriever()
    query_vector = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    scores, indices = index.search(
        query_vector.astype("float32"),
        top_k,
    )

    results = []
    for score, index_position in zip(
        scores[0],
        indices[0],
    ):
        if index_position < 0:
            continue
        result = metadata[index_position].copy()
        result["score"] = float(score)

        results.append(result)

    return results


if __name__ == "__main__":
    query = "Làm thế nào để lập ngân sách cá nhân?"
    results = retrieve(query, top_k=3)
    print(f"\nQuery: {query}\n")
    for rank, result in enumerate(results, start=1):
        print(f"--- Result {rank} ---")
        print(f"Score: {result['score']:.4f}")
        print(f"Chunk: {result['chunk_id']}")
        print(f"Topic: {result['topic']}")
        print(f"Source: {result['source']}")
        print(f"Text:\n{result['text']}")
        print()