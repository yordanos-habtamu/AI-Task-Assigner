"""
Backend Entry Point
Loads data and runs the task assignment workflow.
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add backend to path for imports
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir.parent))

from backend.ai.graph import run_graph


def load_json_file(filepath: str) -> List[Dict[str, Any]]:
    """Load and parse a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}")
        sys.exit(1)


def save_assignments(assignments: List[Dict[str, Any]], output_file: str = "assignments.json"):
    """Save assignments to a JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(assignments, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Assignments saved to: {output_file}")
    except Exception as e:
        print(f"Error saving assignments: {e}")


def print_assignments(assignments: List[Dict[str, Any]]):
    """Pretty print assignments to console."""
    print("\n" + "="*60)
    print("TASK ASSIGNMENTS")
    print("="*60)
    
    for i, assignment in enumerate(assignments, 1):
        print(f"\n{i}. Issue: {assignment['issue_id']}")
        print(f"   Assigned to: {assignment['developer_name']} ({assignment['assigned_to']})")
        print(f"   Confidence: {assignment['confidence_score']}/10")
        print(f"   Reason: {assignment['reason']}")
    
    print("\n" + "="*60 + "\n")


def main():
    """Main entry point for the backend."""
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY='your-api-key'")
        sys.exit(1)
    
    # Define data file paths
    data_dir = backend_dir / "data"
    issues_file = data_dir / "issues.json"
    developers_file = data_dir / "developers.json"
    
    print("Loading data files...")
    issues = load_json_file(str(issues_file))
    developers = load_json_file(str(developers_file))
    
    print(f"✓ Loaded {len(issues)} issues")
    print(f"✓ Loaded {len(developers)} developers\n")
    
    try:
        # Run the workflow
        assignments = run_graph(issues, developers, api_key)
        
        # Display results
        print_assignments(assignments)
        
        # Save to file
        output_file = backend_dir.parent / "assignments.json"
        save_assignments(assignments, str(output_file))
        
    except Exception as e:
        print(f"\n❌ Error running workflow: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
