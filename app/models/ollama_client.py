import json
import logging
import threading
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3:latest"
TIMEOUT = 300


def _call_ollama(prompt: str) -> str | None:
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 512, "temperature": 0.1},
    }).encode()
    req = urllib.request.Request(
        OLLAMA_API,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        logger.info(f"Calling Ollama ({OLLAMA_MODEL})...")
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
        body = resp.read().decode()
        data = json.loads(body)
        result = data.get("response", "").strip()
        logger.info("Ollama response received")
        return result
    except urllib.error.HTTPError as e:
        logger.error(f"Ollama HTTP error {e.code}: {e.reason}")
        return None
    except urllib.error.URLError as e:
        logger.error(f"Ollama connection failed: {e.reason}")
        return None
    except OSError as e:
        logger.error(f"Ollama OS error: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Ollama bad JSON response: {e}")
        return None


SUMMARY_PROMPT = """Summarize the following text in 1-3 concise sentences.
Return ONLY the summary, no extra commentary.

TEXT:
{text}

SUMMARY:"""


STRUCTURED_PROMPT = """Extract structured information from the text below.
Return ONLY valid JSON with these fields:
- "title": a short descriptive title
- "ai_summary": a 1-2 sentence summary
- "key_topics": an array of 3-6 key topics
- "document_type": one of "report", "article", "email", "note", "technical", "legal", "other"
- "sentiment": one of "positive", "negative", "neutral"
- "extracted_entities": array of {{"name": "...", "type": "person|organization|location|product|other"}}

TEXT:
{text}

JSON:"""


def _run_summary(text: str, document_id: int):
    from app.storage import repository as repo
    prompt = SUMMARY_PROMPT.format(text=text[:2000])
    result = _call_ollama(prompt)
    if result and len(result) > 10:
        try:
            existing = repo.get_summary_by_document(document_id)
            if existing:
                repo.insert_summary(document_id, result, [])
        except Exception as e:
            logger.warning(f"Failed to store Ollama summary: {e}")


def _run_structured_json(text: str, document_id: int):
    from app.storage import repository as repo
    prompt = STRUCTURED_PROMPT.format(text=text[:2000])
    raw = _call_ollama(prompt)
    if not raw:
        return
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        cleaned = cleaned.rsplit("```", 1)[0]
    parsed = None
    try:
        parsed = json.loads(cleaned.strip())
    except json.JSONDecodeError:
        logger.warning("Ollama returned invalid JSON, attempting extraction...")
        try:
            start = cleaned.index("{")
            end = cleaned.rindex("}") + 1
            parsed = json.loads(cleaned[start:end])
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Could not parse Ollama response: {e}")
            return
    if parsed is None:
        return
    try:
        repo.insert_structured_output(document_id, parsed)
        logger.info(f"Structured output saved for document {document_id}")
    except Exception as e:
        logger.error(f"Failed to save structured output: {e}")


def schedule_ollama_tasks(text: str, document_id: int):
    if not text or len(text.strip()) < 20:
        return
    t1 = threading.Thread(target=_run_summary, args=(text, document_id), daemon=True)
    t1.start()
    t2 = threading.Thread(target=_run_structured_json, args=(text, document_id), daemon=True)
    t2.start()
    logger.info(f"Scheduled Ollama background tasks for document {document_id}")


def ollama_summary(text: str) -> str | None:
    if not text or len(text.strip()) < 20:
        return None
    prompt = SUMMARY_PROMPT.format(text=text[:2000])
    return _call_ollama(prompt)


def ollama_structured_json(text: str) -> dict | None:
    if not text or len(text.strip()) < 20:
        return None
    prompt = STRUCTURED_PROMPT.format(text=text[:2000])
    raw = _call_ollama(prompt)
    if not raw:
        return None
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        cleaned = cleaned.rsplit("```", 1)[0]
    try:
        return json.loads(cleaned.strip())
    except json.JSONDecodeError:
        logger.warning("Ollama returned invalid JSON, attempting extraction...")
        try:
            start = cleaned.index("{")
            end = cleaned.rindex("}") + 1
            return json.loads(cleaned[start:end])
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Could not parse Ollama response: {e}")
            return None
