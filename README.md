# Agent Evaluation Platform

### Professional Overview

This repository demonstrates a production-ready contact agent architecture built for advanced AI-driven customer support workflows.

It combines:  
- **FastAPI** for REST API exposure  
- **OpenAI** for structured LLM decision making and embeddings  
- **Retrieval-Augmented Generation (RAG)** for grounded answers from source material  
- **Human-in-the-loop (HITL)** escalation for high-risk or low-confidence cases  

The codebase is designed to support high-quality triage, automated issue creation, safe escalation, and continuous evaluation.

---

## Key Capabilities

- **Intelligent request routing**: classifies incoming contact messages into `inquiry`, `bug`, `complaint`, `spam`, or `urgent_human`.
- **RAG-based knowledge grounding**: semantic search over course material with chunking, embeddings, and relevance ranking.
- **Structured LLM output**: uses Pydantic-driven structured responses for deterministic downstream processing.
- **Automated quality evaluation**: evaluates generated responses and retries until quality thresholds are met.
- **Human review workflow**: supports explicit human approval, rejection, and editing for unresolved or sensitive cases.
- **Modular agent graph**: clean node-based pipeline for Router → Worker → Evaluator → HITL → End.

---

## Architecture

The project is organized around a modular agent workflow:

1. **RouterNode**  
   - Uses LLM classification to determine request category and whether human review is required.
2. **WorkerNode**  
   - Executes the appropriate action based on routing, including RAG retrieval for inquiries and bug report generation for bug tickets.
3. **EvaluatorNode**  
   - Runs a second LLM pass to verify output quality and decide if retry or escalation is needed.
4. **HITLNode**  
   - Provides a human-in-the-loop review interface for manual approval and editing.
5. **EndNode**  
   - Finalizes the response output after the pipeline completes.

This separation enables robust control, better traceability, and clear extension points for future capabilities.

---

## Technology Stack

- `Python`  
- `FastAPI`  
- `OpenAI` Python client  
- `Pydantic` for strong typed models  
- `python-dotenv` for config management  

---

## Project Structure

- `backend/app.py` — REST API entrypoint for contact routing, HITL approval, and RAG operations
- `backend/run.py` — CLI entrypoint for local workflow execution
- `backend/config.py` — runtime settings and environment configuration
- `backend/models.py` — domain definitions for router decisions, worker outputs, evaluator results, and approval state
- `backend/services/llm_service.py` — OpenAI integration, structured responses, text embeddings
- `backend/services/rag_service.py` — semantic chunking, embedding generation, vector search, and retrieval
- `backend/nodes/` — node implementations for routing, work execution, evaluation, human handoff, and finalization
- `backend/graph/workflow.py` — orchestrates the full contact agent pipeline

---

## Installation

1. Create and activate a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r backend/requirements.txt
```

3. Set environment variables in `.env`:

```text
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDINGS_MODEL=text-embedding-3-large
```

---

## Running the Platform

### API server

```powershell
cd backend
uvicorn app:app --reload
```

### Frontend app

```powershell
cd frontend/chat-halo-glow
npm install
npm run dev -- --host 0.0.0.0
```

The frontend chat widget connects to the backend at `http://localhost:8000/contact` by default.

### CLI workflow

```powershell
cd backend
python run.py "Your incoming customer message here"
```

---

## Docker Support

### Build the image

```powershell
docker build -t agent-evaluation .
```

### Run the container

```powershell
docker run --rm -p 8000:8000 --env-file backend/.env agent-evaluation
```

### Or use Docker Compose

```powershell
docker compose up --build
```

> Ensure your `backend/.env` file exists with `OPENAI_API_KEY` and any other required variables.

---

## Example Endpoints

- `GET /health` — health check
- `POST /contact` — submit a message for triage and response generation
- `POST /contact/{request_id}/approve` — approve or reject a human-reviewed request
- `POST /rag/index` — build or refresh semantic index
- `POST /rag/query` — retrieve top-k relevant documents from course material

---

## Why This Project Stands Out

- **Advanced AI orchestration**: the system uses multiple LLM phases to route, generate, and verify output.
- **Grounded responses**: RAG retrieval ensures answers are based on real course content rather than hallucination.
- **Safety-first design**: human fallback is embedded into the workflow for uncertain or sensitive cases.
- **Engineering maturity**: typed models, structured outputs, and clear separation of concerns make the codebase production-ready.

---

## Hiring-Focused Takeaways

If you are evaluating this project for recruitment, note that it demonstrates:

- Practical experience with modern AI and LLM integration
- Capability to build modular, maintainable agent systems
- Understanding of retrieval-augmented generation and semantic search
- Ability to design safe workflows with human oversight
- Strong API-first thinking and clean architecture

---

## Future Enhancements

Potential next steps include:

- adding a web UI or dashboard for HITL review  
- extending RAG storage to a real vector database  
- supporting multiple LLM providers with fallbacks  
- adding logging / telemetry for production observability

---

## License

This repository is provided for technical evaluation and demonstration purposes.
