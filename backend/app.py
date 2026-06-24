import uuid
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models import AgentState, TriageRequest, ApprovalRequest, WorkerOutput, OutputType, RetrievedDocument
from nodes.router import RouterNode
from nodes.worker import WorkerNode
from nodes.evaluator import EvaluatorNode
from nodes.end_node import EndNode
from services.llm_service import LLMService
from services.rag_service import RAGService
from utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="Contact Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_RETRIES = 3

# In-memory store for requests awaiting human approval
pending_states: dict[str, AgentState] = {}


# ---------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------

class ContactRequest(BaseModel):
    message: str


class ContactResponse(BaseModel):
    request_id: str
    status: str                         # "done" | "pending_human"
    final_output: Optional[str] = None
    category: Optional[str] = None
    output_type: Optional[str] = None
    retry_count: int = 0
    needs_human: bool = False


class ApprovalPayload(BaseModel):
    approved: bool
    edited_reply: Optional[str] = None
    comment: Optional[str] = None


# ---------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------

def _nodes() -> tuple[RouterNode, WorkerNode, EvaluatorNode, EndNode]:
    llm = LLMService()
    return RouterNode(llm), WorkerNode(llm), EvaluatorNode(llm), EndNode()

rag_service = RAGService()


class RAGIndexResponse(BaseModel):
    indexed_chunks: int


class RAGQueryRequest(BaseModel):
    question: str
    top_k: int = 5


def _run_until_hitl(message: str) -> tuple[AgentState, bool]:
    """Runs Router → Worker/Evaluator loop. Returns (state, needs_human)."""
    router, worker, evaluator, _ = _nodes()

    state = AgentState(request=TriageRequest(message=message))

    state.router_decision = router.run(state.request)
    logger.info(
        f"Router → {state.router_decision.category} "
        f"(conf={state.router_decision.confidence_score:.2f})"
    )

    while True:
        state.worker_output = worker.run(state)
        state.evaluator_result = evaluator.run(state)
        logger.info(
            f"Evaluator → passed={state.evaluator_result.passed} "
            f"needs_human={state.evaluator_result.needs_human} "
            f"retry={state.retry_count}"
        )

        if state.evaluator_result.passed:
            break
        if state.retry_count >= MAX_RETRIES:
            break
        state.retry_count += 1

    needs_human = bool(
        state.evaluator_result and state.evaluator_result.needs_human
    )
    return state, needs_human


# ---------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/rag/index", response_model=RAGIndexResponse)
def build_rag_index():
    chunks = rag_service.build_index(force=True)
    return RAGIndexResponse(indexed_chunks=len(chunks))


@app.post("/rag/query", response_model=list[RetrievedDocument])
def query_rag(payload: RAGQueryRequest):
    return rag_service.query(payload.question, top_k=payload.top_k)


@app.post("/contact", response_model=ContactResponse)
def contact(payload: ContactRequest):
    request_id = str(uuid.uuid4())
    logger.info(f"[{request_id}] incoming: {payload.message[:80]}")

    state, needs_human = _run_until_hitl(payload.message)

    response = ContactResponse(
        request_id=request_id,
        category=state.router_decision.category if state.router_decision else None,
        output_type=state.worker_output.output_type if state.worker_output else None,
        retry_count=state.retry_count,
        needs_human=needs_human,
        status="pending_human" if needs_human else "done",
    )

    if needs_human:
        pending_states[request_id] = state
        logger.info(f"[{request_id}] waiting for human approval")
        return response

    _, _, _, end = _nodes()
    state.final_output = end.run(state)
    response.final_output = state.final_output
    logger.info(f"[{request_id}] done → {state.final_output[:80]}")
    return response


@app.post("/contact/{request_id}/approve", response_model=ContactResponse)
def approve(request_id: str, payload: ApprovalPayload):
    state = pending_states.pop(request_id, None)
    if not state:
        raise HTTPException(
            status_code=404,
            detail="Request not found or already resolved"
        )

    edited_output = None
    if payload.edited_reply and state.worker_output:
        edited_output = WorkerOutput(
            output_type=OutputType.reply,
            reply_text=payload.edited_reply,
        )

    state.approval_request = ApprovalRequest(
        approved=payload.approved,
        edited_output=edited_output,
        comment=payload.comment,
    )

    if not payload.approved:
        state.final_output = "Request rejected by human agent." + (
            f" Reason: {payload.comment}" if payload.comment else ""
        )
    else:
        _, _, _, end = _nodes()
        state.final_output = end.run(state)

    action = "approved" if payload.approved else "rejected"
    logger.info(f"[{request_id}] human {action}")

    return ContactResponse(
        request_id=request_id,
        status="done",
        final_output=state.final_output,
        category=state.router_decision.category if state.router_decision else None,
        output_type=state.worker_output.output_type if state.worker_output else None,
        retry_count=state.retry_count,
        needs_human=False,
    )
