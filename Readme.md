# AI Codebase Assistant

An AI-powered codebase assistant that lets developers connect a GitHub repository and ask natural-language questions about its source code.

The system uses **Hybrid RAG, Qdrant, Sentence Transformers, CrossEncoder reranking, LangGraph, MCP, and Google Gemini** to retrieve relevant code and generate grounded answers with source citations.

---

## Features

- Connect and index GitHub repositories
- Structure-aware code chunking
- Dense + sparse hybrid retrieval
- Qdrant vector database
- Reciprocal Rank Fusion (RRF)
- Code-aware identifier/file ranking
- CrossEncoder reranking
- LangGraph RAG orchestration
- MCP-based repository inspection tools
- Conversational chat history
- Gemini-powered answers
- File and line-level source citations

---

## Architecture

```text
GitHub Repository
       ↓
Clone & Source File Discovery
       ↓
Code Chunking + Metadata
       ↓
Dense + Sparse Embeddings
       ↓
Qdrant Hybrid Search
       ↓
RRF Fusion
       ↓
Top 20 Candidates
       ↓
Code-aware Ranking
       ↓
CrossEncoder Reranking
       ↓
Top 5 Chunks
       ↓
LangGraph Generation
       ↓
Google Gemini
       ↓
Answer + Sources
````

### MCP Integration

MCP provides read-only tools for direct repository inspection:

```text
search_code()
get_file()
list_files()
```

MCP complements the RAG pipeline when direct codebase inspection is useful.

---

## Retrieval Pipeline

The assistant uses both semantic and lexical retrieval.

### Dense Retrieval

Sentence Transformer embeddings capture semantic relationships between the user's question and code chunks.

### Sparse Retrieval

Sparse retrieval helps find exact:

* Function names
* Class names
* Filenames
* API routes
* Code identifiers

### Hybrid Search

Dense and sparse results are combined using **Reciprocal Rank Fusion (RRF)**.

The resulting top 20 candidates are then passed through a lightweight code-aware ranking stage and a **CrossEncoder** reranker to select the final top 5 chunks.

---

## LangGraph Workflow

The RAG workflow is implemented as a LangGraph pipeline:

```text
START
  ↓
Retrieve
  ↓
Code-aware Ranking
  ↓
CrossEncoder Rerank
  ↓
Generate
  ↓
END
```

This keeps retrieval, ranking, and generation modular and makes the pipeline easier to extend.

---

## Repository Indexing

Each code chunk is stored with metadata such as:

```text
repo_id
file
language
start_line
end_line
chunk_type
symbol
content
```

This metadata is used to provide source-level citations in generated answers.

---

## Example Questions

```text
How does hybrid search work?

How are code chunks created?

How does reranking work?

How is the Gemini response generated?

How does the chat API work?

Where is conversation history handled?

Which file contains the index_repository function?
```

---

## Tech Stack

**Backend**

* Python
* FastAPI
* Uvicorn

**AI / GenAI**

* Google Gemini
* LangGraph
* LangChain
* MCP
* Sentence Transformers
* CrossEncoder

**Retrieval**

* Qdrant
* Dense Vector Search
* Sparse Retrieval
* RRF
* CrossEncoder Reranking

**Frontend**

* React
* JavaScript
* Axios

**Infrastructure**

* Docker
* Git / GitHub

---

## Project Structure

```text
AI-Codebase-Intelligent-Assistant/
│
├── backend/
│   ├── api/
│   │   ├── chat.py
│   │   └── repository.py
│   │
│   ├── services/
│   │   ├── chunk_service.py
│   │   ├── embedding_service.py
│   │   ├── graph_service.py
│   │   ├── index_service.py
│   │   ├── llm_service.py
│   │   ├── mcp_server.py
│   │   ├── reranker_service.py
│   │   ├── rag_service.py
│   │   ├── sparse_embedding_service.py
│   │   └── vector_service.py
│   │
│   ├── evaluation/
│   │   └── evaluate_rag.py
│   │
│   └── main.py
│
├── frontend/
│   └── src/
│       └── App.jsx
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## Setup

### Prerequisites

* Python 3.10+
* Node.js
* Docker
* Git
* Google Gemini API key

### Backend

```bash
cd backend

python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Create `backend/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key
```

### Start Qdrant

```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Start Backend

```bash
cd backend
uvicorn main:app --reload
```

### Start Frontend

```bash
cd frontend
npm install
npm start
```

---

## Evaluation

The project includes an evaluation script covering representative codebase questions.

Latest evaluation:

```text
Queries:          7
Source Hit Rate:  85.71% (6/7)
Average Sources:  5.00
Average Latency:  17.81s
```

The evaluation measures whether the expected source file appears in the retrieved results.

---

## Key Engineering Highlights

* Hybrid dense + sparse retrieval for semantic and exact code search
* RRF-based result fusion
* Two-stage retrieval with CrossEncoder reranking
* Code-aware ranking for identifiers and filenames
* LangGraph-based RAG orchestration
* MCP tools for repository inspection
* Conversational context handling
* Source-grounded Gemini responses
* FastAPI + React application architecture

---

## Future Improvements

* Incremental repository indexing
* Private GitHub repository support
* Streaming responses
* AST-based code parsing
* Dependency graph retrieval
* Retrieval caching
* Production deployment
* Larger automated evaluation datasets

---

