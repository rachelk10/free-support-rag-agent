from models import AgentState, EvaluatorResult, OutputType
from services.llm_service import LLMService


class EvaluatorNode:
    MAX_RETRIES = 3

    def __init__(self, llm: LLMService):
        self.llm = llm

    def build_messages(self, state: AgentState):
        worker = state.worker_output
        decision = state.router_decision
        output_type = worker.output_type if worker else "unknown"

        # Build context section — only include fields relevant to output_type
        if output_type == OutputType.reply:
            output_context = f"reply_text: {worker.reply_text}"
        elif output_type == OutputType.github_issue:
            issue = worker.issue
            output_context = (
                f"issue title: {issue.title if issue else 'MISSING'}\n"
                f"issue body: {issue.body if issue else 'MISSING'}\n"
                f"severity: {issue.severity if issue else 'MISSING'}"
            )
        elif output_type in (OutputType.human_handoff, OutputType.blocked):
            output_context = f"notes: {worker.notes or 'none provided'}"
        else:
            output_context = "no output"

        system_prompt = """
You are a quality evaluator for an AI customer support system.

Evaluate the worker's output based ONLY on the output_type. Do not check fields that are irrelevant.

Rules per output_type:
- "reply": Is reply_text helpful, relevant, and professional? Problem: empty or off-topic reply.
- "github_issue": Does the issue have a clear title and body? Problem: title or body missing or vague.
- "human_handoff": Is escalation justified given the category and message? Problem: unnecessary escalation.
- "blocked": Is blocking justified? Problem: blocking seems too aggressive.

Return:
- passed: true if the output is acceptable for its type
- feedback: short explanation of your decision
- needs_human: true only if you recommend human review (not just because it is a human_handoff)
""".strip()

        user_prompt = f"""
Original message:
{state.request.message}

Router category: {decision.category if decision else "unknown"}
Router reason: {decision.reason if decision else "none"}

Worker output_type: {output_type}
{output_context}

Retry count: {state.retry_count}
""".strip()

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def run(self, state: AgentState) -> EvaluatorResult:
        worker = state.worker_output

        # Worker already decided to escalate — no evaluation needed
        if worker and worker.output_type == OutputType.human_handoff:
            return EvaluatorResult(
                passed=True,
                feedback="Worker escalated to human — skipping evaluation.",
                needs_human=True,
            )

        # Blocked content — trust worker guardrail, no retry needed
        if worker and worker.output_type == OutputType.blocked:
            return EvaluatorResult(
                passed=True,
                feedback="Request was blocked by worker.",
                needs_human=False,
            )

        messages = self.build_messages(state)

        result = self.llm.generate_structured(
            messages=messages,
            response_model=EvaluatorResult,
            temperature=0.0,
        )

        # After max retries with no pass → force human
        if not result.passed and state.retry_count >= self.MAX_RETRIES:
            result.needs_human = True

        return result