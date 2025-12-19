"""
🎯 TalentScout - AI Hiring Assistant (Streamlit UI)

This is the main Streamlit application for the TalentScout Hiring Assistant.
It provides an intuitive chat interface for candidate screening and technical assessment.
"""

import streamlit as st
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_V1_PREFIX = "/api/v1"

# Page configuration
st.set_page_config(
    page_title="TalentScout - AI Hiring Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium UI
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.3s ease-in;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .assistant-message {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-right: 20%;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .system-message {
        background: linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);
        color: white;
        text-align: center;
        font-style: italic;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
    }
    
    /* Profile card */
    .profile-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    
    .profile-field {
        margin-bottom: 0.75rem;
        padding: 0.5rem;
        border-left: 3px solid #667eea;
        background: rgba(102, 126, 234, 0.1);
        border-radius: 0.25rem;
    }
    
    .profile-label {
        font-weight: 600;
        color: #667eea;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .profile-value {
        font-size: 1.1rem;
        margin-top: 0.25rem;
    }
    
    /* Tech stack badges */
    .tech-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 1rem;
        margin: 0.25rem;
        font-size: 0.85rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* Question card */
    .question-card {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        padding: 1rem;
        margin: 0.75rem 0;
        border-radius: 0.5rem;
    }
    
    .question-number {
        font-weight: 700;
        color: #10b981;
        font-size: 1.1rem;
    }
    
    /* Status indicators */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 1rem;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.25rem;
    }
    
    .status-gathering {
        background: #fef3c7;
        color: #92400e;
    }
    
    .status-complete {
        background: #d1fae5;
        color: #065f46;
    }
    
    .status-active {
        background: #dbeafe;
        color: #1e40af;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'candidate_profile' not in st.session_state:
    st.session_state.candidate_profile = {}
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
if 'conversation_ended' not in st.session_state:
    st.session_state.conversation_ended = False


class APIClient:
    """API client for TalentScout backend"""
    
    @staticmethod
    def mock_login() -> Optional[str]:
        """Perform mock login to get auth token"""
        try:
            response = requests.post(
                f"{API_BASE_URL}{API_V1_PREFIX}/auth/mock-login",
                json={"email": f"candidate_{datetime.now().timestamp()}@example.com"}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("access_token")
        except Exception as e:
            st.error(f"Authentication failed: {str(e)}")
        return None
    
    @staticmethod
    def start_conversation(token: str) -> Optional[str]:
        """Start a new conversation"""
        try:
            response = requests.post(
                f"{API_BASE_URL}{API_V1_PREFIX}/chat/start",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("conversation_id")
        except Exception as e:
            st.error(f"Failed to start conversation: {str(e)}")
        return None
    
    @staticmethod
    def send_message(token: str, conversation_id: str, message: str) -> Optional[Dict]:
        """Send a message and get response"""
        try:
            response = requests.post(
                f"{API_BASE_URL}{API_V1_PREFIX}/chat/message",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "conversation_id": conversation_id,
                    "message": message
                }
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Failed to send message: {str(e)}")
        return None
    
    @staticmethod
    def get_candidate_profile(token: str) -> Optional[Dict]:
        """Get current candidate profile"""
        try:
            response = requests.get(
                f"{API_BASE_URL}{API_V1_PREFIX}/candidates/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            st.error(f"Failed to get profile: {str(e)}")
        return None


def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 TalentScout</h1>
        <p>AI-Powered Hiring Assistant | Let's find your perfect role!</p>
    </div>
    """, unsafe_allow_html=True)


def render_chat_message(role: str, content: str):
    """Render a chat message with appropriate styling"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong><br>{content}
        </div>
        """, unsafe_allow_html=True)
    elif role == "assistant":
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 Assistant:</strong><br>{content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message system-message">
            {content}
        </div>
        """, unsafe_allow_html=True)


def render_profile_sidebar():
    """Render candidate profile in sidebar"""
    with st.sidebar:
        st.markdown("### 👤 Your Profile")
        
        if st.session_state.candidate_profile:
            profile = st.session_state.candidate_profile
            
            # Name
            if profile.get('full_name'):
                st.markdown(f"""
                <div class="profile-field">
                    <div class="profile-label">Full Name</div>
                    <div class="profile-value">{profile['full_name']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Email
            if profile.get('email'):
                st.markdown(f"""
                <div class="profile-field">
                    <div class="profile-label">Email</div>
                    <div class="profile-value">{profile['email']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Phone
            if profile.get('phone'):
                st.markdown(f"""
                <div class="profile-field">
                    <div class="profile-label">Phone</div>
                    <div class="profile-value">{profile['phone']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Experience
            if profile.get('years_experience'):
                st.markdown(f"""
                <div class="profile-field">
                    <div class="profile-label">Experience</div>
                    <div class="profile-value">{profile['years_experience']} years</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Position
            if profile.get('desired_positions'):
                positions = profile['desired_positions']
                if isinstance(positions, list):
                    positions_str = ", ".join(positions)
                else:
                    positions_str = positions
                st.markdown(f"""
                <div class="profile-field">
                    <div class="profile-label">Desired Positions</div>
                    <div class="profile-value">{positions_str}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Location
            if profile.get('location'):
                st.markdown(f"""
                <div class="profile-field">
                    <div class="profile-label">Location</div>
                    <div class="profile-value">{profile['location']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Tech Stack
            if profile.get('tech_stack'):
                st.markdown('<div class="profile-label">Tech Stack</div>', unsafe_allow_html=True)
                tech_stack = profile['tech_stack']
                
                # Parse tech stack if it's a dict
                if isinstance(tech_stack, dict):
                    for category, techs in tech_stack.items():
                        if techs:
                            st.markdown(f"**{category.title()}:**")
                            for tech in techs:
                                st.markdown(f'<span class="tech-badge">{tech}</span>', unsafe_allow_html=True)
                elif isinstance(tech_stack, list):
                    for tech in tech_stack:
                        st.markdown(f'<span class="tech-badge">{tech}</span>', unsafe_allow_html=True)
            
            # Technical Questions
            if profile.get('technical_questions'):
                st.markdown("---")
                st.markdown("### 📝 Technical Questions")
                questions = profile['technical_questions']
                if isinstance(questions, list):
                    for i, q in enumerate(questions, 1):
                        st.markdown(f"""
                        <div class="question-card">
                            <span class="question-number">{i}.</span> {q}
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("Your profile will appear here as we collect information.")
        
        # Status
        st.markdown("---")
        st.markdown("### 📊 Status")
        if st.session_state.conversation_ended:
            st.markdown('<span class="status-badge status-complete">✅ Completed</span>', unsafe_allow_html=True)
        elif st.session_state.conversation_id:
            st.markdown('<span class="status-badge status-active">💬 Active</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-badge status-gathering">🔄 Ready to Start</span>', unsafe_allow_html=True)
        
        # Actions
        st.markdown("---")
        if st.button("🔄 Start New Session"):
            st.session_state.clear()
            st.rerun()


def initialize_session():
    """Initialize a new conversation session"""
    if not st.session_state.auth_token:
        with st.spinner("Authenticating..."):
            token = APIClient.mock_login()
            if token:
                st.session_state.auth_token = token
            else:
                st.error("Failed to authenticate. Please refresh the page.")
                return False
    
    if not st.session_state.conversation_id:
        with st.spinner("Starting conversation..."):
            conv_id = APIClient.start_conversation(st.session_state.auth_token)
            if conv_id:
                st.session_state.conversation_id = conv_id
                # Add welcome message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Hello! 👋 Welcome to TalentScout. I'm your AI hiring assistant, and I'm here to help screen your profile for potential opportunities.\n\nI'll ask you a few questions to understand your background and technical skills. Once I have all the information, I'll generate some technical questions relevant to your expertise.\n\nLet's get started! What's your full name?"
                })
            else:
                st.error("Failed to start conversation. Please refresh the page.")
                return False
    
    return True


def handle_user_input(user_message: str):
    """Handle user input and get AI response"""
    # Add user message to chat
    st.session_state.messages.append({
        "role": "user",
        "content": user_message
    })
    
    # Send message to API
    with st.spinner("Thinking..."):
        response = APIClient.send_message(
            st.session_state.auth_token,
            st.session_state.conversation_id,
            user_message
        )
        
        if response:
            # Add assistant response
            st.session_state.messages.append({
                "role": "assistant",
                "content": response.get("response", "")
            })
            
            # Update profile
            if response.get("profile"):
                st.session_state.candidate_profile = response["profile"]
            
            # Check if conversation ended
            if response.get("conversation_ended"):
                st.session_state.conversation_ended = True
                st.balloons()
        else:
            st.error("Failed to get response. Please try again.")


def main():
    """Main application"""
    render_header()
    render_profile_sidebar()
    
    # Initialize session
    if not initialize_session():
        return
    
    # Main chat area
    st.markdown("### 💬 Conversation")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            render_chat_message(message["role"], message["content"])
    
    # Chat input
    if not st.session_state.conversation_ended:
        st.markdown("---")
        user_input = st.chat_input("Type your message here...", key="chat_input")
        
        if user_input:
            handle_user_input(user_input)
            st.rerun()
    else:
        st.success("✅ Screening completed! Our team will review your profile and technical responses.")
        st.info("💡 **Next Steps:** You'll receive an email within 2-3 business days with further instructions.")
        
        if st.button("📥 Download Summary"):
            # Create downloadable summary
            summary = {
                "profile": st.session_state.candidate_profile,
                "conversation": st.session_state.messages,
                "timestamp": datetime.now().isoformat()
            }
            st.download_button(
                label="Download JSON",
                data=json.dumps(summary, indent=2),
                file_name=f"talentscout_screening_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )


if __name__ == "__main__":
    main()
