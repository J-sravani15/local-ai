from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class DocumentSchema(BaseModel):
    id: Optional[int] = None
    title: str = ""
    source: str = ""
    content_type: str = "text"
    raw_text: str = ""
    char_count: int = 0
    word_count: int = 0
    page_count: int = 0
    processed: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class EntitySchema(BaseModel):
    id: Optional[int] = None
    document_id: int
    entity_type: str
    entity_value: str
    confidence: float = 0.0
    context_start: int = 0
    context_end: int = 0


class ClassificationSchema(BaseModel):
    id: Optional[int] = None
    document_id: int
    category: str
    confidence: float = 0.0
    all_scores: Optional[dict] = None


class EmbeddingSchema(BaseModel):
    id: Optional[int] = None
    document_id: int
    chunk_id: int
    embedding: list[float]


class ExtractedDataSchema(BaseModel):
    document: DocumentSchema
    entities: list[EntitySchema] = []
    classification: Optional[ClassificationSchema] = None
    summary: str = ""
    suggested_tags: list[str] = []


def document_schema_sql() -> str:
    return """
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT DEFAULT '',
        source TEXT DEFAULT '',
        content_type TEXT DEFAULT 'text',
        raw_text TEXT DEFAULT '',
        char_count INTEGER DEFAULT 0,
        word_count INTEGER DEFAULT 0,
        page_count INTEGER DEFAULT 0,
        processed INTEGER DEFAULT 0,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS entities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        entity_type TEXT NOT NULL,
        entity_value TEXT NOT NULL,
        confidence REAL DEFAULT 0.0,
        context_start INTEGER DEFAULT 0,
        context_end INTEGER DEFAULT 0,
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS classifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        confidence REAL DEFAULT 0.0,
        all_scores TEXT,
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL,
        chunk_id INTEGER DEFAULT 0,
        embedding BLOB,
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS summaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL UNIQUE,
        summary_text TEXT DEFAULT '',
        suggested_tags TEXT DEFAULT '',
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS structured_outputs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER NOT NULL UNIQUE,
        title TEXT DEFAULT '',
        ai_summary TEXT DEFAULT '',
        key_topics TEXT DEFAULT '[]',
        document_type TEXT DEFAULT 'other',
        sentiment TEXT DEFAULT 'neutral',
        extracted_entities TEXT DEFAULT '[]',
        raw_json TEXT DEFAULT '{}',
        FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
    );

    CREATE INDEX IF NOT EXISTS idx_entities_doc ON entities(document_id);
    CREATE INDEX IF NOT EXISTS idx_classifications_doc ON classifications(document_id);
    CREATE INDEX IF NOT EXISTS idx_embeddings_doc ON embeddings(document_id);
    CREATE INDEX IF NOT EXISTS idx_structured_doc ON structured_outputs(document_id);
    """
