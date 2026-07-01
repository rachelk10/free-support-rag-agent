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
    You are a friendly, professional course support worker in an AI contact center.

    Conversation style:
    - Be warm, friendly, and human.
    - If the user only greets you, thanks you, says goodbye, or engages in small talk,
      respond naturally in one or two short sentences.
    - Do NOT introduce or summarize the course unless the user asks about it.
    - Never volunteer large amounts of information that were not requested.
    - Answer only the user's actual question.    
    - Use a supportive, respectful tone.
    - Be concise but helpful.

    Business objective:
    - Help users understand the value of the course and support purchase decisions.
    - When users express objections, doubts, hesitation, or concerns about the course,
      acknowledge the concern respectfully and respond with confidence.
    - Explain course value clearly (content quality, practical value, guidance/support,
      instructor expertise, outcomes), while staying honest and professional.
    - Never pressure, manipulate, or use aggressive sales tactics.

    Grounding policy:
    - If course material is provided, use it as reference only when needed to answer the user's actual question.
    - Do not summarize retrieved course material unless the user explicitly asks for it.
    - If a specific factual claim is not supported by the provided sources, say so clearly.
    - For greetings and casual conversation, ignore retrieved course material and reply naturally.

    Scope policy (use judgment, not keyword matching):
    - If the user asks something clearly unrelated to the course/business context,
      reply politely that you can help with course-related questions and purchase guidance,
      and redirect to relevant topics.
    - Do not escalate unrelated safe messages to a human.

    Possible outputs:
    1. reply - answer the user directly
    2. github_issue - create a structured bug report
    3. blocked - refuse unsafe/spam content
    4. human_handoff - escalate to human agent

    Escalation policy:
    - Prefer reply whenever possible.
    - Use human_handoff only when truly needed (high-risk/sensitive situations,
      explicit request for a human, or unresolved account-specific actions you cannot perform Or requesting information that you don't have.).
    - For complaint category, first try an empathetic, solution-oriented reply; escalate only if needed.

    Routing rules:
    - If router category is bug → prefer github_issue
    - If router category is inquiry or complaint → prefer reply
    - If router category is spam → blocked

    Return valid structured output only.
    """.strip()

        if retrieved_docs:
            sources = "\n\n".join(
                f"Source: {doc.source}\n{doc.content.strip()}"
                for doc in retrieved_docs
            )
            user_prompt = f"""
User message:
{state.request.message}

Router category:
{decision.category.value if decision else 'unknown'}

Retrieved course material (reference only):
{sources}

Respond in a warm, trustworthy tone.
Use the retrieved material ONLY if it is needed to answer the user's question.
Do NOT summarize the course unless the user explicitly requested course information.
If a requested factual detail is unavailable in the provided material, say so clearly.
""".strip()
        else:
            user_prompt = f"""
User message:
{state.request.message}

Router category:
{decision.category.value if decision else 'unknown'}

No relevant course material was retrieved.
Use judgment:
- If this is a normal greeting/conversation turn, reply naturally and briefly.
- If this is clearly unrelated to course support, politely decline and redirect to course topics.
- If this is a course-related concern/objection, address it respectfully, explain value confidently,
  and be transparent about what you can/cannot verify.
- Escalate to human only when truly necessary.
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

        if decision and decision.category == Category.greeting:
            retrieved_docs = []

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

        if decision and decision.category == Category.complaint:
            if result.output_type not in (OutputType.reply, OutputType.human_handoff):
                result.output_type = OutputType.reply

            if result.output_type == OutputType.reply and not result.reply_text:
                result.reply_text = (
                    "Thank you for sharing your concern. "
                    "I want to help and clarify what the course includes so you can decide confidently."
                )

        if result.output_type == OutputType.reply and not result.reply_text:
            result.reply_text = (
                "I’m here to help with course-related questions. "
                "Please share what you want to know about the course, and I’ll do my best to assist."
            )

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

        if category == Category.complaint and result.output_type not in (
            OutputType.reply,
            OutputType.human_handoff,
        ):
            result.output_type = OutputType.reply

        if category == Category.greeting:
            result.output_type = OutputType.reply

        if not result.reply_text:
            result.reply_text = (
            "Hello! I'm happy to help. What would you like to know about the course?"
        )

        if category == Category.spam:
            result.output_type = OutputType.blocked

        if category == Category.urgent_human:
            result.output_type = OutputType.human_handoff

        return result