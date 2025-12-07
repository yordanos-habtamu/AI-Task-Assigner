"""
LangGraph Workflow
Orchestrates the multi-agent workflow for task assignment.
"""

import os
from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END
from backend.ai.issue_agent import IssueAnalyzer
from backend.ai.dev_agent import DeveloperAnalyzer
from backend.ai.assign_agent import AssignmentAgent
from backend.ai.notification_agent import NotificationAgent


class WorkflowState(TypedDict):
    """State passed through the workflow."""
    issues: List[Dict[str, Any]]
    developers: List[Dict[str, Any]]
    analyzed_issues: List[Dict[str, Any]]
    analyzed_developers: List[Dict[str, Any]]
    assignments: List[Dict[str, Any]]
    notifications: List[Dict[str, Any]]
    api_key: str
    model_name: str
    provider_type: str


def analyze_issues_node(state: WorkflowState) -> WorkflowState:
    """Node to analyze all issues."""
    print("Analyzing issues...")
    
    # Create provider with explicit settings from state
    from backend.ai.llm_provider import create_provider
    provider = create_provider(
        provider_type=state.get("provider_type", "openai"),
        api_key=state.get("api_key"),
        model=state.get("model_name")
    )
    
    issue_analyzer = IssueAnalyzer(provider=provider)
    
    analyzed_issues = []
    for i, issue in enumerate(state["issues"], 1):
        print(f"  Analyzing issue {i}/{len(state['issues'])}: {issue.get('id')}")
        analyzed = issue_analyzer.analyze(issue)
        analyzed_issues.append(analyzed)
    
    state["analyzed_issues"] = analyzed_issues
    return state


def analyze_developers_node(state: WorkflowState) -> WorkflowState:
    """Node to analyze all developers."""
    print("Analyzing developers...")
    
    # Create provider with explicit settings from state
    from backend.ai.llm_provider import create_provider
    provider = create_provider(
        provider_type=state.get("provider_type", "openai"),
        api_key=state.get("api_key"),
        model=state.get("model_name")
    )
    
    dev_analyzer = DeveloperAnalyzer(provider=provider)
    
    analyzed_developers = []
    for i, developer in enumerate(state["developers"], 1):
        print(f"  Analyzing developer {i}/{len(state['developers'])}: {developer.get('name')}")
        analyzed = dev_analyzer.analyze(developer)
        analyzed_developers.append(analyzed)
    
    state["analyzed_developers"] = analyzed_developers
    return state


def assign_tasks_node(state: WorkflowState) -> WorkflowState:
    """Node to assign tasks to developers."""
    print("Assigning tasks...")
    
    # Create provider with explicit settings from state
    from backend.ai.llm_provider import create_provider
    provider = create_provider(
        provider_type=state.get("provider_type", "openai"),
        api_key=state.get("api_key"),
        model=state.get("model_name")
    )
    
    assignment_agent = AssignmentAgent(provider=provider)
    
    assignments = assignment_agent.assign(
        state["analyzed_issues"],
        state["analyzed_developers"]
    )
    
    state["assignments"] = assignments
    print(f"  Created {len(assignments)} assignments")
    return state


def generate_notifications_node(state: WorkflowState) -> WorkflowState:
    """Node to generate notifications for assignments."""
    print("Generating notifications...")
    
    # Create provider with explicit settings from state
    from backend.ai.llm_provider import create_provider
    provider = create_provider(
        provider_type=state.get("provider_type", "openai"),
        api_key=state.get("api_key"),
        model=state.get("model_name")
    )
    
    notification_agent = NotificationAgent(provider=provider)
    
    notifications = notification_agent.generate(state["assignments"])
    
    state["notifications"] = notifications
    print(f"  Generated {len(notifications)} notification drafts")
    return state


def create_workflow() -> StateGraph:
    """Create the LangGraph workflow."""
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("analyze_issues", analyze_issues_node)
    workflow.add_node("analyze_developers", analyze_developers_node)
    workflow.add_node("assign_tasks", assign_tasks_node)
    workflow.add_node("generate_notifications", generate_notifications_node)
    
    # Add edges
    workflow.set_entry_point("analyze_issues")
    workflow.add_edge("analyze_issues", "analyze_developers")
    workflow.add_edge("analyze_developers", "assign_tasks")
    workflow.add_edge("assign_tasks", "generate_notifications")
    workflow.add_edge("generate_notifications", END)
    
    return workflow.compile()


def run_graph(
    issues: List[Dict[str, Any]], 
    developers: List[Dict[str, Any]], 
    api_key: str = None,
    model_name: str = None,
    provider_type: str = None
) -> List[Dict[str, Any]]:
    """
    Run the complete workflow.
    
    Args:
        issues: List of issue dictionaries
        developers: List of developer dictionaries
        api_key: API key (optional, overrides env)
        model_name: Model name (optional, overrides env)
        provider_type: Provider type (optional, overrides env)
        
    Returns:
        List of assignments
    """
    # Determine provider settings
    provider_type = provider_type or os.getenv("AI_PROVIDER", "openai").lower()
    
    # Validation
    if provider_type == "openai":
        if not (api_key or os.getenv("OPENAI_API_KEY")):
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY or pass api_key parameter.")
    elif provider_type == "gemini":
        if not (api_key or os.getenv("GOOGLE_API_KEY")):
            raise ValueError("Google API key required. Set GOOGLE_API_KEY environment variable or pass api_key parameter.")
    elif provider_type == "ollama":
        # Ollama doesn't need API key, but should be running
        print(f"Using Ollama at {os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')}")
    
    print("\n" + "="*60)
    print(f"Starting Task Assignment Workflow ({provider_type.upper()} Provider)")
    if model_name:
        print(f"Model: {model_name}")
    print("="*60)
    
    workflow = create_workflow()
    
    initial_state: WorkflowState = {
        "issues": issues,
        "developers": developers,
        "analyzed_issues": [],
        "analyzed_developers": [],
        "assignments": [],
        "notifications": [],
        "api_key": api_key,
        "model_name": model_name,
        "provider_type": provider_type
    }
    
    final_state = workflow.invoke(initial_state)
    
    print("="*60)
    print("Workflow completed successfully!")
    print("="*60 + "\n")
    
    return final_state["notifications"]
