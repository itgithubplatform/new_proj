"""Chat service for managing conversations and message flow"""
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import Conversation, Message, Candidate, User
from app.models.conversation import MessageRole, ConversationStatus
from app.services.llm_service import llm_service
from app.services.vector_db_service import vector_db_service
from datetime import datetime
import json


class ChatService:
    """Service for managing chat conversations"""
    
    CONVERSATION_STATES = {
        "GREETING": 0,
        "COLLECT_NAME": 1,
        "COLLECT_EMAIL": 2,
        "COLLECT_PHONE": 3,
        "COLLECT_EXPERIENCE": 4,
        "COLLECT_POSITION": 5,
        "COLLECT_LOCATION": 6,
        "COLLECT_TECH_STACK": 7,
        "GENERATE_QUESTIONS": 8,
        "ASK_QUESTIONS": 9,
        "COMPLETED": 10
    }
    
    def __init__(self, db: Session):
        """Initialize chat service
        
        Args:
            db: Database session
        """
        self.db = db
    
    def start_conversation(self, user_id: str) -> Tuple[Conversation, str]:
        """Start a new conversation
        
        Args:
            user_id: User ID
            
        Returns:
            Tuple of (conversation object, greeting message)
        """
        # Create new conversation
        conversation = Conversation(
            user_id=user_id,
            title="Candidate Screening",
            status=ConversationStatus.ACTIVE
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        # Generate greeting
        greeting = llm_service.generate_greeting()
        
        # Store greeting message
        self._add_message(conversation.id, MessageRole.ASSISTANT, greeting)
        
        return conversation, greeting
    
    def process_message(
        self,
        conversation_id: str,
        user_message: str,
        user_id: str
    ) -> str:
        """Process user message and generate response
        
        Args:
            conversation_id: Conversation ID
            user_message: User's message
            user_id: User ID
            
        Returns:
            Assistant's response
        """
        # Get conversation
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
        
        if not conversation:
            return "Conversation not found. Please start a new conversation."
        
        # Store user message
        self._add_message(conversation_id, MessageRole.USER, user_message)
        
        # Check if user wants to end conversation
        if llm_service.detect_conversation_end(user_message):
            return self._end_conversation(conversation)
        
        # Get candidate data
        candidate = self.db.query(Candidate).filter(
            Candidate.user_id == user_id
        ).first()
        
        if not candidate:
            candidate = Candidate(user_id=user_id)
            self.db.add(candidate)
            self.db.commit()
            self.db.refresh(candidate)
        
        # Get conversation history
        history = self._get_conversation_history(conversation_id)
        
        # Determine current state and update candidate data
        response = self._process_conversation_flow(
            candidate,
            user_message,
            history
        )
        
        # Store assistant response
        self._add_message(conversation_id, MessageRole.ASSISTANT, response)
        
        # Store context in vector DB
        candidate_data = self._candidate_to_dict(candidate)
        vector_db_service.store_conversation_context(
            conversation_id,
            history + [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": response}
            ],
            candidate_data
        )
        
        return response
    
    def _process_conversation_flow(
        self,
        candidate: Candidate,
        user_message: str,
        history: List[Dict[str, str]]
    ) -> str:
        """Process conversation flow based on current state
        
        Args:
            candidate: Candidate object
            user_message: Current user message
            history: Conversation history
            
        Returns:
            Assistant response
        """
        # Determine what information we still need
        needs_name = not candidate.full_name
        needs_email = not candidate.email
        needs_phone = not candidate.phone
        needs_experience = candidate.years_experience is None
        needs_position = not candidate.desired_positions
        needs_location = not candidate.current_location
        needs_tech_stack = not candidate.tech_stack_raw
        
        # Update candidate based on conversation context
        if needs_name:
            candidate.full_name = user_message.strip()
            self.db.commit()
            return f"Nice to meet you, {candidate.full_name}! 👋\n\nWhat's your email address?"
        
        elif needs_email:
            candidate.email = user_message.strip()
            self.db.commit()
            return f"Great! What's your phone number?"
        
        elif needs_phone:
            candidate.phone = user_message.strip()
            self.db.commit()
            return f"Perfect! How many years of experience do you have in tech?"
        
        elif needs_experience:
            try:
                years = int(''.join(filter(str.isdigit, user_message)))
                candidate.years_experience = years
                self.db.commit()
                return f"{years} years - excellent! What position(s) are you interested in?"
            except:
                return "Please provide your years of experience as a number (e.g., 3, 5, 10)"
        
        elif needs_position:
            positions = [p.strip() for p in user_message.split(',')]
            candidate.desired_positions = positions
            self.db.commit()
            return f"Great choice! Where are you currently located?"
        
        elif needs_location:
            candidate.current_location = user_message.strip()
            self.db.commit()
            return ("Excellent! Now, please tell me about your technical skills.\n\n"
                   "List your tech stack including:\n"
                   "- Programming languages\n"
                   "- Frameworks\n"
                   "- Databases\n"
                   "- Tools & technologies")
        
        elif needs_tech_stack:
            # Parse tech stack
            candidate.tech_stack_raw = user_message
            tech_stack = llm_service.parse_tech_stack(user_message)
            candidate.tech_stack = tech_stack
            
            # Generate technical questions
            questions = llm_service.generate_technical_questions(
                tech_stack,
                candidate.years_experience or 1,
                candidate.desired_positions[0] if candidate.desired_positions else "Developer",
                num_questions=5
            )
            candidate.technical_questions = questions
            candidate.screening_status = "questions_generated"
            self.db.commit()
            
            # Format questions response
            response = ("Perfect! I've analyzed your tech stack. ✅\n\n"
                       "Based on your skills, here are some technical questions:\n\n")
            
            for i, q in enumerate(questions, 1):
                response += f"{i}. **{q['technology']}**: {q['question']}\n\n"
            
            response += "\nFeel free to answer these questions, or let me know if you have any concerns!"
            return response
        
        else:
            # All info collected, handle Q&A or generate response
            candidate_data = self._candidate_to_dict(candidate)
            response = llm_service.generate_response(
                user_message,
                history,
                candidate_data
            )
            return response
    
    def _end_conversation(self, conversation: Conversation) -> str:
        """End the conversation
        
        Args:
            conversation: Conversation object
            
        Returns:
            Closing message
        """
        conversation.status = ConversationStatus.COMPLETED
        conversation.ended_at = datetime.utcnow()
        self.db.commit()
        
        return llm_service.generate_closing_message()
    
    def _add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str
    ) -> Message:
        """Add a message to the conversation
        
        Args:
            conversation_id: Conversation ID
            role: Message role
            content: Message content
            
        Returns:
            Created message object
        """
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.db.add(message)
        
        # Update conversation message count
        conversation = self.db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()
        if conversation:
            conversation.message_count += 1
        
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def _get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 20
    ) -> List[Dict[str, str]]:
        """Get conversation history
        
        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages
            
        Returns:
            List of messages as dictionaries
        """
        messages = self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(limit).all()
        
        messages.reverse()  # Chronological order
        
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]
    
    def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Conversation]:
        """Get conversation by ID
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID for authorization
            
        Returns:
            Conversation object or None
        """
        return self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()
    
    def get_user_conversations(self, user_id: str) -> List[Conversation]:
        """Get all conversations for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of conversations
        """
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.started_at.desc()).all()
    
    def _candidate_to_dict(self, candidate: Candidate) -> Dict[str, Any]:
        """Convert candidate to dictionary
        
        Args:
            candidate: Candidate object
            
        Returns:
            Candidate data dictionary
        """
        return {
            "full_name": candidate.full_name,
            "email": candidate.email,
            "phone": candidate.phone,
            "years_experience": candidate.years_experience,
            "desired_positions": candidate.desired_positions,
            "current_location": candidate.current_location,
            "tech_stack": candidate.tech_stack,
            "technical_questions": candidate.technical_questions
        }
