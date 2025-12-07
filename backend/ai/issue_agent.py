"""
Issue Analyzer Agent
Uses LangChain with pluggable LLM providers to analyze GitHub issues.
"""

import os
from typing import Dict, Any
from pydantic import BaseModel, Field
from backend.ai.llm_provider import LLMProvider, create_provider


class IssueAnalysis(BaseModel):
    """Structured output for issue analysis."""
    required_skills: list[str] = Field(description="List of technical skills required to complete this issue")
    difficulty: str = Field(description="Difficulty level: 'easy', 'medium', 'hard', or 'expert'")
    summary: str = Field(description="Brief summary of what the issue entails")
    estimated_complexity: int = Field(description="Complexity score from 1-10")


class IssueAnalyzer:
    """Analyzes issues to extract structured information for assignment."""
    
    def __init__(self, provider: LLMProvider = None):
        """
        Initialize the Issue Analyzer.
        
        Args:
            provider: LLMProvider instance. If not provided, will create from environment variables.
        """
        if provider is None:
            # Create provider from environment
            provider_type = os.getenv("AI_PROVIDER", "openai")
            provider = create_provider(provider_type)
        
        self.provider = provider
        
        self.system_prompt = """You are an expert software engineering manager analyzing GitHub issues.
Your task is to extract structured information from issue descriptions to help assign them to developers.

Be precise and thoughtful in your analysis."""
    
    def analyze(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze an issue and return structured information.
        
        Args:
            issue: Dictionary containing issue information (id, title, description, labels, estimated_hours)
            
        Returns:
            Dictionary with analysis results
        """
        user_prompt = f"""Analyze the following issue:

ID: {issue.get("id", "")}
Title: {issue.get("title", "")}
Description: {issue.get("description", "")}
Labels: {", ".join(issue.get("labels", []))}
Estimated Hours: {issue.get("estimated_hours", 0)}

Extract the required skills, difficulty level, summary, and complexity score."""
        
        result = self.provider.get_json_completion(
            prompt=user_prompt,
            system_prompt=self.system_prompt,
            schema=IssueAnalysis
        )
        
        # Add original issue ID to result
        result["issue_id"] = issue.get("id")
        
        return result
