import logging
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import UPLOAD_DIR, SUPPORTED_EXTENSIONS
from app.storage.database import init_db
from app.storage import repository as repo
from app.ingestion.text_ingestor import ingest_text, ingest_text_file
from app.ingestion.pdf_ingestor import ingest_pdf
from app.ingestion.image_ingestor import ingest_image
from app.processing.normalizer import normalize_pipeline
from app.processing.chunker import chunk_text
from app.transformation.extractor import extract_structured_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _ensure_serializable(obj):
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if isinstance(v, bytes):
                obj[k] = v.decode("utf-8", errors="replace")
            elif isinstance(v, (dict, list)):
                _ensure_serializable(v)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, bytes):
                obj[i] = v.decode("utf-8", errors="replace")
            elif isinstance(v, (dict, list)):
                _ensure_serializable(v)


app = FastAPI(title="Local AI - Document Intelligence Pipeline")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("Application started - offline CPU-first AI pipeline ready")


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")

@app.get("/")
def serve_frontend():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/health")
def health_check():
    return {"status": "ok", "mode": "offline", "engine": "cpu-first"}


@app.post("/api/ingest/text")
def ingest_text_endpoint(
    text: str = Form(...),
    title: str = Form(""),
):
    try:
        raw = ingest_text(text)
        normalized = normalize_pipeline(raw["raw_text"])
        chunks = chunk_text(normalized)
        doc_id = repo.insert_document(
            title=title or "Untitled Text",
            source=raw["source"],
            content_type="text",
            raw_text=normalized,
            char_count=raw["char_count"],
            word_count=raw["word_count"],
        )
        structured = extract_structured_data(normalized, doc_id)
        if structured["entities"]:
            repo.insert_entities(structured["entities"])
        if structured["classification"]:
            repo.insert_classification(structured["classification"])
        if structured["summary"]:
            repo.insert_summary(doc_id, structured["summary"], structured["suggested_tags"])
        repo.update_document_processed(doc_id)
        return {
            "document_id": doc_id,
            "title": title or "Untitled Text",
            "char_count": raw["char_count"],
            "word_count": raw["word_count"],
            "chunks": len(chunks),
            "entities_found": len(structured["entities"]),
            "classification": structured["classification"],
            "summary": structured["summary"],
            "suggested_tags": structured["suggested_tags"],
            "status": "processed",
            "ollama_background": True,
        }
    except Exception as e:
        logger.exception("Text ingestion failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ingest/file")
async def ingest_file_endpoint(file: UploadFile = File(...)):
    try:
        ext = Path(file.filename).suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {ext}. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
            )
        file_path = UPLOAD_DIR / file.filename
        file_path = file_path.resolve()
        if not str(file_path).startswith(str(UPLOAD_DIR.resolve())):
            raise HTTPException(status_code=400, detail="Invalid file path")
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        if ext == ".pdf":
            raw = ingest_pdf(file_path)
        elif ext in {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}:
            raw = ingest_image(file_path)
        else:
            raw = ingest_text_file(file_path)
        raw["raw_text"] = raw.get("raw_text", "")
        normalized = normalize_pipeline(raw["raw_text"])
        chunks = chunk_text(normalized)
        doc_id = repo.insert_document(
            title=file.filename,
            source=file.filename,
            content_type=raw.get("content_type", ext.lstrip(".")),
            raw_text=normalized,
            char_count=raw.get("char_count", 0),
            word_count=raw.get("word_count", 0),
            page_count=raw.get("page_count", 0),
        )
        structured = extract_structured_data(normalized, doc_id)
        if structured["entities"]:
            repo.insert_entities(structured["entities"])
        if structured["classification"]:
            repo.insert_classification(structured["classification"])
        if structured["summary"]:
            repo.insert_summary(doc_id, structured["summary"], structured["suggested_tags"])
        repo.update_document_processed(doc_id)
        return {
            "document_id": doc_id,
            "filename": file.filename,
            "content_type": raw.get("content_type", ext.lstrip(".")),
            "char_count": raw.get("char_count", 0),
            "word_count": raw.get("word_count", 0),
            "chunks": len(chunks),
            "entities_found": len(structured["entities"]),
            "classification": structured["classification"],
            "summary": structured["summary"],
            "suggested_tags": structured["suggested_tags"],
            "status": "processed",
            "ollama_background": True,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("File ingestion failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents")
def list_documents(limit: int = 50, offset: int = 0):
    docs = repo.get_all_documents(limit, offset)
    return {"documents": docs, "total": len(docs)}


@app.get("/api/documents/{doc_id}")
def get_document(doc_id: int):
    doc = repo.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    entities = repo.get_entities_by_document(doc_id)
    classification = repo.get_classification_by_document(doc_id)
    summary = repo.get_summary_by_document(doc_id)
    structured_output = repo.get_structured_output(doc_id)
    result = {
        "document": doc,
        "entities": entities,
        "classification": classification,
        "summary": summary,
        "structured_output": structured_output,
    }
    _ensure_serializable(result)
    return result


@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: int):
    success = repo.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "deleted", "document_id": doc_id}


@app.get("/api/search")
def search_documents(q: str = ""):
    if not q:
        return {"results": []}
    results = repo.search_documents(q)
    return {"results": results, "query": q}


@app.get("/api/stats")
def get_stats():
    docs = repo.get_all_documents(limit=10000)
    total_docs = len(docs)
    processed = sum(1 for d in docs if d["processed"])
    total_chars = sum(d["char_count"] for d in docs)
    total_words = sum(d["word_count"] for d in docs)
    return {
        "total_documents": total_docs,
        "processed": processed,
        "total_chars": total_chars,
        "total_words": total_words,
    }
