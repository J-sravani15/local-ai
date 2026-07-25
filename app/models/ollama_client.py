import json
import logging
import threading
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)

OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:latest"
TIMEOUT = 300


def _call_ollama(prompt: str) -> str | None:
    payload = json.dumps(
        {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 512, "temperature": 0.1},
        }
    ).encode()
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


def _extract_json_str(raw: str) -> str | None:
    cleaned = raw.strip()
    if "```" in cleaned:
        parts = cleaned.split("```")
        for i in range(1, len(parts), 2):
            candidate = parts[i].strip()
            if candidate.lower().startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("{"):
                return candidate
    try:
        start = cleaned.index("{")
        end = cleaned.rindex("}") + 1
        return cleaned[start:end]
    except ValueError:
        pass
    return None


def _call_ollama_json(prompt: str, max_retries: int = 2) -> dict | None:
    last_raw = None
    last_error = None
    for attempt in range(1 + max_retries):
        raw = _call_ollama(prompt)
        if not raw:
            last_error = "Ollama returned empty response"
            continue
        last_raw = raw
        extracted = _extract_json_str(raw)
        if not extracted:
            last_error = "Could not extract JSON string from response"
            continue
        try:
            parsed = json.loads(extracted)
            if isinstance(parsed, dict):
                return parsed
            last_error = f"Parsed JSON is not a dict, got {type(parsed).__name__}"
        except json.JSONDecodeError as e:
            last_error = str(e)
    logger.error("All Ollama retries exhausted for structured JSON request")
    logger.error(f"Raw Ollama response: {last_raw}")
    if last_error:
        logger.error(f"Parsing error: {last_error}")
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
    parsed = _call_ollama_json(prompt)
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
    t2 = threading.Thread(
        target=_run_structured_json, args=(text, document_id), daemon=True
    )
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
    return _call_ollama_json(prompt)
