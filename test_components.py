"""
Simple test script to verify GitHub connector and database.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.github_connector import GitHubConnector
from backend.database import get_database
from backend.data_source_manager import DataSourceManager


def test_database():
    """Test database initialization."""
    print("\n" + "="*60)
    print("Testing Database...")
    print("="*60)
    
    try:
        db = get_database()
        session = db.get_session()
        print("✓ Database initialized successfully")
        print(f"✓ Database location: task_assignments.db")
        session.close()
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False


def test_github_connector():
    """Test GitHub connector with a public repo."""
    print("\n" + "="*60)
    print("Testing GitHub Connector...")
    print("="*60)
    
    try:
        connector = GitHubConnector()
        
        # Test with a small public repo
        print("\nTesting with public repo: octocat/Hello-World")
        
        # Parse URL
        owner, repo = connector.parse_repo_url("octocat/Hello-World")
        print(f"✓ Parsed repo: {owner}/{repo}")
        
        # Get repo
        repo_obj = connector.get_repository("octocat/Hello-World")
        print(f"✓ Connected to repo: {repo_obj.full_name}")
        
        # Check for issues
        has_issues = connector.check_repo_has_issues("octocat/Hello-World")
        print(f"✓ Has issues: {has_issues}")
        
        # Get rate limit info
        rate_limit = connector.get_rate_limit_info()
        print(f"✓ GitHub API rate limit: {rate_limit['core']['remaining']}/{rate_limit['core']['limit']} remaining")
        
        return True
        
    except Exception as e:
        print(f"✗ GitHub connector test failed: {e}")
        return False


def test_data_source_manager():
    """Test data source manager."""
    print("\n" + "="*60)
    print("Testing Data Source Manager...")
    print("="*60)
    
    try:
        manager = DataSourceManager()
        
        # Test repo detection
        print("\nTesting repo state detection...")
        has_issues, count = manager.detect_repo_state("octocat/Hello-World")
        print(f"✓ Repo has {count} issues")
        
        return True
        
    except Exception as e:
        print(f"✗ Data source manager test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 AI Task Assignment System - Component Tests")
    print("="*60)
    
    results = {
        "Database": test_database(),
        "GitHub Connector": test_github_connector(),
        "Data Source Manager": test_data_source_manager()
    }
    
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All tests passed!")
        print("\nYou can now run the application with: ./run.sh")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
