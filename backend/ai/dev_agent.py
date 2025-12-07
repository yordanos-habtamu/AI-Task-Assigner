"""
Developer Analyzer Agent
Uses LangChain with pluggable LLM providers to analyze developer profiles.
"""

import os
from typing import Dict, Any
from pydantic import BaseModel, Field
from backend.ai.llm_provider import LLMProvider, create_provider


class DeveloperAnalysis(BaseModel):
    """Structured output for developer analysis."""
    strengths: list[str] = Field(description="Key technical strengths and areas of expertise")
    weaknesses: list[str] = Field(description="Areas where the developer has less experience")
    preferred_skills: list[str] = Field(description="Skills the developer prefers to work with")
    workload_state: str = Field(description="Current workload state: 'available', 'moderate', 'busy', or 'overloaded'")
    availability_hours: int = Field(description="Available hours for new work")
    skill_match_score: int = Field(description="Overall skill versatility score from 1-10")


class DeveloperAnalyzer:
    """Analyzes developer profiles to extract structured information for assignment."""
    
    def __init__(self, provider: LLMProvider = None):
        """
        Initialize the Developer Analyzer.
        
        Args:
            provider: LLMProvider instance. If not provided, will create from environment variables.
        """
        if provider is None:
            # Create provider from environment
            provider_type = os.getenv("AI_PROVIDER", "openai")
            provider = create_provider(provider_type)
        
        self.provider = provider
        
        self.system_prompt = """You are an expert software engineering manager analyzing developer profiles.
Your task is to extract structured information from developer data to help assign tasks effectively.

Consider workload, skills, experience, and preferences in your analysis."""
    
    def analyze(self, developer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a developer profile and return structured information.
        
        Args:
            developer: Dictionary containing developer information
            
        Returns:
            Dictionary with analysis results
        """
        user_prompt = f"""Analyze the following developer:

ID: {developer.get("id", "")}
Name: {developer.get("name", "")}
Skills: {", ".join(developer.get("skills", []))}
Experience: {developer.get("experience_years", 0)} years
Current Workload: {developer.get("current_workload_hours", 0)}h / {developer.get("max_capacity_hours", 40)}h
Recent Performance: {developer.get("recent_performance", "unknown")}
Preferences: {", ".join(developer.get("preferences", []))}

Extract strengths, weaknesses, preferred skills, workload state, availability, and skill match score."""
        
        result = self.provider.get_json_completion(
            prompt=user_prompt,
            system_prompt=self.system_prompt,
            schema=DeveloperAnalysis
        )
        
        # Add original developer ID and name to result
        result["developer_id"] = developer.get("id")
        result["developer_name"] = developer.get("name")
        
        return result
