import logging
from functools import lru_cache
from app.config import MODEL_CONFIG, MODEL_CACHE_DIR

logger = logging.getLogger(__name__)


class ModelLoadError(Exception):
    pass


@lru_cache(maxsize=1)
def load_embedding_model():
    try:
        from sentence_transformers import SentenceTransformer
        model_name = MODEL_CONFIG["embedding_model"]
        logger.info(f"Loading embedding model: {model_name}")
        model = SentenceTransformer(
            model_name,
            cache_folder=str(MODEL_CACHE_DIR),
            device=MODEL_CONFIG["device"],
        )
        logger.info("Embedding model loaded successfully")
        return model
    except Exception as e:
        logger.warning(f"Failed to load embedding model: {e}")
        return None


@lru_cache(maxsize=1)
def load_ner_pipeline():
    try:
        from transformers import pipeline
        model_name = MODEL_CONFIG["ner_model"]
        logger.info(f"Loading NER pipeline: {model_name}")
        ner = pipeline(
            "ner",
            model=model_name,
            tokenizer=model_name,
            device=-1,
            model_kwargs={"cache_dir": str(MODEL_CACHE_DIR)},
        )
        logger.info("NER pipeline loaded successfully")
        return ner
    except Exception as e:
        logger.warning(f"Failed to load NER pipeline: {e}")
        return None


@lru_cache(maxsize=1)
def load_classifier_pipeline():
    try:
        from transformers import pipeline
        model_name = MODEL_CONFIG["classifier_model"]
        logger.info(f"Loading zero-shot classifier: {model_name}")
        classifier = pipeline(
            "zero-shot-classification",
            model=model_name,
            tokenizer=model_name,
            device=-1,
            model_kwargs={"cache_dir": str(MODEL_CACHE_DIR)},
        )
        logger.info("Classifier loaded successfully")
        return classifier
    except Exception as e:
        logger.warning(f"Failed to load classifier: {e}")
        return None


def get_embedding(text: str) -> list[float] | None:
    model = load_embedding_model()
    if model is None:
        return None
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def extract_entities(text: str) -> list[dict]:
    ner = load_ner_pipeline()
    if ner is None:
        return []
    results = ner(text)
    entities = []
    for r in results:
        entities.append({
            "entity": r["entity"],
            "word": r["word"],
            "score": round(r["score"], 4),
            "start": r["start"],
            "end": r["end"],
        })
    return entities


def classify_text(text: str, labels: list[str] | None = None) -> dict | None:
    classifier = load_classifier_pipeline()
    if classifier is None:
        return None
    if labels is None:
        labels = [
            "business", "technology", "finance", "research",
            "education", "legal", "healthcare", "news",
            "personal", "science",
        ]
    result = classifier(text, labels)
    return {
        "labels": result["labels"],
        "scores": [round(s, 4) for s in result["scores"]],
        "top_label": result["labels"][0],
        "top_score": round(result["scores"][0], 4),
    }
