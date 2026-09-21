
import json
from pathlib import Path
import faiss
import numpy as np


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "processed" / "embeddings.json"
INDEX_FILE = (
    BASE_DIR
    / "processed"
    / "financial_knowledge.index"
)
METADATA_FILE = (
    BASE_DIR
    / "processed"
    / "financial_knowledge_metadata.json"
)


def build_faiss_index():
    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        records = json.load(file)
    if not records:
        raise ValueError(
            "No embeddings found."
        )
    embeddings = np.array(
        [
            record["embedding"]
            for record in records
        ],
        dtype="float32",
    )
    if embeddings.ndim != 2:
        raise ValueError(
            "Embeddings must be a 2D array."
        )
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(
        dimension
    )
    index.add(embeddings)
    metadata = []

    for record in records:
        record_metadata = {
            key: value
            for key, value in record.items()
            if key != "embedding"
        }
        metadata.append(
            record_metadata
        )

    faiss.write_index(
        index,
        str(INDEX_FILE),
    )
    METADATA_FILE.write_text(
        json.dumps(
            metadata,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        f"Indexed {index.ntotal} chunks."
    )
    print(
        f"Vector dimension: {dimension}"
    )
    print(
        f"Index: {INDEX_FILE}"
    )
    print(
        f"Metadata: {METADATA_FILE}"
    )


if __name__ == "__main__":
    build_faiss_index()