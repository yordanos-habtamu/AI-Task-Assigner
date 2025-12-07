"""
Database models for the AI Task Assignment System.
Uses SQLAlchemy ORM with SQLite.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class User(Base):
    """User model for authentication and preferences."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Stored API Keys (Encrypted ideally, but plain for this MVP as requested)
    openai_key = Column(String, nullable=True)
    google_key = Column(String, nullable=True)
    
    # Relationships
    assignments = relationship("Assignment", back_populates="user")


class Repository(Base):
    """GitHub repository being tracked."""
    __tablename__ = 'repositories'
    
    id = Column(Integer, primary_key=True)
    url = Column(String(500), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    owner = Column(String(200))
    has_issues = Column(Boolean, default=True)
    last_synced = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    issues = relationship("Issue", back_populates="repository", cascade="all, delete-orphan")
    developers = relationship("Developer", back_populates="repository", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Repository(name='{self.name}', url='{self.url}')>"


class Issue(Base):
    """Issue/task to be assigned."""
    __tablename__ = 'issues'
    
    id = Column(Integer, primary_key=True)
    repo_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)
    
    # GitHub fields
    github_id = Column(String(100))  # GitHub issue number or ID
    github_url = Column(String(500))
    
    # Issue details
    title = Column(String(500), nullable=False)
    description = Column(Text)
    labels = Column(JSON)  # Stored as JSON array
    estimated_hours = Column(Integer)
    
    # AI analysis results (cached)
    required_skills = Column(JSON)
    difficulty = Column(String(50))
    summary = Column(Text)
    estimated_complexity = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="issues")
    assignments = relationship("Assignment", back_populates="issue")
    
    def __repr__(self):
        return f"<Issue(id={self.id}, title='{self.title[:30]}')>"


class Developer(Base):
    """Developer who can be assigned tasks."""
    __tablename__ = 'developers'
    
    id = Column(Integer, primary_key=True)
    repo_id = Column(Integer, ForeignKey('repositories.id'), nullable=False)
    
    # GitHub fields
    github_username = Column(String(200))
    github_id = Column(String(100))
    avatar_url = Column(String(500))
    
    # Developer details
    name = Column(String(200), nullable=False)
    email = Column(String(200))
    skills = Column(JSON)  # Stored as JSON array
    experience_years = Column(Integer)
    current_workload_hours = Column(Integer, default=0)
    max_capacity_hours = Column(Integer, default=40)
    recent_performance = Column(String(50))
    preferences = Column(JSON)  # Stored as JSON array
    
    # AI analysis results (cached)
    strengths = Column(JSON)
    weaknesses = Column(JSON)
    preferred_skills = Column(JSON)
    workload_state = Column(String(50))
    availability_hours = Column(Integer)
    skill_match_score = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="developers")
    assignments = relationship("Assignment", back_populates="developer")
    
    def __repr__(self):
        return f"<Developer(id={self.id}, name='{self.name}')>"


class Assignment(Base):
    """Assignment of an issue to a developer."""
    __tablename__ = 'assignments'
    
    id = Column(Integer, primary_key=True)
    issue_id = Column(Integer, ForeignKey('issues.id'), nullable=False)
    developer_id = Column(Integer, ForeignKey('developers.id'), nullable=False)
    
    # Assignment metadata
    confidence_score = Column(Integer)
    reason = Column(Text)
    status = Column(String(50), default='pending')  # pending, accepted, in_progress, completed, rejected
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    issue = relationship("Issue", back_populates="assignments")
    developer = relationship("Developer", back_populates="assignments")
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="assignments")
    
    def __repr__(self):
        return f"<Assignment(id={self.id}, issue_id={self.issue_id}, developer_id={self.developer_id}, status='{self.status}')>"


# Database connection and session management
class Database:
    """Database connection manager."""
    
    def __init__(self, db_url: str = "sqlite:///task_assignments.db"):
        """
        Initialize database connection.
        
        Args:
            db_url: SQLAlchemy database URL
        """
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(self.engine)
    
    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal()
    
    def drop_tables(self):
        """Drop all tables (use with caution!)."""
        Base.metadata.drop_all(self.engine)


# Singleton instance
_db_instance: Optional[Database] = None


def get_database(db_url: str = "sqlite:///task_assignments.db") -> Database:
    """
    Get or create database singleton instance.
    
    Args:
        db_url: SQLAlchemy database URL
        
    Returns:
        Database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_url)
        _db_instance.create_tables()
    return _db_instance
