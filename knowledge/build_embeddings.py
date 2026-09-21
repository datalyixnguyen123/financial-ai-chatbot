
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "processed" / "chunks.json"
OUTPUT_FILE = BASE_DIR / "processed" / "embeddings.json"
MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)


def build_embeddings():
    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        chunks = json.load(file)
    if not chunks:
        raise ValueError(
            "No chunks found."
        )
    texts = [
        chunk["text"]
        for chunk in chunks
    ]
    print(
        f"Loading embedding model: {MODEL_NAME}"
    )
    model = SentenceTransformer(
        MODEL_NAME
    )
    print(
        f"Encoding {len(texts)} chunks..."
    )
    vectors = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=True,
    )
    results = []
    for chunk, vector in zip(
        chunks,
        vectors,
    ):
        record = dict(chunk)

        record["embedding"] = vector.tolist()

        results.append(record)
    OUTPUT_FILE.write_text(
        json.dumps(
            results,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        f"Created {len(results)} embeddings."
    )
    print(
        f"Output: {OUTPUT_FILE}"
    )
    print(
        f"Embedding dimension: {vectors.shape[1]}"
    )


if __name__ == "__main__":
    build_embeddings()