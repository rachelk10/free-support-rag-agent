from models import AgentState, ApprovalRequest, WorkerOutput, OutputType


class HITLNode:
    """
    Human-in-the-Loop Node

    מציג את תוצאת ה-Worker למשתמש אנושי ומבקש אישור.
    בשלב זה: קלט מהטרמינל.
    בגרסת fullstack: ימתין ל-API endpoint.
    """

    def run(self, state: AgentState) -> ApprovalRequest:
        worker = state.worker_output

        self._display(state)

        choice = self._prompt_choice()

        if choice == "a":
            return ApprovalRequest(approved=True)

        if choice == "r":
            comment = input("סיבת הדחייה (אופציונלי): ").strip() or None
            return ApprovalRequest(approved=False, comment=comment)

        # edit
        edited = self._prompt_edit(worker)
        return ApprovalRequest(approved=True, edited_output=edited)

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def _display(self, state: AgentState):
        worker = state.worker_output
        decision = state.router_decision

        print("\n" + "=" * 60)
        print("HUMAN REVIEW REQUIRED")
        print("=" * 60)
        print(f"Message   : {state.request.message}")
        print(f"Category  : {decision.category if decision else 'unknown'}")
        print(f"Output type: {worker.output_type if worker else 'none'}")

        if worker:
            if worker.output_type == OutputType.reply:
                print(f"Reply     : {worker.reply_text}")
            elif worker.output_type == OutputType.github_issue and worker.issue:
                print(f"Issue title: {worker.issue.title}")
                print(f"Issue body : {worker.issue.body}")
                print(f"Severity  : {worker.issue.severity}")
            if worker.notes:
                print(f"Notes     : {worker.notes}")

        if state.evaluator_result:
            print(f"Evaluator : {state.evaluator_result.feedback}")

        print("=" * 60)

    def _prompt_choice(self) -> str:
        while True:
            choice = input("[a] Approve  [r] Reject  [e] Edit > ").strip().lower()
            if choice in ("a", "r", "e"):
                return choice
            print("בחרי a / r / e")

    def _prompt_edit(self, worker: WorkerOutput | None) -> WorkerOutput:
        print("\nעריכה — השאירי ריק לשמירת הערך הקיים.")

        if worker and worker.output_type == OutputType.reply:
            new_text = input(f"Reply [{worker.reply_text}]: ").strip()
            return WorkerOutput(
                output_type=OutputType.reply,
                reply_text=new_text or worker.reply_text,
                notes=worker.notes if worker else None,
            )

        if worker and worker.output_type == OutputType.github_issue and worker.issue:
            new_title = input(f"Title [{worker.issue.title}]: ").strip()
            new_body = input(f"Body [{worker.issue.body}]: ").strip()
            from models import IssueDraft
            edited_issue = IssueDraft(
                title=new_title or worker.issue.title,
                body=new_body or worker.issue.body,
                labels=worker.issue.labels,
                severity=worker.issue.severity,
            )
            return WorkerOutput(
                output_type=OutputType.github_issue,
                issue=edited_issue,
                notes=worker.notes,
            )

        # fallback — מחזיר כמו שהיה
        return worker or WorkerOutput(output_type=OutputType.human_handoff)
