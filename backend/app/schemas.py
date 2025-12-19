"""Pydantic schemas for API requests and responses"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# Auth Schemas
class GoogleAuthRequest(BaseModel):
    """Google OAuth authentication request"""
    id_token: str = Field(..., description="Google ID token")


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    google_id: Optional[str] = None
    profile_picture: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Chat Schemas
class ChatMessageRequest(BaseModel):
    """Chat message request"""
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    """Chat message response"""
    response: str
    conversation_id: str
    message_id: str
    timestamp: datetime


class ConversationResponse(BaseModel):
    """Conversation response"""
    id: str
    title: str
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    message_count: int
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Message response"""
    id: str
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Candidate Schemas
class CandidateResponse(BaseModel):
    """Candidate response"""
    id: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    years_experience: Optional[int] = None
    desired_positions: Optional[List[str]] = None
    current_location: Optional[str] = None
    tech_stack: Optional[Dict[str, List[str]]] = None
    technical_questions: Optional[List[Dict[str, Any]]] = None
    screening_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Health Check
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    database: str
    vector_db: str
