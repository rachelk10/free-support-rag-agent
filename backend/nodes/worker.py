from models import (
    AgentState,
    WorkerOutput,
    OutputType,
    IssueDraft,
    Category,
    RetrievedDocument,
)

from services.llm_service import LLMService
from services.rag_service import RAGService


class WorkerNode:
    """
    Worker Node

    תפקיד:
    - ביצוע פעולה בהתאם לקטגוריה מה-Router
    - יצירת תשובה / issue / או העברה להמשך טיפול
    """

    def __init__(self, llm: LLMService):
        self.llm = llm
        self.rag = RAGService()

    # ------------------------------------------------------------
    # Prompt builder
    # ------------------------------------------------------------

    def build_messages(
        self,
        state: AgentState,
        retrieved_docs: list[RetrievedDocument] | None = None,
    ): 
        """
        בונה את ההוראות ל-LLM לפי החלטת ה-Router.
        """

        decision = state.router_decision

        system_prompt = """
You are a support worker inside an AI contact center system.

When course material is available, answer the user using only those documents.
If no relevant course material exists, say so clearly and do not invent facts.

Possible outputs:
1. reply - answer the user directly
2. github_issue - create a structured bug report
3. blocked - refuse unsafe/spam content
4. human_handoff - escalate to human agent

Rules:
- Always return valid structured output only
- Be concise
- If router category is bug → github_issue
- If router category is inquiry → reply
- If router category is complaint → human_handoff
- If unclear → human_handoff
""".strip()

        if retrieved_docs:
            sources = "\n\n".join(
                f"Source: {doc.source}\n{doc.content.strip()}"
                for doc in retrieved_docs
            )
            user_prompt = f"""
User message:
{state.request.message}

Retrieved course material:
{sources}

Answer using only the provided sources. Cite each claim with the source name in brackets.
If the answer cannot be found in the course material, say that the answer is not available.
""".strip()
        else:
            user_prompt = f"""
User message:
{state.request.message}

No relevant course material was retrieved. If you cannot answer from the course material,
state that the information is unavailable.
""".strip()

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    # ------------------------------------------------------------
    # Main execution
    # ------------------------------------------------------------

    def run(self, state: AgentState) -> WorkerOutput:
        """
        מריץ את ה-Worker ומחזיר החלטה + תוצר.
        """

        decision = state.router_decision
        retrieved_docs: list[RetrievedDocument] = []

        if decision and decision.category == Category.inquiry:
            retrieved_docs = self.rag.query(state.request.message, top_k=4)

        messages = self.build_messages(state, retrieved_docs)

        result = self.llm.generate_structured(
            messages=messages,
            response_model=WorkerOutput,
            temperature=0.2
        )

        # --------------------------------------------------------
        # Post-processing guardrails
        # --------------------------------------------------------

        # אם יש issue אבל אין title → fallback ל-human
        if result.output_type == OutputType.github_issue:
            if not result.issue or not result.issue.title:
                result.output_type = OutputType.human_handoff

        # אם reply ריק → escalate
        if decision and decision.category == Category.inquiry:
            result.output_type = OutputType.reply
            if not result.reply_text:
                result.reply_text = (
                    "I could not find a matching answer in the course material."
                )

        if result.output_type == OutputType.reply and not result.reply_text:
            result.output_type = OutputType.human_handoff

        # --------------------------------------------------------
        # Category-aligned enforcement
        # --------------------------------------------------------
        category = state.router_decision.category if state.router_decision else None

        if category == Category.bug and result.output_type != OutputType.github_issue:
            result.output_type = OutputType.github_issue

        if category == Category.inquiry and result.output_type not in (
            OutputType.reply,
            OutputType.human_handoff,
        ):
            result.output_type = OutputType.reply

        if category == Category.complaint and result.output_type != OutputType.human_handoff:
            result.output_type = OutputType.human_handoff

        if category == Category.spam:
            result.output_type = OutputType.blocked

        if category == Category.urgent_human:
            result.output_type = OutputType.human_handoff

        return result