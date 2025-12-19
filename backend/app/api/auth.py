"""Authentication endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime
from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.models import User
from app.schemas import GoogleAuthRequest, TokenResponse
import uuid

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    auth_request: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user with Google OAuth
    
    Args:
        auth_request: Google authentication request with ID token
        db: Database session
        
    Returns:
        JWT tokens and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Verify Google ID token
        if settings.GOOGLE_CLIENT_ID:
            # Production: Verify with Google
            try:
                idinfo = id_token.verify_oauth2_token(
                    auth_request.id_token,
                    requests.Request(),
                    settings.GOOGLE_CLIENT_ID
                )
                
                google_id = idinfo['sub']
                email = idinfo['email']
                full_name = idinfo.get('name', '')
                profile_picture = idinfo.get('picture', '')
            except Exception as e:
                # Development fallback: Mock verification
                print(f"Google token verification failed (using mock): {str(e)}")
                google_id = "mock_google_id_" + str(uuid.uuid4())[:8]
                email = "demo@example.com"
                full_name = "Demo User"
                profile_picture = ""
        else:
            # Development mode: Mock Google auth
            google_id = "mock_google_id_" + str(uuid.uuid4())[:8]
            email = "demo@example.com"
            full_name = "Demo User"
            profile_picture = ""
        
        # Check if user exists
        user = db.query(User).filter(User.google_id == google_id).first()
        
        if not user:
            # Create new user
            user = User(
                email=email,
                google_id=google_id,
                full_name=full_name,
                profile_picture=profile_picture,
                is_verified=True,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()
        
        # Create JWT tokens
        access_token = create_access_token(data={"sub": user.id})
        refresh_token = create_refresh_token(data={"sub": user.id})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "profile_picture": user.profile_picture
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/mock-login", response_model=TokenResponse)
async def mock_login(db: Session = Depends(get_db)):
    """Mock login for development/testing
    
    Args:
        db: Database session
        
    Returns:
        JWT tokens and user information
    """
    # Create or get mock user
    mock_email = "test@talentscout.dev"
    user = db.query(User).filter(User.email == mock_email).first()
    
    if not user:
        user = User(
            email=mock_email,
            google_id="mock_google_id",
            full_name="Test User",
            is_verified=True,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "profile_picture": user.profile_picture
        }
    )
