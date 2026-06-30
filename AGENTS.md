# Local AI - Developer Notes

## Run commands
```bash
# Install dependencies
pip install -r requirements.txt

# Download models (first run, requires internet)
python -c "from app.models.loader import load_embedding_model, load_ner_pipeline, load_classifier_pipeline; load_embedding_model(); load_ner_pipeline(); load_classifier_pipeline()"

# Run the server
python run.py

# Run tests
python -m pytest tests/ -v
```

## Architecture
- `app/main.py` - FastAPI server entry point
- `app/ingestion/` - Multi-modal input handlers (text, PDF, images)
- `app/processing/` - Text normalization and chunking
- `app/transformation/` - NER, classification, schema extraction
- `app/storage/` - SQLite persistence
- `app/models/` - Local SLM loading and caching
- `frontend/` - Web UI

## Offline-first
- Once models are cached, no internet needed
- All inference runs on CPU via Hugging Face transformers
- SQLite provides local persistence
- Graceful degradation when models unavailable
