# CRISIS Economics Simulator - RAG Component

![ChromaDB](https://img.shields.io/badge/chromadb-0.4+-blue.svg)

**Retrieval-Augmented Generation for financial knowledge queries**

---

## Overview

This component implements a RAG (Retrieval-Augmented Generation) system for retrieving relevant financial knowledge from the FE-EKG knowledge graph. It enables context-aware responses by combining vector similarity search with structured knowledge graph queries.

---

## What It Does

### Knowledge Retrieval
- **Vector storage** of financial events and relationships using ChromaDB
- **Semantic search** using sentence transformers
- **Context augmentation** for LLM/SLM queries

### Integration Points
- **ABM agents** query RAG for historical context before decisions
- **SLM** receives retrieved context for enhanced reasoning
- **Knowledge Graph** provides structured data for ingestion

---

## Files

```
rag/
├── README.md              # This file
├── RAG_WORKFLOW.md        # Detailed workflow documentation
├── EVALUATION_PLAN.md     # Evaluation methodology
├── ingest.py              # Document ingestion to vector store
├── ingest_incremental.py  # Incremental updates
├── retriever.py           # Query and retrieval logic
├── check_db.py            # Database health checks
├── test_retrieval.py      # Test scripts
├── requirements.txt       # RAG-specific dependencies
└── data/                  # Vector store data (gitignored)
```

---

## Quick Start

### Install Dependencies

```bash
pip install chromadb sentence-transformers
# Or use the requirements file
pip install -r rag/requirements.txt
```

### Ingest Data

```bash
# Initial ingestion from knowledge graph
./venv/bin/python rag/ingest.py

# Incremental updates
./venv/bin/python rag/ingest_incremental.py
```

### Query the RAG System

```python
from rag.retriever import RAGRetriever

# Initialize retriever
retriever = RAGRetriever()

# Query for relevant context
query = "What happened during the Lehman Brothers bankruptcy?"
results = retriever.query(query, top_k=5)

for doc in results:
    print(f"Score: {doc['score']:.3f}")
    print(f"Content: {doc['content']}")
    print("---")
```

### Test Retrieval

```bash
./venv/bin/python rag/test_retrieval.py
```

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│  Knowledge      │     │  User Query     │
│  Graph (FEEKG)  │     │  or ABM Agent   │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  Ingestion      │     │  Retriever      │
│  Pipeline       │     │  (Semantic)     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────────────────────────────┐
│           ChromaDB Vector Store         │
│  (Sentence Transformer Embeddings)      │
└─────────────────────────────────────────┘
```

---

## Configuration

### Environment Variables

```bash
# ChromaDB settings (optional, uses defaults)
CHROMA_PERSIST_DIR=./rag/data/chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Embedding Model

Default: `all-MiniLM-L6-v2` (fast, good quality)

Alternatives:
- `all-mpnet-base-v2` (higher quality, slower)
- `paraphrase-MiniLM-L6-v2` (optimized for similarity)

---

## Integration with ABM

```python
from abm import BankAgent
from rag.retriever import RAGRetriever

class EnhancedBankAgent(BankAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rag = RAGRetriever()

    def make_decision(self):
        # Get historical context
        context = self.rag.query(
            f"Bank failures with capital ratio {self.capital_ratio}",
            top_k=3
        )

        # Use context for decision
        # ... decision logic with historical examples
```

---

## Evaluation

See `EVALUATION_PLAN.md` for:
- Retrieval accuracy metrics
- Response relevance scoring
- Performance benchmarks

---

## Documentation

- **[RAG_WORKFLOW.md](RAG_WORKFLOW.md)** - Detailed system workflow
- **[EVALUATION_PLAN.md](EVALUATION_PLAN.md)** - Evaluation methodology

---

## Dependencies

```
chromadb>=0.4.0
sentence-transformers>=2.2.0
```

---

## Status

**Current:** Foundation Complete ✅
- Vector store setup
- Basic ingestion pipeline
- Query interface

**Next:** Integration with ABM agents
- Connect to agent decision loops
- Optimize retrieval for simulation speed
- Add more financial event context
