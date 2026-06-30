import logging
from app.models.loader import classify_text

logger = logging.getLogger(__name__)

PREDEFINED_CATEGORIES = [
    "business", "technology", "science", "education",
    "health", "entertainment", "sports", "politics",
    "legal", "personal", "finance", "medical",
    "research", "news", "documentation",
]


def classify_document(text: str) -> dict | None:
    return classify_text(text[:512], PREDEFINED_CATEGORIES)
