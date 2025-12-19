"""Chat endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, Conversation, Message
from app.schemas import (
    ChatMessageRequest,
    ChatMessageResponse,
    ConversationResponse,
    MessageResponse
)
from app.services.chat_service import ChatService
from datetime import datetime

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/start", response_model=ChatMessageResponse)
async def start_conversation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new conversation
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Initial greeting message
    """
    chat_service = ChatService(db)
    conversation, greeting = chat_service.start_conversation(current_user.id)
    
    # Get the first message
    first_message = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).first()
    
    return ChatMessageResponse(
        response=greeting,
        conversation_id=conversation.id,
        message_id=first_message.id,
        timestamp=datetime.utcnow()
    )


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    message_request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a chat message
    
    Args:
        message_request: Chat message request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Assistant's response
    """
    chat_service = ChatService(db)
    
    # If no conversation ID provided, start new conversation
    if not message_request.conversation_id:
        conversation, _ = chat_service.start_conversation(current_user.id)
        conversation_id = conversation.id
    else:
        conversation_id = message_request.conversation_id
    
    # Process message
    try:
        response = chat_service.process_message(
            conversation_id,
            message_request.message,
            current_user.id
        )
        
        # Get the last message
        last_message = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).first()
        
        return ChatMessageResponse(
            response=response,
            conversation_id=conversation_id,
            message_id=last_message.id,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for current user
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of conversations
    """
    chat_service = ChatService(db)
    conversations = chat_service.get_user_conversations(current_user.id)
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation
    
    Args:
        conversation_id: Conversation ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Conversation object
    """
    chat_service = ChatService(db)
    conversation = chat_service.get_conversation(conversation_id, current_user.id)
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return conversation


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages in a conversation
    
    Args:
        conversation_id: Conversation ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of messages
    """
    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()
    
    return messages
