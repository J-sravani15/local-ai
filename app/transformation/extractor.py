import logging
from app.models.loader import extract_entities, classify_text, get_embedding
from app.models.ollama_client import schedule_ollama_tasks, ollama_summary, ollama_structured_json

logger = logging.getLogger(__name__)


def extract_structured_data(text: str, document_id: int) -> dict:
    entities_result = extract_entities(text)
    entities = []
    for ent in entities_result:
        entities.append({
            "document_id": document_id,
            "entity_type": ent["entity"],
            "entity_value": ent["word"],
            "confidence": ent["score"],
            "context_start": ent["start"],
            "context_end": ent["end"],
        })

    classification_result = classify_text(text[:512])
    classification = None
    if classification_result:
        classification = {
            "document_id": document_id,
            "category": classification_result["top_label"],
            "confidence": classification_result["top_score"],
            "all_scores": dict(zip(
                classification_result["labels"],
                classification_result["scores"],
            )),
        }

    summary = generate_summary(text)

    embedding = get_embedding(text[:512])
    embeddings_data = None
    if embedding:
        embeddings_data = {
            "document_id": document_id,
            "chunk_id": 0,
            "embedding": embedding,
        }

    top_entities = sorted(entities, key=lambda e: e["confidence"], reverse=True)[:5]
    suggested_tags = list(set(e["entity_value"].lower() for e in top_entities if e["confidence"] > 0.5))

    schedule_ollama_tasks(text, document_id)
    logger.info(f"Scheduled Ollama background processing for doc {document_id}")

    return {
        "entities": entities,
        "classification": classification,
        "summary": summary,
        "suggested_tags": suggested_tags,
        "embedding": embeddings_data,
        "structured_json": None,
    }


def generate_summary(text: str, max_sentences: int = 3) -> str:
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if len(sentences) <= max_sentences:
        return text.strip()
    return " ".join(sentences[:max_sentences]).strip()
