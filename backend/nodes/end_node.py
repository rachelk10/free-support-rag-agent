from models import AgentState, OutputType


class EndNode:
    """
    End Node

    יוצר את הפלט הסופי על בסיס תוצאת ה-Worker או המשוב האנושי מ-HITL.
    """

    def run(self, state: AgentState) -> str:
        # עדיפות: אם היה HITL ויש edited_output — השתמש בו
        if state.approval_request and state.approval_request.edited_output:
            worker = state.approval_request.edited_output
        else:
            worker = state.worker_output

        if not worker:
            return "Error: no output produced."

        if worker.output_type == OutputType.reply:
            final = worker.reply_text or "No reply generated."

        elif worker.output_type == OutputType.github_issue:
            issue = worker.issue
            if issue:
                final = (
                    f"GitHub Issue Created\n"
                    f"Title   : {issue.title}\n"
                    f"Severity: {issue.severity}\n"
                    f"Labels  : {', '.join(issue.labels) if issue.labels else 'none'}\n"
                    f"Body    :\n{issue.body}"
                )
            else:
                final = "Error: issue data missing."

        elif worker.output_type == OutputType.human_handoff:
            comment = (
                state.approval_request.comment
                if state.approval_request
                else None
            )
            final = (
                f"Transferred to human agent."
                + (f" Note: {comment}" if comment else "")
            )

        elif worker.output_type == OutputType.blocked:
            final = "Request blocked: content is not allowed."

        else:
            final = "Unknown output type."

        return final
