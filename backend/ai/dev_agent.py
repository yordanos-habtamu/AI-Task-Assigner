"""
Developer Analyzer Agent
Uses LangChain to analyze developer profiles and extract structured information.
"""

import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field


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
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Developer Analyzer.
        
        Args:
            api_key: OpenAI API key. If not provided, will use OPENAI_API_KEY env variable.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key.")
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=self.api_key
        )
        
        self.parser = JsonOutputParser(pydantic_object=DeveloperAnalysis)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert software engineering manager analyzing developer profiles.
Your task is to extract structured information from developer data to help assign tasks effectively.

{format_instructions}

Consider workload, skills, experience, and preferences in your analysis."""),
            ("user", """Analyze the following developer:

ID: {id}
Name: {name}
Skills: {skills}
Experience: {experience_years} years
Current Workload: {current_workload_hours}h / {max_capacity_hours}h
Recent Performance: {recent_performance}
Preferences: {preferences}

Extract strengths, weaknesses, preferred skills, workload state, availability, and skill match score.""")
        ])
        
        self.chain = self.prompt | self.llm | self.parser
    
    def analyze(self, developer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a developer profile and return structured information.
        
        Args:
            developer: Dictionary containing developer information
            
        Returns:
            Dictionary with analysis results
        """
        result = self.chain.invoke({
            "id": developer.get("id", ""),
            "name": developer.get("name", ""),
            "skills": ", ".join(developer.get("skills", [])),
            "experience_years": developer.get("experience_years", 0),
            "current_workload_hours": developer.get("current_workload_hours", 0),
            "max_capacity_hours": developer.get("max_capacity_hours", 40),
            "recent_performance": developer.get("recent_performance", "unknown"),
            "preferences": ", ".join(developer.get("preferences", [])),
            "format_instructions": self.parser.get_format_instructions()
        })
        
        # Add original developer ID and name to result
        result["developer_id"] = developer.get("id")
        result["developer_name"] = developer.get("name")
        
        return result
