# AttorneysInRAGs

A legal compliance analysis tool that automatically checks Terms of Service and Privacy Policy documents against Indian IT laws and regulations using RAG (Retrieval-Augmented Generation).

## Overview

AttorneysInRAGs analyzes legal documents through a multi-stage pipeline:

1. **Filtering** - Extracts relevant legal clauses using ontology-based keyword matching + AI classification
2. **Matching** - Embeds clauses and queries a vector database of laws to find potential matches
3. **Analysis** - Uses an LLM to determine if matches constitute actual violations

## Architecture

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────────┐
│  Input ToS  │───▶│  Filter      │───▶│  Vector DB  │───▶│  LLM         │
│  Document   │    │  (filter.py)  │    │  (matcher)│   │  (inference)  │
└─────────────┘    └──────────────┘    └─────────────┘    └──────────────┘
                         │                    │                   │
                   Ontology + AI        ChromaDB +            Ollama +
                   Classification       BGE Embeddings        Mistral
```

## Installation

### Prerequisites
- Python 3.11 or 3.12.3 (<3.14)
- Ollama with `mistral:latest` model

### Setup

```bash
# Clone and enter directory
cd AttorneysInRAGs

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install chromadb sentence-transformers spacy transformers fastapi uvicorn httpx

# Download spaCy model
python -m spacy download en_core_web_sm

# Pull Ollama model
ollama pull mistral:latest
```

### Initialize Database

```bash
python experimentation/db_generator.py
```

This populates the ChromaDB vector database with embedded law rationales from `backend/database/db.json`.

## Usage

### CLI Testing

```bash
python backend/main.py
```

Reads `backend/text.txt` and runs the full pipeline.

### API Server

```bash
# From project root
uvicorn backend.api:app --host 0.0.0.0 --port 8000
```

#### Endpoint

**POST** `/analyze`

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Your Terms of Service text here..."}'
```

#### Response

```json
{
  "summary": "Executive summary of violations found.",
  "aggregations": {
    "total_violations": 2,
    "critical_severity": 1,
    "high_severity": 1,
    "medium_severity": 0,
    "low_severity": 0
  },
  "violations": [
    {
      "violating_rule": "ToS clause text...",
      "actual_rule": "The actual law text...",
      "source": "[IT_ACT_SEC_43A] DATA_SHARING, LIABILITY",
      "severity": "CRITICAL",
      "reason": "Why this is a violation"
    }
    ...
  ]
}
```

## Project Structure

```
AttorneysInRAGs/
├── backend/
│   ├── api.py              # FastAPI server
│   ├── main.py             # CLI pipeline runner
│   ├── filter.py         # RelevanceFilter (ontology + AI)
│   ├── matcher.py       # Vector search + matching
│   ├── inference.py         # LLM inference (Ollama)
│   ├── text.txt            # Sample input for testing
│   └── database/
│       ├── db.json         # Law rules database
│       └── chroma_db/      # Vector embeddings
├── experimentation/
│   ├── db_generator.py     # Populate ChromaDB
│   └── svo.py              # Text distillation experiments
└── README.md
```

## Configuration

### Embedding Model
Uses `BAAI/bge-small-en-v1.5` (384-dim) for fast, high-quality embeddings.

### LLM
Default: Ollama with `mistral:latest`. Configure in `backend/inference.py`:

```python
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral:latest"
```

### Similarity Threshold
Adjust in `backend/matcher.py`:

```python
threshold=0.40  # Lower = stricter matching
```

## Law Domains Covered

- `DATA_COLLECTION` - Data gathering practices
- `DATA_RETENTION` - Storage duration requirements
- `DATA_SHARING` - Third-party sharing rules
- `CONSENT` - User consent requirements
- `SECURITY_PRACTICES` - Security standards
- `BREACH_RESPONSE` - Incident notification rules
- `USER_RIGHTS` - Access, correction, deletion rights
- `GRIEVANCE` - Complaint handling procedures
- `LIABILITY` - Liability and indemnification
- `SENSITIVE_DATA` - Special category data rules
- `CHILDREN_DATA` - Minor protection rules
- `LOGGING_AUDIT` - Audit trail requirements

## Law documents used
IT Act, 2000 Sections 43 & 66

DPDP Act, 2023

IT Security Practices Rules

CERT-In Guidelines

IT Intermediary Guidelines

## License

MIT
