"""
Data Source Manager
Handles smart selection between GitHub API and JSON upload.
"""

from typing import List, Dict, Any, Optional, Tuple
from backend.github_connector import GitHubConnector
from backend.database import get_database, Repository
from backend.crud import RepositoryService, IssueService, DeveloperService
import json


class DataSourceManager:
    """Manages data sources (GitHub or JSON) and database storage."""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize data source manager.
        
        Args:
            github_token: GitHub Personal Access Token (optional)
        """
        self.github = GitHubConnector(github_token)
        self.db = get_database()
    
    def detect_repo_state(self, repo_url: str) -> Tuple[bool, int]:
        """
        Detect if a repository has issues.
        
        Args:
            repo_url: GitHub repository URL or 'owner/repo'
            
        Returns:
            Tuple of (has_issues: bool, issue_count: int)
        """
        try:
            has_issues = self.github.check_repo_has_issues(repo_url)
            repo = self.github.get_repository(repo_url)
            return has_issues, repo.open_issues_count
        except Exception as e:
            raise ValueError(f"Failed to check repository: {str(e)}")
    
    def get_data_from_github(self, repo_url: str, max_issues: int = 100, 
                            max_contributors: int = 50) -> Tuple[List[Dict], List[Dict], int]:
        """
        Fetch data from GitHub and store in database.
        
        Args:
            repo_url: GitHub repository URL
            max_issues: Maximum issues to fetch
            max_contributors: Maximum contributors to fetch
            
        Returns:
            Tuple of (issues, developers, repo_id)
        """
        # Parse repo URL
        owner, repo_name = self.github.parse_repo_url(repo_url)
        full_repo_name = f"{owner}/{repo_name}"
        
        # Check if repo exists in database
        session = self.db.get_session()
        try:
            repo = RepositoryService.get_by_url(session, full_repo_name)
            
            if not repo:
                # Create new repository record
                repo = RepositoryService.create(
                    session,
                    url=full_repo_name,
                    name=repo_name,
                    owner=owner,
                    has_issues=True
                )
                print(f"✓ Created repository record: {full_repo_name}")
            else:
                print(f"✓ Using existing repository: {full_repo_name}")
            
            # Fetch issues from GitHub
            print("\nFetching data from GitHub...")
            github_issues = self.github.fetch_issues(repo_url, max_issues=max_issues)
            
            # Store issues in database
            issues = []
            for gh_issue in github_issues:
                issue = IssueService.create(
                    session,
                    repo_id=repo.id,
                    title=gh_issue['title'],
                    description=gh_issue['description'],
                    labels=gh_issue['labels'],
                    estimated_hours=gh_issue.get('estimated_hours'),
                    github_id=gh_issue['github_id'],
                    github_url=gh_issue['github_url']
                )
                issues.append(self._issue_to_dict(issue))
            
            print(f"✓ Stored {len(issues)} issues in database")
            
            # Fetch contributors from GitHub
            github_devs = self.github.fetch_contributors(repo_url, max_contributors=max_contributors)
            
            # Store developers in database
            developers = []
            for gh_dev in github_devs:
                # Check if developer already exists
                existing = DeveloperService.get_by_github_username(session, gh_dev['github_username'])
                
                if not existing:
                    dev = DeveloperService.create(
                        session,
                        repo_id=repo.id,
                        name=gh_dev['name'],
                        skills=gh_dev['skills'],
                        experience_years=gh_dev['experience_years'],
                        github_username=gh_dev['github_username'],
                        current_workload_hours=gh_dev['current_workload_hours'],
                        max_capacity_hours=gh_dev['max_capacity_hours'],
                        recent_performance=gh_dev['recent_performance'],
                        preferences=gh_dev['preferences']
                    )
                    developers.append(self._developer_to_dict(dev))
                else:
                    developers.append(self._developer_to_dict(existing))
            
            print(f"✓ Stored {len(developers)} developers in database")
            
            # Update sync time
            RepositoryService.update_sync_time(session, repo.id)
            
            return issues, developers, repo.id
            
        finally:
            session.close()
    
    def get_data_from_json(self, issues_json: List[Dict], developers_json: List[Dict],
                          repo_name: str = "Manual Upload") -> Tuple[List[Dict], List[Dict], int]:
        """
        Load data from JSON and store in database.
        
        Args:
            issues_json: List of issue dictionaries
            developers_json: List of developer dictionaries  
            repo_name: Name for the manual project
            
        Returns:
            Tuple of (issues, developers, repo_id)
        """
        session = self.db.get_session()
        try:
            # Create or get repository
            repo = RepositoryService.get_by_url(session, repo_name)
            
            if not repo:
                repo = RepositoryService.create(
                    session,
                    url=repo_name,
                    name=repo_name,
                    owner="Manual",
                    has_issues=False  # Manual upload
                )
                print(f"✓ Created manual project: {repo_name}")
            
            # Store issues
            issues = []
            for issue_data in issues_json:
                issue = IssueService.create(
                    session,
                    repo_id=repo.id,
                    title=issue_data['title'],
                    description=issue_data.get('description', ''),
                    labels=issue_data.get('labels', []),
                    estimated_hours=issue_data.get('estimated_hours'),
                    github_id=issue_data.get('id')
                )
                issues.append(self._issue_to_dict(issue))
            
            print(f"✓ Stored {len(issues)} issues from JSON")
            
            # Store developers
            developers = []
            for dev_data in developers_json:
                dev = DeveloperService.create(
                    session,
                    repo_id=repo.id,
                    name=dev_data['name'],
                    skills=dev_data.get('skills', []),
                    experience_years=dev_data.get('experience_years', 0),
                    current_workload_hours=dev_data.get('current_workload_hours', 0),
                    max_capacity_hours=dev_data.get('max_capacity_hours', 40),
                    recent_performance=dev_data.get('recent_performance', 'good'),
                    preferences=dev_data.get('preferences', [])
                )
                developers.append(self._developer_to_dict(dev))
            
            print(f"✓ Stored {len(developers)} developers from JSON")
            
            return issues, developers, repo.id
            
        finally:
            session.close()
    
    def _issue_to_dict(self, issue) -> Dict[str, Any]:
        """Convert database Issue to dictionary."""
        return {
            "id": issue.github_id or f"ISSUE-{issue.id}",
            "title": issue.title,
            "description": issue.description or "",
            "labels": issue.labels or [],
            "estimated_hours": issue.estimated_hours
        }
    
    def _developer_to_dict(self, dev) -> Dict[str, Any]:
        """Convert database Developer to dictionary."""
        return {
            "id": dev.github_username or f"DEV-{dev.id}",
            "name": dev.name,
            "skills": dev.skills or [],
            "experience_years": dev.experience_years,
            "current_workload_hours": dev.current_workload_hours,
            "max_capacity_hours": dev.max_capacity_hours,
            "recent_performance": dev.recent_performance,
            "preferences": dev.preferences or []
        }
