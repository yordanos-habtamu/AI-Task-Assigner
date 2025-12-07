"""
CRUD operations for database entities.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import Repository, Issue, Developer, Assignment, User


class RepositoryService:
    """CRUD operations for repositories."""
    
    @staticmethod
    def create(session: Session, url: str, name: str, owner: str = None, has_issues: bool = True) -> Repository:
        """Create a new repository."""
        repo = Repository(
            url=url,
            name=name,
            owner=owner,
            has_issues=has_issues
        )
        session.add(repo)
        session.commit()
        session.refresh(repo)
        return repo
    
    @staticmethod
    def get_by_url(session: Session, url: str) -> Optional[Repository]:
        """Get repository by URL."""
        return session.query(Repository).filter_by(url=url).first()
    
    @staticmethod
    def get_all(session: Session) -> List[Repository]:
        """Get all repositories."""
        return session.query(Repository).all()
    
    @staticmethod
    def update_sync_time(session: Session, repo_id: int):
        """Update last sync time."""
        repo = session.query(Repository).filter_by(id=repo_id).first()
        if repo:
            repo.last_synced = datetime.utcnow()
            session.commit()


class IssueService:
    """CRUD operations for issues."""
    
    @staticmethod
    def create(session: Session, repo_id: int, title: str, description: str = None,
               labels: List[str] = None, estimated_hours: int = None,
               github_id: str = None, github_url: str = None) -> Issue:
        """Create a new issue."""
        issue = Issue(
            repo_id=repo_id,
            title=title,
            description=description,
            labels=labels or [],
            estimated_hours=estimated_hours,
            github_id=github_id,
            github_url=github_url
        )
        session.add(issue)
        session.commit()
        session.refresh(issue)
        return issue
    
    @staticmethod
    def get_by_id(session: Session, issue_id: int) -> Optional[Issue]:
        """Get issue by ID."""
        return session.query(Issue).filter_by(id=issue_id).first()
    
    @staticmethod
    def get_by_repo(session: Session, repo_id: int) -> List[Issue]:
        """Get all issues for a repository."""
        return session.query(Issue).filter_by(repo_id=repo_id).all()
    
    @staticmethod
    def get_unassigned(session: Session, repo_id: int) -> List[Issue]:
        """Get unassigned issues for a repository."""
        return session.query(Issue).filter_by(repo_id=repo_id)\
            .filter(~Issue.assignments.any(Assignment.status.in_(['accepted', 'in_progress', 'completed'])))\
            .all()
    
    @staticmethod
    def update_analysis(session: Session, issue_id: int, analysis: Dict[str, Any]):
        """Store AI analysis results."""
        issue = session.query(Issue).filter_by(id=issue_id).first()
        if issue:
            issue.required_skills = analysis.get('required_skills', [])
            issue.difficulty = analysis.get('difficulty')
            issue.summary = analysis.get('summary')
            issue.estimated_complexity = analysis.get('estimated_complexity')
            issue.updated_at = datetime.utcnow()
            session.commit()


class DeveloperService:
    """CRUD operations for developers."""
    
    @staticmethod
    def create(session: Session, repo_id: int, name: str, skills: List[str] = None,
               experience_years: int = 0, github_username: str = None,
               current_workload_hours: int = 0, max_capacity_hours: int = 40,
               recent_performance: str = 'good', preferences: List[str] = None) -> Developer:
        """Create a new developer."""
        developer = Developer(
            repo_id=repo_id,
            name=name,
            skills=skills or [],
            experience_years=experience_years,
            github_username=github_username,
            current_workload_hours=current_workload_hours,
            max_capacity_hours=max_capacity_hours,
            recent_performance=recent_performance,
            preferences=preferences or []
        )
        session.add(developer)
        session.commit()
        session.refresh(developer)
        return developer
    
    @staticmethod
    def get_by_id(session: Session, developer_id: int) -> Optional[Developer]:
        """Get developer by ID."""
        return session.query(Developer).filter_by(id=developer_id).first()
    
    @staticmethod
    def get_by_repo(session: Session, repo_id: int) -> List[Developer]:
        """Get all developers for a repository."""
        return session.query(Developer).filter_by(repo_id=repo_id).all()
    
    @staticmethod
    def get_by_github_username(session: Session, username: str) -> Optional[Developer]:
        """Get developer by GitHub username."""
        return session.query(Developer).filter_by(github_username=username).first()
    
    @staticmethod
    def update_analysis(session: Session, developer_id: int, analysis: Dict[str, Any]):
        """Store AI analysis results."""
        developer = session.query(Developer).filter_by(id=developer_id).first()
        if developer:
            developer.strengths = analysis.get('strengths', [])
            developer.weaknesses = analysis.get('weaknesses', [])
            developer.preferred_skills = analysis.get('preferred_skills', [])
            developer.workload_state = analysis.get('workload_state')
            developer.availability_hours = analysis.get('availability_hours')
            developer.skill_match_score = analysis.get('skill_match_score')
            developer.updated_at = datetime.utcnow()
            session.commit()


class AssignmentService:
    """CRUD operations for assignments."""
    
    @staticmethod
    def create(session: Session, issue_id: int, developer_id: int,
               confidence_score: int, reason: str, status: str = 'pending') -> Assignment:
        """Create a new assignment."""
        assignment = Assignment(
            issue_id=issue_id,
            developer_id=developer_id,
            confidence_score=confidence_score,
            reason=reason,
            status=status
        )
        session.add(assignment)
        session.commit()
        session.refresh(assignment)
        return assignment
    
    @staticmethod
    def get_by_id(session: Session, assignment_id: int) -> Optional[Assignment]:
        """Get assignment by ID."""
        return session.query(Assignment).filter_by(id=assignment_id).first()
    
    @staticmethod
    def get_by_repo(session: Session, repo_id: int) -> List[Assignment]:
        """Get all assignments for a repository."""
        return session.query(Assignment)\
            .join(Issue)\
            .filter(Issue.repo_id == repo_id)\
            .all()
    
    @staticmethod
    def get_history(session: Session, repo_id: int = None, limit: int = 100) -> List[Assignment]:
        """Get assignment history."""
        query = session.query(Assignment).order_by(Assignment.created_at.desc())
        
        if repo_id:
            query = query.join(Issue).filter(Issue.repo_id == repo_id)
        
        return query.limit(limit).all()
    
    @staticmethod
    def update_status(session: Session, assignment_id: int, status: str):
        """Update assignment status."""
        assignment = session.query(Assignment).filter_by(id=assignment_id).first()
        if assignment:
            assignment.status = status
            if status == 'completed':
                assignment.completed_at = datetime.utcnow()
            session.commit()


class AuthService:
    """Service for user authentication and management."""
    
    def __init__(self, db: Session):
        self.db = db
        
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
        
    def create_user(self, username: str, password_hash: str) -> User:
        db_user = User(username=username, password_hash=password_hash)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
        
    def update_api_keys(self, user_id: int, openai_key: str = None, google_key: str = None):
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            if openai_key is not None:
                user.openai_key = openai_key
            if google_key is not None:
                user.google_key = google_key
            self.db.commit()
            self.db.refresh(user)
        return user
        
    def get_user_keys(self, user_id: int) -> Dict[str, str]:
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            return {
                "openai": user.openai_key,
                "gemini": user.google_key
            }
        return {}
