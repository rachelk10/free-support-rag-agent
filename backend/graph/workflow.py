from models import AgentState, TriageRequest
from nodes.router import RouterNode
from nodes.worker import WorkerNode
from nodes.evaluator import EvaluatorNode
from nodes.hitl import HITLNode
from nodes.end_node import EndNode
from config import get_config
from services.llm_service import LLMService
from services.policy_guardrails import PolicyGuardrailsService, GuardrailAction


class ContactAgentWorkflow:
    def __init__(self):
        self.config = get_config()
        llm = LLMService()
        self.router = RouterNode(llm)
        self.worker = WorkerNode(llm)
        self.evaluator = EvaluatorNode(llm)
        self.hitl = HITLNode()
        self.end = EndNode()
        self.guardrails = PolicyGuardrailsService()

    def run(self, message: str) -> str:
        guardrail_decision = self.guardrails.evaluate(message)
        if guardrail_decision.action == GuardrailAction.block:
            return "Request blocked: content is not allowed by policy."

        state = AgentState(request=TriageRequest(message=message))

        # Step 1: Router
        state.router_decision = self.router.run(state.request)

        # Step 2: Worker + Evaluator loop
        while True:
            state.worker_output = self.worker.run(state)
            state.evaluator_result = self.evaluator.run(state)

            if state.evaluator_result.passed:
                break

            if state.retry_count >= self.config.max_retries:
                break

            state.retry_count += 1

        # Step 3: HITL if needed
        if state.evaluator_result and state.evaluator_result.needs_human:
            state.approval_request = self.hitl.run(state)

            # אם נדחה על ידי האדם — סיים עם הערה
            if not state.approval_request.approved:
                state.final_output = (
                    f"Request rejected by human agent."
                    + (f" Reason: {state.approval_request.comment}" if state.approval_request.comment else "")
                )
                return state.final_output

        # Step 4: End
        state.final_output = self.end.run(state)
        return state.final_output
