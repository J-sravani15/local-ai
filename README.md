# Local AI Document Intelligence 

## Overview

The Local AI Document Intelligence Pipeline is an offline AI-powered document analysis system that processes text and document files without relying on external AI APIs. It uses FastAPI as the backend, Ollama for local Large Language Model (LLM) inference, and a modern frontend to provide intelligent document understanding.

The application supports document ingestion, text extraction, named entity recognition, document classification, summarization, and structured JSON generation using locally running AI models.

---

## Features

- Upload and analyze PDF, TXT, DOC, DOCX, PNG, JPG, BMP and TIFF files
-  Analyze manually entered text
-  Local AI inference using Ollama
-  Automatic document summarization
-  Named Entity Recognition (NER)
-  Document classification
-  Key topic extraction
-  Structured JSON output generation
-  Download structured output as JSON
-  Search processed documents
-  Completely offline (No external AI APIs)

---

## Tech Stack

### Backend
- Python 3.x
- FastAPI
- SQLite
- Ollama
- Transformers
- Sentence Transformers

### Frontend
- HTML
- CSS
- JavaScript

### AI Models
- phi3:mini
- nomic-embed-text
- DistilBERT NER
- all-MiniLM-L6-v2

---

## Project Structure

```
localai/
│
├── app/
│   ├── ingestion/
│   ├── processing/
│   ├── storage/
│   ├── transformation/
│   ├── models/
│   └── main.py
│
├── frontend/
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── uploads/
├── tests/
├── model_cache/
├── requirements.txt
├── run.py
└── README.md
```

---

## Installation

### Clone the repository

```bash
git clone https://code.swecha.org/sravani15/localai.git
cd localai
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Virtual Environment

Windows

```bash
.venv\Scripts\activate
```

Linux/macOS

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Install Ollama

Download and install Ollama from:

https://ollama.com/download

Install the required models:

```bash
ollama pull phi3:mini
ollama pull nomic-embed-text
```

Verify installation:

```bash
ollama list
```

Expected output:

```
phi3:mini
nomic-embed-text
```

---

## Running the Project

Start Ollama:

```bash
ollama serve
```

Run the application:

```bash
python run.py
```

Open in browser:

```
http://127.0.0.1:8000
```

---

## Workflow

1. Upload a document or enter text.
2. Extract text content.
3. Perform Named Entity Recognition.
4. Classify the document.
5. Generate document summary.
6. Generate structured JSON using Ollama.
7. Display results in the frontend.
8. Download JSON output.

---

## Structured Output Example

```json
{
  "title": "Sales Management",
  "ai_summary": "Introduction to Sales Management...",
  "key_topics": [
    "Sales Planning",
    "Marketing",
    "Distribution"
  ],
  "document_type": "report",
  "sentiment": "neutral",
  "extracted_entities": [
    {
      "name": "American Marketing Association",
      "type": "organization"
    }
  ]
}
```

---

## API Endpoints

### Upload Document

```
POST /api/upload
```

### Analyze Text

```
POST /api/ingest
```

### Get Documents

```
GET /api/documents
```

### Get Document Details

```
GET /api/documents/{id}
```

---

## Technologies Used

- FastAPI
- SQLite
- Ollama
- Python
- HTML
- CSS
- JavaScript
- HuggingFace Transformers
- Sentence Transformers

---

## Future Enhancements

- Audio file analysis
- Video transcription and analysis
- Semantic search using embeddings
- RAG-based document chatbot
- Multi-language support
- Export reports as PDF
- Docker deployment
- Cloud deployment

---

## Screenshots

Add screenshots of:

- Home Page
- Upload Page
- Document Analysis
- Structured Output Panel

---

## Author

**Sravani Jagarlamudi**

GitHub:
https://github.com/J-sravani15

GitLab:
https://code.swecha.org/sravani15/localai

---

## License

This project was developed as part of an internship/hackathon assignment for educational purposes.

---