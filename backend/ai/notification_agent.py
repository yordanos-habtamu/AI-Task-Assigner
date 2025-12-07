"""
Notification Agent
Uses LangChain with pluggable LLM providers to generate notification templates.
"""

import os
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from backend.ai.llm_provider import LLMProvider, create_provider


class NotificationDraft(BaseModel):
    """Structured output for notification drafts."""
    jira_title: str = Field(description="Professional title for the Jira ticket")
    jira_description: str = Field(description="Detailed description for the Jira ticket including context and requirements")
    jira_priority: str = Field(description="Suggested priority: High, Medium, or Low")
    slack_message: str = Field(description="Friendly, direct message to the developer for Slack")
    messenger_message: str = Field(description="Brief, casual update message for Messenger/WhatsApp")


class NotificationResult(BaseModel):
    """Container for multiple notification drafts."""
    notifications: List[NotificationDraft] = Field(description="List of notification drafts corresponding to assignments")


class NotificationAgent:
    """Generates notification templates for assignments."""
    
    def __init__(self, provider: LLMProvider = None):
        """
        Initialize the Notification Agent.
        
        Args:
            provider: LLMProvider instance. If not provided, will create from environment variables.
        """
        if provider is None:
            # Create provider from environment
            provider_type = os.getenv("AI_PROVIDER", "openai")
            provider = create_provider(provider_type)
        
        self.provider = provider
        
        self.system_prompt = """You are an expert technical project manager.
Your goal is to draft professional and effective notifications for task assignments.

For each assignment, generate:
1. **Jira Ticket**: Formal, detailed, clear requirements.
2. **Slack Message**: Friendly, encouraging, direct mention of the task.
3. **Messenger/WhatsApp**: Short, concise status update.

Tone:
- Jira: Professional, structured, objective.
- Slack: Collaborative, friendly, motivating.
- Messenger: Brief, informational."""
    
    def generate(self, assignments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate notification drafts for a list of assignments.
        
        Args:
            assignments: List of assignment dictionaries
            
        Returns:
            List of dictionaries containing notification drafts
        """
        if not assignments:
            return []
            
        # Format assignments for prompt
        assignments_text = "\n\n".join([
            f"Assignment {i+1}:\n" +
            f"  Issue ID: {a.get('issue_id')}\n" +
            f"  Developer: {a.get('developer_name')}\n" +
            f"  Reason: {a.get('reason')}\n" +
            f"  Confidence: {a.get('confidence_score')}"
            for i, a in enumerate(assignments)
        ])
        
        user_prompt = f"""Generate notification drafts for the following assignments:

{assignments_text}

For each assignment, provide a Jira ticket draft, a Slack message, and a Messenger update."""
        
        result = self.provider.get_json_completion(
            prompt=user_prompt,
            system_prompt=self.system_prompt,
            schema=NotificationResult
        )
        
        # Merge drafts with original assignment data
        notifications = []
        for i, draft in enumerate(result.get("notifications", [])):
            if i < len(assignments):
                notification_data = draft.dict()
                notification_data.update(assignments[i])
                notifications.append(notification_data)
                
        return notifications
