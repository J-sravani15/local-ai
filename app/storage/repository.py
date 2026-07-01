import json
import logging
from typing import Any, Optional
from app.storage.database import get_connection

logger = logging.getLogger(__name__)


def _safe_row(row) -> dict:
    result: dict[str, Any] = {}
    for key in row.keys():
        val = row[key]
        if isinstance(val, bytes):
            val = val.decode("utf-8", errors="replace")
        result[key] = val
    return result


def insert_document(
    title: str,
    source: str,
    content_type: str,
    raw_text: str,
    char_count: int,
    word_count: int,
    page_count: int = 0,
) -> int:
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO documents (title, source, content_type, raw_text, char_count, word_count, page_count, processed)
               VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
            (title, source, content_type, raw_text, char_count, word_count, page_count),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_document_processed(doc_id: int):
    conn = get_connection()
    try:
        conn.execute("UPDATE documents SET processed = 1 WHERE id = ?", (doc_id,))
        conn.commit()
    finally:
        conn.close()


def get_document(doc_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, title, source, content_type, raw_text, char_count, word_count, page_count, processed, created_at "
            "FROM documents WHERE id = ?",
            (doc_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_all_documents(limit: int = 50, offset: int = 0) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, title, source, content_type, char_count, word_count, processed, created_at "
            "FROM documents ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_document(doc_id: int) -> bool:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        return False
    finally:
        conn.close()


def insert_entities(entities: list[dict]) -> list[int]:
    conn = get_connection()
    ids = []
    try:
        for ent in entities:
            cur = conn.execute(
                """INSERT INTO entities (document_id, entity_type, entity_value, confidence, context_start, context_end)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    ent["document_id"],
                    ent["entity_type"],
                    ent["entity_value"],
                    ent["confidence"],
                    ent.get("context_start", 0),
                    ent.get("context_end", 0),
                ),
            )
            ids.append(cur.lastrowid)
        conn.commit()
    finally:
        conn.close()
    return ids


def get_entities_by_document(doc_id: int) -> list[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, document_id, entity_type, entity_value, confidence, context_start, context_end "
            "FROM entities WHERE document_id = ? ORDER BY confidence DESC",
            (doc_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def insert_classification(classification: dict) -> int:
    if classification is None:
        return -1
    conn = get_connection()
    try:
        raw = classification.get("all_scores", {})
        if isinstance(raw, dict):
            clean = {}
            for k, v in raw.items():
                if isinstance(v, (int, float)):
                    clean[str(k)] = float(v)
                elif isinstance(v, str):
                    try:
                        clean[str(k)] = float(v)
                    except (ValueError, TypeError):
                        clean[str(k)] = 0.0
                else:
                    clean[str(k)] = 0.0
            all_scores_json = json.dumps(clean)
        else:
            all_scores_json = "{}"
        cur = conn.execute(
            """INSERT INTO classifications (document_id, category, confidence, all_scores)
               VALUES (?, ?, ?, ?)""",
            (
                classification["document_id"],
                classification["category"],
                classification["confidence"],
                all_scores_json,
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_classification_by_document(doc_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, document_id, category, confidence, all_scores "
            "FROM classifications WHERE document_id = ?",
            (doc_id,),
        ).fetchone()
        if row:
            result = dict(row)
            raw_scores = result.get("all_scores")
            if isinstance(raw_scores, str):
                result["all_scores"] = json.loads(raw_scores)
            else:
                result["all_scores"] = {}
            return result
        return None
    finally:
        conn.close()


def insert_summary(
    document_id: int, summary_text: str, suggested_tags: list[str]
) -> int:
    conn = get_connection()
    try:
        tags_json = json.dumps(suggested_tags)
        cur = conn.execute(
            "INSERT OR REPLACE INTO summaries (document_id, summary_text, suggested_tags) VALUES (?, ?, ?)",
            (document_id, summary_text, tags_json),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_summary_by_document(doc_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id, document_id, summary_text, suggested_tags "
            "FROM summaries WHERE document_id = ?",
            (doc_id,),
        ).fetchone()
        if row:
            result = dict(row)
            raw_tags = result.get("suggested_tags")
            if isinstance(raw_tags, str):
                result["suggested_tags"] = json.loads(raw_tags)
            else:
                result["suggested_tags"] = []
            return result
        return None
    finally:
        conn.close()


def insert_structured_output(document_id: int, data: dict) -> int:
    conn = get_connection()
    try:
        title = data.get("title", "")
        ai_summary = data.get("ai_summary", "")
        key_topics = json.dumps(data.get("key_topics", []))
        document_type = data.get("document_type", "other")
        sentiment = data.get("sentiment", "neutral")
        extracted_entities = json.dumps(data.get("extracted_entities", []))
        raw_json = json.dumps(data)
        cur = conn.execute(
            """INSERT OR REPLACE INTO structured_outputs
               (document_id, title, ai_summary, key_topics, document_type, sentiment, extracted_entities, raw_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                document_id,
                title,
                ai_summary,
                key_topics,
                document_type,
                sentiment,
                extracted_entities,
                raw_json,
            ),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_structured_output(document_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM structured_outputs WHERE document_id = ?", (document_id,)
        ).fetchone()
        if row:
            result = dict(row)
            for field in ("key_topics", "extracted_entities"):
                raw = result.get(field)
                if isinstance(raw, str):
                    result[field] = json.loads(raw)
                else:
                    result[field] = []
            raw_json = result.get("raw_json")
            if isinstance(raw_json, str):
                try:
                    result["raw_json"] = json.loads(raw_json)
                except (json.JSONDecodeError, TypeError):
                    result["raw_json"] = {}
            else:
                result["raw_json"] = {}
            return result
        return None
    finally:
        conn.close()


def search_documents(query: str) -> list[dict]:
    conn = get_connection()
    try:
        like_pattern = f"%{query}%"
        rows = conn.execute(
            """SELECT id, title, source, content_type, char_count, word_count, processed, created_at
               FROM documents
               WHERE raw_text LIKE ? OR title LIKE ?
               ORDER BY created_at DESC LIMIT 20""",
            (like_pattern, like_pattern),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
