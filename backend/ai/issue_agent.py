"""
Issue Analyzer Agent
Uses LangChain to analyze GitHub issues and extract structured information.
"""

import os
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field


class IssueAnalysis(BaseModel):
    """Structured output for issue analysis."""
    required_skills: list[str] = Field(description="List of technical skills required to complete this issue")
    difficulty: str = Field(description="Difficulty level: 'easy', 'medium', 'hard', or 'expert'")
    summary: str = Field(description="Brief summary of what the issue entails")
    estimated_complexity: int = Field(description="Complexity score from 1-10")


class IssueAnalyzer:
    """Analyzes issues to extract structured information for assignment."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Issue Analyzer.
        
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
        
        self.parser = JsonOutputParser(pydantic_object=IssueAnalysis)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert software engineering manager analyzing GitHub issues.
Your task is to extract structured information from issue descriptions to help assign them to developers.

{format_instructions}

Be precise and thoughtful in your analysis."""),
            ("user", """Analyze the following issue:

ID: {id}
Title: {title}
Description: {description}
Labels: {labels}
Estimated Hours: {estimated_hours}

Extract the required skills, difficulty level, summary, and complexity score.""")
        ])
        
        self.chain = self.prompt | self.llm | self.parser
    
    def analyze(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze an issue and return structured information.
        
        Args:
            issue: Dictionary containing issue information (id, title, description, labels, estimated_hours)
            
        Returns:
            Dictionary with analysis results
        """
        result = self.chain.invoke({
            "id": issue.get("id", ""),
            "title": issue.get("title", ""),
            "description": issue.get("description", ""),
            "labels": ", ".join(issue.get("labels", [])),
            "estimated_hours": issue.get("estimated_hours", 0),
            "format_instructions": self.parser.get_format_instructions()
        })
        
        # Add original issue ID to result
        result["issue_id"] = issue.get("id")
        
        return result
