"""Simple policy guardrails for the contact-agent workflow."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class GuardrailAction(str, Enum):
    """Possible guardrail outcomes."""

    allow = "allow"
    block = "block"


class GuardrailDecision(BaseModel):
    """Result returned by the guardrail evaluator."""

    action: GuardrailAction
    reason: str = ""


class PolicyGuardrailsService:
    """Very small conservative content filter for obvious disallowed input."""

    _blocked_terms = {
        "spam",
        "phishing",
        "malware",
        "credit card",
        "password",
    }

    def evaluate(self, message: str) -> GuardrailDecision:
        """Return a block decision only for empty or obviously unsafe messages."""

        text = (message or "").strip().lower()
        if not text:
            return GuardrailDecision(
                action=GuardrailAction.block,
                reason="Empty message",
            )

        if any(term in text for term in self._blocked_terms):
            return GuardrailDecision(
                action=GuardrailAction.block,
                reason="Message matched a blocked policy term",
            )

        return GuardrailDecision(action=GuardrailAction.allow, reason="Allowed")