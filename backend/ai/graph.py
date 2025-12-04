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


class WorkflowState(TypedDict):
    """State passed through the workflow."""
    issues: List[Dict[str, Any]]
    developers: List[Dict[str, Any]]
    analyzed_issues: List[Dict[str, Any]]
    analyzed_developers: List[Dict[str, Any]]
    assignments: List[Dict[str, Any]]
    api_key: str


def analyze_issues_node(state: WorkflowState) -> WorkflowState:
    """Node to analyze all issues."""
    print("Analyzing issues...")
    issue_analyzer = IssueAnalyzer(api_key=state["api_key"])
    
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
    dev_analyzer = DeveloperAnalyzer(api_key=state["api_key"])
    
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
    assignment_agent = AssignmentAgent(api_key=state["api_key"])
    
    assignments = assignment_agent.assign(
        state["analyzed_issues"],
        state["analyzed_developers"]
    )
    
    state["assignments"] = assignments
    print(f"  Created {len(assignments)} assignments")
    return state


def create_workflow() -> StateGraph:
    """Create the LangGraph workflow."""
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("analyze_issues", analyze_issues_node)
    workflow.add_node("analyze_developers", analyze_developers_node)
    workflow.add_node("assign_tasks", assign_tasks_node)
    
    # Add edges
    workflow.set_entry_point("analyze_issues")
    workflow.add_edge("analyze_issues", "analyze_developers")
    workflow.add_edge("analyze_developers", "assign_tasks")
    workflow.add_edge("assign_tasks", END)
    
    return workflow.compile()


def run_graph(issues: List[Dict[str, Any]], developers: List[Dict[str, Any]], api_key: str = None) -> List[Dict[str, Any]]:
    """
    Run the complete workflow.
    
    Args:
        issues: List of issue dictionaries
        developers: List of developer dictionaries
        api_key: OpenAI API key
        
    Returns:
        List of assignments
    """
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key.")
    
    print("\n" + "="*60)
    print("Starting Task Assignment Workflow")
    print("="*60)
    
    workflow = create_workflow()
    
    initial_state: WorkflowState = {
        "issues": issues,
        "developers": developers,
        "analyzed_issues": [],
        "analyzed_developers": [],
        "assignments": [],
        "api_key": api_key
    }
    
    final_state = workflow.invoke(initial_state)
    
    print("="*60)
    print("Workflow completed successfully!")
    print("="*60 + "\n")
    
    return final_state["assignments"]
