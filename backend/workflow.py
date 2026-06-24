"""Compatibility wrapper for the contact agent workflow.

This module keeps the historical import path `workflow.ContactAgentWorkflow`
working while the actual implementation lives in `graph.workflow`.
"""

from graph.workflow import ContactAgentWorkflow


__all__ = ["ContactAgentWorkflow"]
