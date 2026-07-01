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

Your job is to classify user messages into exactly one category.

Main categories:
- greeting: greetings, thanks, farewells, or casual small talk that does not request course information.
- inquiry: questions or requests for information about the course or purchasing process.
- bug: something is not working or the user reports a technical problem.
- complaint: the user is dissatisfied, frustrated, or reporting a negative experience.

Fallback categories (use only when clearly appropriate):
- spam: irrelevant, abusive, promotional, or nonsensical content.
- urgent_human: situations that require immediate human intervention.

Greeting classification:
- If the message only contains a greeting, thanks, farewell, or other small talk,
  classify it as "greeting".
- Do NOT classify greetings as "inquiry" unless the user also asks a question about the course.

Examples:

greeting
- "Hi"
- "Hello"
- "Good morning"
- "Thanks"
- "Thank you"
- "Bye"
- "How are you?"

inquiry
- "How much does the course cost?"
- "What topics are covered?"
- "Do I need Python experience?"

bug
- "The payment page doesn't work."
- "I can't log in."
- "The video won't play."

complaint
- "I'm disappointed."
- "The videos are low quality."
- "The support takes too long."

Rules:
- Always return ONLY valid JSON.
- Do not include explanations outside JSON.
- Be precise and conservative in classification.
- Prefer greeting, inquiry, bug, or complaint whenever appropriate.
- Use spam and urgent_human only when clearly justified.
- If unsure, lower confidence_score.

JSON schema:
{
  "category": "greeting | inquiry | bug | complaint | spam | urgent_human",
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

        # spam תמיד דורש בדיקה אנושית
        if decision.category == Category.spam:
            decision.requires_human = True

        # אם confidence נמוך מאוד → להפנות לאדם
        if decision.confidence_score < 0.4:
            decision.requires_human = True

        return decision