from app.config import CHUNK_CONFIG


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[dict]:
    if chunk_size is None:
        chunk_size = CHUNK_CONFIG["chunk_size"]
    if overlap is None:
        overlap = CHUNK_CONFIG["chunk_overlap"]

    words = text.split()
    if len(words) <= chunk_size:
        return [{"chunk_id": 0, "text": text, "word_count": len(words), "char_count": len(text)}]

    chunks = []
    start = 0
    chunk_id = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunk_text_str = " ".join(chunk_words)
        chunks.append({
            "chunk_id": chunk_id,
            "text": chunk_text_str,
            "word_count": len(chunk_words),
            "char_count": len(chunk_text_str),
            "start_word_idx": start,
            "end_word_idx": end,
        })
        chunk_id += 1
        start += chunk_size - overlap

    return chunks
