"""Candidate endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, Candidate
from app.schemas import CandidateResponse

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.get("/me", response_model=CandidateResponse)
async def get_my_candidate_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's candidate profile
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Candidate profile
    """
    candidate = db.query(Candidate).filter(
        Candidate.user_id == current_user.id
    ).first()
    
    if not candidate:
        # Create empty candidate profile
        candidate = Candidate(user_id=current_user.id)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
    
    return candidate


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get candidate by ID (admin only in production)
    
    Args:
        candidate_id: Candidate ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Candidate profile
    """
    candidate = db.query(Candidate).filter(
        Candidate.id == candidate_id
    ).first()
    
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Authorization check
    if candidate.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this candidate profile"
        )
    
    return candidate
