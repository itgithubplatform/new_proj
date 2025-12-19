"""Candidate model for storing candidate information"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import uuid


class Candidate(Base):
    """Candidate model storing all information gathered during screening"""
    
    __tablename__ = "candidates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Basic Information
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    # Professional Information
    years_experience = Column(Integer, nullable=True)
    desired_positions = Column(JSON, nullable=True)  # List of positions
    current_location = Column(String, nullable=True)
    
    # Technical Information
    tech_stack = Column(JSON, nullable=True)  # {"languages": [], "frameworks": [], "databases": [], "tools": []}
    tech_stack_raw = Column(Text, nullable=True)  # Raw text input
    
    # Questions and Answers
    technical_questions = Column(JSON, nullable=True)  # List of generated questions
    answers = Column(JSON, nullable=True)  # Candidate's answers
    
    # Status
    screening_status = Column(String, default="in_progress")  # in_progress, completed, abandoned
    screening_completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="candidate")
    
    def __repr__(self):
        return f"<Candidate {self.full_name} - {self.email}>"
