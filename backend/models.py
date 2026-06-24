from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field


# ============================================================
# Enums
# ============================================================

class Category(str, Enum):
    """
    סוג הפנייה שזוהה ע"י ה-Router.
    """

    inquiry = "inquiry"          # בקשת מידע
    bug = "bug"                  # דיווח על תקלה
    complaint = "complaint"      # תלונה
    spam = "spam"                # ספאם
    urgent_human = "urgent_human"  # דורש טיפול אנושי מיידי


class OutputType(str, Enum):
    """
    סוג הפלט שנוצר ע"י ה-Worker.
    """

    reply = "reply"
    github_issue = "github_issue"
    blocked = "blocked"
    human_handoff = "human_handoff"


class Severity(str, Enum):
    """
    רמת חומרה של תקלה.
    """

    low = "low"
    medium = "medium"
    high = "high"


# ============================================================
# Input Models
# ============================================================

class TriageRequest(BaseModel):
    """
    הפנייה המקורית שהתקבלה מהמשתמש.
    """

    message: str = Field(
        ...,
        min_length=1,
        description="User contact request"
    )


# ============================================================
# Router Models
# ============================================================

class RouterDecision(BaseModel):
    """
    תוצאת הסיווג של ה-Router.
    """

    category: Category

    confidence_score: float = Field(
        ...,
        ge=0,
        le=1,
        description="Confidence score between 0 and 1"
    )

    reason: str

    requires_human: bool = False

# ============================================================
# Issue Models
# ============================================================

class IssueDraft(BaseModel):
    """
    טיוטת Issue שנוצרת עבור דיווח על באג.
    """

    title: str

    body: str

    labels: list[str] = Field(default_factory=list)

    severity: Severity = Severity.medium

    missing_details: list[str] = Field(default_factory=list)


# ============================================================
# RAG Models
# ============================================================

class RetrievedDocument(BaseModel):
    """
    מסמך שנשלף ממערכת ה-RAG.
    ישמש בעתיד להערכת איכות ה-RAG.
    """

    source: str

    content: str

    score: float


# ============================================================
# Worker Models
# ============================================================

class WorkerOutput(BaseModel):
    """
    הפלט שנוצר ע"י ה-Worker.
    """

    output_type: OutputType

    reply_text: str | None = None

    issue: IssueDraft | None = None

    notes: str | None = None

    retrieved_docs: list[RetrievedDocument] = Field(default_factory=list)

# ============================================================
# Evaluator Models
# ============================================================

class EvaluatorResult(BaseModel):
    """
    תוצאת הערכת האיכות של ה-Evaluator.
    """

    passed: bool

    feedback: str

    needs_human: bool = False


# ============================================================
# Human Approval Models
# ============================================================

class ApprovalRequest(BaseModel):
    """
    החלטת הגורם האנושי בשלב HITL.
    """

    approved: bool

    edited_output: WorkerOutput | None = None

    comment: str | None = None


# ============================================================
# Global Workflow State
# ============================================================

class AgentState(BaseModel):
    """
    האובייקט המרכזי שעובר בין כל ה-Nodes.

    Router
        ↓
    Worker
        ↓
    Evaluator
        ↓
    HITL
        ↓
    End
    """

    request: TriageRequest

    router_decision: RouterDecision | None = None

    worker_output: WorkerOutput | None = None

    evaluator_result: EvaluatorResult | None = None

    approval_request: ApprovalRequest | None = None

    retry_count: int = 0

    final_output: str | None = None