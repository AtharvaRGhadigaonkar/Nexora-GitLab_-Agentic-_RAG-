# 🦊 Nexora — Agentic RAG Knowledge Assistant

### Your intelligent workspace companion for GitLab documentation, engineering workflows, and enterprise IT support.

Nexora is an AI-powered Agentic Retrieval-Augmented Generation (RAG) assistant designed to help organizations interact with internal knowledge through natural language.

It prioritizes private company documentation, retrieves relevant information using semantic search, evaluates the quality of retrieved evidence, and generates context-aware responses. When internal information is insufficient, Nexora can use external web search to supplement its knowledge.

---

## ✨ Features

- **Private Knowledge First:** Prioritizes internal company documents over external information.
- **Agentic Workflow:** Uses LangGraph to orchestrate query classification, retrieval, evidence evaluation, and response generation.
- **Semantic Document Retrieval:** Uses HuggingFace embeddings and Pinecone for similarity-based search.
- **Intelligent Web Fallback:** Uses Tavily when internal knowledge does not provide sufficient evidence.
- **Query Refinement:** Rewrites and retries queries to improve retrieval relevance.
- **Multi-format Document Ingestion:** Supports PDF, TXT, Markdown, and DOCX documents.
- **OCR Support:** Extracts text from scanned PDF documents.
- **Source Attribution:** Displays the sources used to generate responses.
- **Agent Activity Tracking:** Provides visibility into workflow execution through the frontend.
- **Audit Logging:** Maintains local records of application activity.

---

## 🧠 System Architecture

Nexora follows an agentic retrieval pipeline designed to prioritize organizational knowledge.

### 1. Query Processing

```text
       USER QUERY
            |
            v
    QUERY CLASSIFICATION
            |
            v
   PRIVATE KNOWLEDGE SEARCH
            |
            v
    EVIDENCE EVALUATION
            |
       +----+----+
       |         |
   SUFFICIENT  INSUFFICIENT
       |         |
       |         v
       |     TAVILY SEARCH
       |         |
       |         v
       |    QUERY REFINEMENT
       |         |
       |         v
       |    RETRIEVAL RETRY
       |         |
       +----+----+
            |
            v
     GROUNDED RESPONSE
            |
            v
        USER OUTPUT
```

### 2. Document Ingestion

```text
     COMPANY DOCUMENTS
              |
              v
       DOCUMENT LOADING
              |
              v
        TEXT EXTRACTION
              |
              v
         OCR (IF NEEDED)
              |
              v
        TEXT CHUNKING
              |
              v
    HUGGINGFACE EMBEDDINGS
              |
              v
         PINECONE
              |
              v
      SEMANTIC RETRIEVAL
```

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | FastAPI |
| Agent Orchestration | LangGraph |
| LLM Inference | Groq |
| Vector Database | Pinecone |
| Embedding Model | all-MiniLM-L6-v2 |
| External Search | Tavily |
| Document Processing | PyMuPDF, PyPDF, python-docx |
| OCR | Tesseract OCR, PyMuPDF |
| Frontend | HTML, CSS, JavaScript |
| Local Database | SQLite |

### Embedding Configuration

Nexora uses `sentence-transformers/all-MiniLM-L6-v2` to generate 384-dimensional embeddings.

These embeddings are stored in Pinecone using cosine similarity for semantic document retrieval.

---

## 📂 Project Structure

```text
Nexora/
│
├── .vscode/
│   └── settings.json
│
├── app/
│   ├── api/
│   │   ├── routes.py
│   │   └── __init__.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── __init__.py
│   │
│   ├── rag/
│   │   ├── state.py
│   │   ├── vectorstore.py
│   │   ├── workflow.py
│   │   └── _init_.py
│   │
│   ├── services/
│   │   ├── audit.py
│   │   ├── ingestion.py
│   │   └── __init__.py
│   │
│   └── main.py
│
├── data/
│   ├── audit.db
│   │
│   └── sample_kb/
│       ├── GitLab_Company Structure.pdf
│       ├── GitLab_Employee_Onboarding_Guide.pdf
│       ├── GitLab_HR_Policies.pdf
│       ├── GitLab_Information_Security_Policy.pdf
│       ├── GitLab_Performance_and_Appraisal_Policy.pdf
│       ├── GitLab_Product_Documentation.pdf
│       └── GitLab_Troubleshoot_Guidelines.pdf
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── app.js
│
├── templates/
│   └── index.html
│
├── uploads/
│   └── GitLab_Employee Handbook.pdf
│
├── .env
├── .gitignore
├── ingest_sample_kb.py
├── main.py
├── requirements.txt
└── run.py
```

### Directory Overview

| Directory / File | Purpose |
|---|---|
| `app/api/` | FastAPI routes and API endpoints |
| `app/core/` | Application configuration and logging |
| `app/rag/` | LangGraph workflow, state management, and vector retrieval |
| `app/services/` | Document ingestion and audit services |
| `data/sample_kb/` | Internal GitLab knowledge base documents |
| `data/audit.db` | Local SQLite audit database |
| `static/` | Frontend CSS and JavaScript |
| `templates/` | HTML application interface |
| `uploads/` | Uploaded company documents |
| `ingest_sample_kb.py` | Initial knowledge base ingestion |
| `requirements.txt` | Python dependencies |
| `run.py` | Application startup script |

---

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.11 or later
- Pinecone account and API key
- Groq API key
- Tavily API key
- Tesseract OCR (for scanned PDF extraction)

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd Nexora
```

### 2. Create a Virtual Environment

Using Conda:

```bash
conda create -n AgenticRag python=3.11
conda activate AgenticRag
```

Alternatively, using Python:

```bash
python -m venv venv
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root.

```env
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Add any additional configuration variables required by `app/core/config.py`.

**Important:** Never commit your `.env` file or expose API credentials.

### 5. Configure the Knowledge Base

Place company documents inside:

```text
data/sample_kb/
```

Supported document formats:

- PDF
- TXT
- Markdown
- DOCX

### 6. Ingest Documents

Run the ingestion script:

```bash
python ingest_sample_kb.py
```

The ingestion pipeline:

1. Loads the documents.
2. Extracts text, including OCR for scanned PDFs.
3. Splits documents into smaller chunks.
4. Generates embeddings.
5. Stores the vectors in Pinecone.

### 7. Run Nexora

Start the FastAPI application using the configured entry point:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```

Open the application:

```text
http://127.0.0.1:8080
```

If your `run.py` provides a custom startup routine, you can also use that entry point as configured in the project.

---

## 💬 Example Queries

Nexora can answer questions related to internal company documentation and engineering workflows.

| Category | Example Query |
|---|---|
| GitLab | How do I configure a GitLab CI/CD pipeline? |
| Repository | What is our repository access policy? |
| Engineering | How do I troubleshoot GitLab Runner? |
| HR | What is the employee onboarding process? |
| Security | What are the company's information security policies? |
| IT Support | How do I connect to the company VPN? |
| External Knowledge | What is the latest guidance for a software issue? |

---

## 🔐 Design Philosophy

### Private Knowledge First

Nexora is designed around the principle of prioritizing internal organizational knowledge.

Rather than immediately relying on general-purpose LLM knowledge, it retrieves relevant company documentation and evaluates the available evidence before generating an answer.

External search acts as a supplementary information source when internal documentation is insufficient.

This approach aims to improve contextual relevance, reduce unsupported responses, and make organizational information easier to access.

---

## 🚀 Future Scope

- **GitLab API Integration:** Direct access to project documentation, repositories, and GitLab resources.
- **Conversation Memory:** Context-aware follow-up questions across conversations.
- **Role-Based Access Control:** Different knowledge access levels for organizational teams.
- **Incremental Indexing:** Update the vector database when documents change.
- **Advanced Retrieval Evaluation:** Improve document relevance and retrieval quality.
- **Enhanced Observability:** Detailed agent execution monitoring and performance analytics.

---

## 👨‍💻 Project Information

**Project:** Nexora — Agentic RAG Knowledge Assistant

**Domain:** Agentic AI · Retrieval-Augmented Generation · Enterprise Knowledge Management

**Core Technologies:** Python · FastAPI · LangGraph · Groq · Pinecone · HuggingFace · Tavily

---

*Making organizational knowledge easier to discover, understand, and use.*