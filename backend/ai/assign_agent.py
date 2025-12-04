"""
Assignment Agent
Uses LangChain to intelligently assign issues to developers.
"""

import os
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field


class Assignment(BaseModel):
    """Structured output for a single assignment."""
    issue_id: str = Field(description="ID of the issue being assigned")
    assigned_to: str = Field(description="ID of the developer assigned to this issue")
    developer_name: str = Field(description="Name of the assigned developer")
    reason: str = Field(description="Detailed explanation of why this developer is the best match")
    confidence_score: int = Field(description="Confidence in this assignment from 1-10")


class AssignmentResult(BaseModel):
    """Structured output for all assignments."""
    assignments: list[Assignment] = Field(description="List of all issue assignments")


class AssignmentAgent:
    """Assigns issues to developers based on analysis results."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Assignment Agent.
        
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
        
        self.parser = JsonOutputParser(pydantic_object=AssignmentResult)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert software engineering manager making optimal task assignments.
Your goal is to assign each issue to the best-suited developer based on:
1. Skill match
2. Current workload and availability
3. Difficulty vs experience level
4. Developer preferences
5. Recent performance

{format_instructions}

IMPORTANT RULES:
- Don't overload developers who are already busy
- Match issue difficulty to developer experience
- Consider developer preferences when possible
- Balance workload across the team
- Provide clear, specific reasons for each assignment"""),
            ("user", """Make assignments for the following issues and developers:

ANALYZED ISSUES:
{issues}

ANALYZED DEVELOPERS:
{developers}

Assign each issue to the most suitable developer with detailed reasoning.""")
        ])
        
        self.chain = self.prompt | self.llm | self.parser
    
    def assign(self, analyzed_issues: List[Dict[str, Any]], analyzed_developers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Assign issues to developers based on analysis.
        
        Args:
            analyzed_issues: List of analyzed issue dictionaries
            analyzed_developers: List of analyzed developer dictionaries
            
        Returns:
            List of assignment dictionaries with issue_id, assigned_to, developer_name, reason, and confidence_score
        """
        # Format issues for prompt
        issues_text = "\n\n".join([
            f"Issue {i+1}:\n" + 
            f"  ID: {issue['issue_id']}\n" +
            f"  Skills Needed: {', '.join(issue['required_skills'])}\n" +
            f"  Difficulty: {issue['difficulty']}\n" +
            f"  Complexity: {issue['estimated_complexity']}/10\n" +
            f"  Summary: {issue['summary']}"
            for i, issue in enumerate(analyzed_issues)
        ])
        
        # Format developers for prompt
        developers_text = "\n\n".join([
            f"Developer {i+1}:\n" +
            f"  ID: {dev['developer_id']}\n" +
            f"  Name: {dev['developer_name']}\n" +
            f"  Strengths: {', '.join(dev['strengths'])}\n" +
            f"  Workload: {dev['workload_state']}\n" +
            f"  Available Hours: {dev['availability_hours']}h\n" +
            f"  Skill Match Score: {dev['skill_match_score']}/10\n" +
            f"  Preferences: {', '.join(dev['preferred_skills'])}"
            for i, dev in enumerate(analyzed_developers)
        ])
        
        result = self.chain.invoke({
            "issues": issues_text,
            "developers": developers_text,
            "format_instructions": self.parser.get_format_instructions()
        })
        
        return result["assignments"]
