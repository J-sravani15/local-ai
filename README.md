# Local AI Document Intelligence 

## Overview

The Local AI Document Intelligence Pipeline is an offline AI-powered document analysis system that processes text and document files without relying on external AI APIs. It uses FastAPI as the backend, Ollama for local Large Language Model (LLM) inference, and a modern frontend to provide intelligent document understanding.

The application supports document ingestion, text extraction, named entity recognition, document classification, summarization, and structured JSON generation using locally running AI models.

## Features

<<<<<<< HEAD
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
=======
- Offline-first AI processing
- CPU-optimized inference
- PDF and text document ingestion
- Named Entity Recognition (NER)
- Automatic document classification
- AI-generated summaries
- Structured JSON generation using Ollama (phi3:mini)
- SQLite local storage
- Searchable document history
- Download structured JSON
- Real-time dashboard statistics

---

## Technology Stack

### Backend

- FastAPI
- Python
- SQLite

### AI Models

- Ollama
- phi3:mini
- Hugging Face Transformers
- sentence-transformers

### Frontend

- HTML
- CSS
- JavaScript

---

## Project Architecture

Document Upload

↓

Text Extraction

↓

Named Entity Recognition

↓

Document Classification

↓

Summary Generation

↓

Structured JSON Generation (phi3:mini)

↓

SQLite Storage

↓

Frontend Visualization

---

## Installation

Clone the repository

```bash
git clone <repository-url>
cd localai
```

Create virtual environment

```bash
python -m venv .venv
```

Activate environment

Windows

```bash
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Install Ollama

Download:

https://ollama.com

Pull the required model

```bash
ollama pull phi3:mini
```

Start Ollama

```bash
ollama serve
```

Run the application

```bash
python run.py
```

Open

```
http://127.0.0.1:8000
```

---

## Usage

1. Upload a document.
2. Wait for processing.
3. View:
   - Summary
   - Classification
   - Entities
   - Structured Output
4. Download the generated JSON.

---

## Folder Structure

```
app/
frontend/
uploads/
tests/
data/
run.py
requirements.txt
```

---

## Supported Formats

- PDF
- TXT
- DOC
- PNG
- JPG
- BMP
- TIFF

---

## Offline Capability

All AI inference runs locally using:

- Ollama
- phi3:mini
- Hugging Face local models

No OpenAI or external AI APIs are used during inference.

---

## Future Improvements

- Audio transcription
- Video support
- Image captioning
- Vector database integration
- Faster quantized models

---

## Authors

Team LocalAI
>>>>>>> 4397f3c (Enhance Local AI dashboard and structured output UI)

---

## License

<<<<<<< HEAD
This project was developed as part of an internship/hackathon assignment for educational purposes.

---
=======
MIT License
>>>>>>> 4397f3c (Enhance Local AI dashboard and structured output UI)
