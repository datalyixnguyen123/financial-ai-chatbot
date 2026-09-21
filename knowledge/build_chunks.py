
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "sources"
METADATA_FILE = BASE_DIR / "metadata" / "sources.json"
OUTPUT_DIR = BASE_DIR / "processed"
OUTPUT_FILE = OUTPUT_DIR / "chunks.json"
CHUNK_SIZE = 500


def load_source_metadata():
    with METADATA_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    documents = data.get("documents")
    if not isinstance(documents, list):
        raise ValueError(
            "sources.json must contain a 'documents' list."
        )
    metadata_by_file = {}

    for document in documents:
        file_name = document.get("file")
        if not file_name:
            raise ValueError(
                f"Missing 'file' in metadata: {document}"
            )
        if file_name in metadata_by_file:
            raise ValueError(
                f"Duplicate metadata for file: {file_name}"
            )
        metadata_by_file[file_name] = document

    return metadata_by_file


def chunk_markdown(text: str, chunk_size: int = CHUNK_SIZE):
    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) <= chunk_size:
            if current_chunk:
                current_chunk += "\n\n"
            current_chunk += paragraph
        else:
            if current_chunk:
                chunks.append(current_chunk)

            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def build_chunks():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metadata_by_file = load_source_metadata()
    source_files = sorted(
        SOURCE_DIR.glob("*.md")
    )

    if not source_files:
        raise ValueError(
            f"No Markdown files found in {SOURCE_DIR}"
        )

    all_chunks = []

    for source_file in source_files:
        file_name = source_file.name
        if file_name not in metadata_by_file:
            raise ValueError(
                f"Missing metadata for file: {file_name}"
            )
        metadata = metadata_by_file[file_name]
        document_id = metadata["id"]
        topic = metadata["topic"]
        text = source_file.read_text(
            encoding="utf-8"
        )
        chunks = chunk_markdown(text)
        for index, chunk in enumerate(
            chunks,
            start=1,
        ):
            chunk_record = {
                **metadata,
                "chunk_id": (
                    f"{document_id}_chunk_{index:03d}"
                ),
                "text": chunk,
            }

            all_chunks.append(chunk_record)

    OUTPUT_FILE.write_text(
        json.dumps(
            all_chunks,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        f"Found {len(source_files)} source files."
    )
    print(
        f"Created {len(all_chunks)} chunks."
    )
    print(
        f"Output: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    build_chunks()