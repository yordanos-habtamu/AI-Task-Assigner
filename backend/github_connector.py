"""
GitHub Repository Connector
Fetches issues and contributors from GitHub repositories.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from github import Github, GithubException, RateLimitExceededException
from github.Repository import Repository as GithubRepo
from github.Issue import Issue as GithubIssue
from github.NamedUser import NamedUser
import time


class GitHubConnector:
    """Connects to GitHub and fetches repository data."""
    
    def __init__(self, access_token: Optional[str] = None):
        """
        Initialize GitHub connector.
        
        Args:
            access_token: GitHub Personal Access Token (optional, but recommended for higher rate limits)
        """
        self.access_token = access_token or os.getenv("GITHUB_TOKEN")
        self.github = Github(self.access_token) if self.access_token else Github()
        
    def parse_repo_url(self, repo_url: str) -> Tuple[str, str]:
        """
        Parse GitHub repository URL to extract owner and repo name.
        
        Args:
            repo_url: Full GitHub URL or 'owner/repo' format
            
        Returns:
            Tuple of (owner, repo_name)
            
        Examples:
            "https://github.com/facebook/react" -> ("facebook", "react")
            "facebook/react" -> ("facebook", "react")
        """
        # Remove common URL prefixes
        repo_url = repo_url.replace("https://github.com/", "")
        repo_url = repo_url.replace("http://github.com/", "")
        repo_url = repo_url.replace("github.com/", "")
        repo_url = repo_url.strip("/")
        
        # Split by /
        parts = repo_url.split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]
        else:
            raise ValueError(f"Invalid repository URL format: {repo_url}. Expected 'owner/repo' or full GitHub URL.")
    
    def get_repository(self, repo_url: str) -> GithubRepo:
        """
        Get GitHub repository object.
        
        Args:
            repo_url: Repository URL or 'owner/repo'
            
        Returns:
            GitHub Repository object
        """
        owner, repo_name = self.parse_repo_url(repo_url)
        try:
            return self.github.get_repo(f"{owner}/{repo_name}")
        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"Repository not found: {owner}/{repo_name}")
            elif e.status == 403:
                raise ValueError(f"Access denied to repository: {owner}/{repo_name}. Check your GitHub token.")
            else:
                raise ValueError(f"GitHub API error: {e.data.get('message', str(e))}")
    
    def fetch_issues(self, repo_url: str, state: str = "open", max_issues: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch issues from a GitHub repository.
        
        Args:
            repo_url: Repository URL or 'owner/repo'
            state: Issue state ('open', 'closed', or 'all')
            max_issues: Maximum number of issues to fetch
            
        Returns:
            List of issue dictionaries in internal format
        """
        repo = self.get_repository(repo_url)
        issues = []
        
        print(f"Fetching issues from {repo.full_name}...")
        
        try:
            # Get issues (excluding pull requests)
            github_issues = repo.get_issues(state=state)
            
            count = 0
            for issue in github_issues:
                # Skip pull requests
                if issue.pull_request is not None:
                    continue
                
                # Convert to internal format
                issues.append({
                    "id": f"ISSUE-{issue.number}",
                    "github_id": str(issue.number),
                    "github_url": issue.html_url,
                    "title": issue.title,
                    "description": issue.body or "",
                    "labels": [label.name for label in issue.labels],
                    "estimated_hours": None,  # Not available from GitHub, could estimate from labels
                    "state": issue.state,
                    "created_at": issue.created_at.isoformat(),
                    "updated_at": issue.updated_at.isoformat()
                })
                
                count += 1
                if count >= max_issues:
                    break
            
            print(f"✓ Fetched {len(issues)} issues")
            return issues
            
        except RateLimitExceededException:
            raise ValueError("GitHub API rate limit exceeded. Please provide a GitHub token or wait before retrying.")
    
    def fetch_contributors(self, repo_url: str, max_contributors: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch contributors from a GitHub repository.
        
        Args:
            repo_url: Repository URL or 'owner/repo'
            max_contributors: Maximum number of contributors to fetch
            
        Returns:
            List of developer dictionaries in internal format
        """
        repo = self.get_repository(repo_url)
        developers = []
        
        print(f"Fetching contributors from {repo.full_name}...")
        
        try:
            contributors = repo.get_contributors()
            
            count = 0
            for contributor in contributors:
                # Get user details
                try:
                    user = self.github.get_user(contributor.login)
                    
                    # Estimate skills from repos (simplified - could be enhanced)
                    skills = self._estimate_skills_from_repos(user)
                    
                    developers.append({
                        "id": f"DEV-{contributor.login}",
                        "github_username": contributor.login,
                        "github_id": str(contributor.id),
                        "name": user.name or contributor.login,
                        "email": user.email or "",
                        "avatar_url": user.avatar_url,
                        "skills": skills,
                        "experience_years": self._estimate_experience(user),
                        "current_workload_hours": 0,  # Unknown, will be managed internally
                        "max_capacity_hours": 40,
                        "recent_performance": "good",  # Default
                        "preferences": [],  # Unknown
                        "contributions": contributor.contributions
                    })
                    
                    count += 1
                    if count >= max_contributors:
                        break
                        
                except Exception as e:
                    print(f"  Warning: Could not fetch details for {contributor.login}: {e}")
                    continue
            
            print(f"✓ Fetched {len(developers)} contributors")
            return developers
            
        except RateLimitExceededException:
            raise ValueError("GitHub API rate limit exceeded. Please provide a GitHub token or wait before retrying.")
    
    def check_repo_has_issues(self, repo_url: str) -> bool:
        """
        Check if a repository has any open issues.
        
        Args:
            repo_url: Repository URL or 'owner/repo'
            
        Returns:
            True if repo has open issues, False otherwise
        """
        repo = self.get_repository(repo_url)
        return repo.open_issues_count > 0
    
    def _estimate_skills_from_repos(self, user: NamedUser, max_repos: int = 10) -> List[str]:
        """
        Estimate developer skills from their repositories' languages.
        
        Args:
            user: GitHub user object
            max_repos: Maximum repositories to analyze
            
        Returns:
            List of estimated skills/languages
        """
        try:
            repos = user.get_repos()
            languages = set()
            
            count = 0
            for repo in repos:
                if repo.language and count < max_repos:
                    languages.add(repo.language)
                    count += 1
            
            return list(languages)
        except:
            return []
    
    def _estimate_experience(self, user: NamedUser) -> int:
        """
        Estimate years of experience based on GitHub account age.
        
        Args:
            user: GitHub user object
            
        Returns:
            Estimated years of experience
        """
        try:
            from datetime import datetime
            account_age = datetime.now() - user.created_at
            years = account_age.days // 365
            return max(1, min(years, 15))  # Clamp between 1-15 years
        except:
            return 3  # Default
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """
        Get current GitHub API rate limit information.
        
        Returns:
            Dictionary with rate limit details
        """
        rate_limit = self.github.get_rate_limit()
        return {
            "core": {
                "limit": rate_limit.core.limit,
                "remaining": rate_limit.core.remaining,
                "reset_time": rate_limit.core.reset
            },
            "search": {
                "limit": rate_limit.search.limit,
                "remaining": rate_limit.search.remaining,
                "reset_time": rate_limit.search.reset
            }
        }
