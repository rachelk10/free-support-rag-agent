from models import TriageRequest, RouterDecision, Category
from services.llm_service import LLMService


class RouterNode:
    """
    Router Node

    אחראי על שלב ה-triage הראשוני של המערכת.

    קלט:
        TriageRequest

    פלט:
        RouterDecision

    תפקיד:
    - סיווג הבקשה לקטגוריה
    - הערכת ודאות (confidence)
    - החלטה האם נדרש טיפול אנושי מיידי
    """

    def __init__(self, llm: LLMService):
        self.llm = llm

    # ------------------------------------------------------------
    # Prompt / Messages Builder
    # ------------------------------------------------------------

    def build_messages(self, request: TriageRequest):
        """
        בונה את ה-messages ל-LLM בצורה תקנית (system + user).
        """

        system_prompt = """
You are a customer support routing engine.

    Your primary job is to classify user messages into one of these main categories:

    Main categories:
    - inquiry: general question or information request
    - bug: something is not working or broken
    - complaint: user is unhappy, frustrated, or reporting bad experience

    Fallback categories (use only when clearly needed):
- spam: irrelevant, abusive, or nonsensical content
- urgent_human: requires immediate human intervention

Rules:
- Always return ONLY valid JSON.
- Do not include explanations outside JSON.
- Be precise and conservative in classification.
    - Prefer inquiry/bug/complaint whenever possible.
- If unsure, lower confidence_score.

JSON schema:
{
  "category": "inquiry | bug | complaint | spam | urgent_human",
  "confidence_score": 0.0 - 1.0,
  "reason": "short explanation",
  "requires_human": true | false
}
""".strip()

        return [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": request.message
            }
        ]

    # ------------------------------------------------------------
    # Main execution
    # ------------------------------------------------------------

    def run(self, request: TriageRequest) -> RouterDecision:
        """
        מריץ את ה-Router ומחזיר החלטת סיווג.
        """

        messages = self.build_messages(request)

        decision = self.llm.generate_structured(
            messages=messages,
            response_model=RouterDecision,
            temperature=0.0
        )

        # --------------------------------------------------------
        # Post-processing / Guardrails (מחוץ ל-LLM)
        # --------------------------------------------------------

        # אם זה urgent → תמיד human
        if decision.category == Category.urgent_human:
            decision.requires_human = True

        # spam / uncertain edge-cases יכולים לדרוש עין אנושית
        if decision.category == Category.spam:
            decision.requires_human = True

        # אם confidence נמוך מאוד → להפנות לאדם
        if decision.confidence_score < 0.4:
            decision.requires_human = True

        return decision