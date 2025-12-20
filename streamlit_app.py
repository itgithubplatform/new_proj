"""
🎯 TalentScout - AI Hiring Assistant (Standalone Streamlit Cloud Version)

This version runs entirely on Streamlit Cloud without FastAPI backend.
All LLM calls are made directly from Streamlit.
"""

import streamlit as st
import os
from typing import Dict, List, Optional
from datetime import datetime
import json
import re

# Configure page
st.set_page_config(
    page_title="TalentScout - AI Hiring Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import Google Gemini
try:
    import google.generativeai as genai
except ImportError:
    st.error("⚠️ Google Generative AI not installed. Run: pip install google-generativeai")
    st.stop()

# Configure Gemini API
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
if not GEMINI_API_KEY:
    st.error("⚠️ GEMINI_API_KEY not found! Add it to Streamlit Secrets.")
    st.info("Go to: https://share.streamlit.io → Your app → Settings → Secrets")
    st.code('GEMINI_API_KEY = "your-api-key-here"', language="toml")
    st.stop()

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Custom CSS (same as original)
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --success-color: #10b981;
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
    
    /* Tech badges */
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
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'profile' not in st.session_state:
    st.session_state.profile = {}
if 'stage' not in st.session_state:
    st.session_state.stage = 'greeting'
if 'conversation_ended' not in st.session_state:
    st.session_state.conversation_ended = False

# Helper functions
def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone format"""
    # Remove common separators
    phone_clean = re.sub(r'[\s\-\(\)]', '', phone)
    # Check if it's 10-15 digits
    return bool(re.match(r'^\+?\d{10,15}$', phone_clean))

def extract_info_from_message(message: str, field: str) -> Optional[str]:
    """Extract specific information from message"""
    message_lower = message.lower().strip()
    
    if field == 'name':
        # Check if it looks like a name (2+ words, no numbers)
        words = message.split()
        if len(words) >= 2 and not any(char.isdigit() for char in message):
            return message.strip()
    
    elif field == 'email':
        # Extract email using regex
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', message)
        if email_match:
            return email_match.group(0)
    
    elif field == 'phone':
        # Extract phone number
        phone_match = re.search(r'[\+\d][\d\s\-\(\)]{9,}', message)
        if phone_match:
            return phone_match.group(0).strip()
    
    elif field == 'experience':
        # Extract years of experience
        years_match = re.search(r'(\d+)\s*(?:years?|yrs?)', message_lower)
        if years_match:
            return int(years_match.group(1))
        # Check if it's just a number
        if message.strip().isdigit():
            return int(message.strip())
    
    elif field == 'position':
        return message.strip()
    
    elif field == 'location':
        return message.strip()
    
    return None

def generate_tech_questions(tech_stack: Dict, position: str, experience: int) -> List[str]:
    """Generate technical questions using Gemini"""
    try:
        # Prepare tech list
        all_techs = []
        for category, techs in tech_stack.items():
            if techs:
                all_techs.extend(techs if isinstance(techs, list) else [techs])
        
        tech_str = ", ".join(all_techs[:10])  # Limit to avoid token issues
        
        prompt = f"""Generate exactly 5 technical interview questions for a {position} position 
with {experience} years of experience in: {tech_str}.

Requirements:
- Questions should assess practical problem-solving
- Mix of conceptual and hands-on scenarios
- Appropriate difficulty for {experience} years experience
- Relevant to real-world applications

Return ONLY a JSON array of 5 question strings, nothing else.
Example format: ["Question 1?", "Question 2?", ...]"""
        
        response = model.generate_content(prompt)
        
        # Parse JSON response
        text = response.text.strip()
        # Remove markdown code blocks if present
        text = re.sub(r'```json\s*|\s*```', '', text)
        questions = json.loads(text)
        
        return questions if isinstance(questions, list) else []
    
    except Exception as e:
        st.error(f"Error generating questions: {str(e)}")
        # Fallback questions
        return [
            f"Explain your experience with {all_techs[0] if all_techs else 'your main technology'}.",
            f"Describe a challenging project you've worked on as a {position}.",
            f"How do you approach debugging complex issues?",
            f"What best practices do you follow in your development workflow?",
            f"How do you stay updated with the latest technologies?"
        ]

def get_ai_response(user_message: str, stage: str, profile: Dict) -> str:
    """Get AI response based on conversation stage"""
    try:
        context = f"Current profile: {json.dumps(profile)}\nConversation stage: {stage}"
        
        system_prompt = """You are TalentScout's AI Hiring Assistant. Be friendly, professional, and concise.
        
Your goal: Gather candidate information in this order:
1. Full Name
2. Email
3. Phone
4. Years of Experience
5. Desired Position
6. Location
7. Tech Stack

After gathering all info, generate 5 technical questions.

Keep responses SHORT (1-2 sentences). Be conversational."""

        prompt = f"""{system_prompt}

{context}

User said: "{user_message}"

Respond appropriately based on the stage and information gathered."""
        
        response = model.generate_content(prompt)
        return response.text.strip()
    
    except Exception as e:
        return f"I apologize, I'm having trouble processing that. Could you please rephrase? (Error: {str(e)})"

def render_header():
    """Render header"""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 TalentScout</h1>
        <p>AI-Powered Hiring Assistant | Let's find your perfect role!</p>
    </div>
    """, unsafe_allow_html=True)

def render_chat_message(role: str, content: str):
    """Render chat message"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong><br>{content}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 Assistant:</strong><br>{content}
        </div>
        """, unsafe_allow_html=True)

def render_sidebar():
    """Render profile sidebar"""
    with st.sidebar:
        st.markdown("### 👤 Your Profile")
        
        profile = st.session_state.profile
        
        if profile:
            for key, value in profile.items():
                if value:
                    label = key.replace('_', ' ').title()
                    
                    if key == 'tech_stack' and isinstance(value, dict):
                        st.markdown(f"**{label}:**")
                        for cat, techs in value.items():
                            if techs:
                                st.markdown(f"*{cat.title()}:* {', '.join(techs) if isinstance(techs, list) else techs}")
                    elif key == 'technical_questions' and isinstance(value, list):
                        st.markdown(f"**{label}:**")
                        for i, q in enumerate(value, 1):
                            st.markdown(f"{i}. {q}")
                    else:
                        st.markdown(f"**{label}:** {value}")
        else:
            st.info("Your profile will appear here as we chat.")
        
        st.markdown("---")
        if st.button("🔄 Start New Session"):
            st.session_state.clear()
            st.rerun()

# Main app
def main():
    render_header()
    render_sidebar()
    
    # Initialize conversation
    if not st.session_state.messages:
        welcome = """Hello! 👋 Welcome to TalentScout. I'm your AI hiring assistant.

I'll ask you a few questions to understand your background and technical skills. Then I'll generate some relevant technical questions for you.

Let's get started! What's your full name?"""
        st.session_state.messages.append({"role": "assistant", "content": welcome})
    
    # Display messages
    st.markdown("### 💬 Conversation")
    for msg in st.session_state.messages:
        render_chat_message(msg["role"], msg["content"])
    
    # Chat input
    if not st.session_state.conversation_ended:
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            # Check for exit keywords
            if user_input.lower().strip() in ['bye', 'goodbye', 'exit', 'quit', 'thanks', 'thank you', "that's all"]:
                st.session_state.messages.append({"role": "user", "content": user_input})
                farewell = """Thank you for your time! 🎉

Our team will review your profile and responses. You'll hear from us within 2-3 business days.

Good luck! 🚀"""
                st.session_state.messages.append({"role": "assistant", "content": farewell})
                st.session_state.conversation_ended = True
                st.balloons()
                st.rerun()
            
            # Add user message
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Process based on stage
            profile = st.session_state.profile
            response = ""
            
            if 'full_name' not in profile:
                name = extract_info_from_message(user_input, 'name')
                if name:
                    profile['full_name'] = name
                    response = f"Nice to meet you, {name}! What's your email address?"
                else:
                    response = "I didn't catch your full name. Could you please provide your first and last name?"
            
            elif 'email' not in profile:
                email = extract_info_from_message(user_input, 'email')
                if email and validate_email(email):
                    profile['email'] = email
                    response = "Great! What's your phone number?"
                else:
                    response = "That doesn't look like a valid email. Please provide a valid email address."
            
            elif 'phone' not in profile:
                phone = extract_info_from_message(user_input, 'phone')
                if phone and validate_phone(phone):
                    profile['phone'] = phone
                    response = "Perfect! How many years of professional experience do you have?"
                else:
                    response = "Please provide a valid phone number (e.g., +1234567890 or 1234567890)."
            
            elif 'years_experience' not in profile:
                exp = extract_info_from_message(user_input, 'experience')
                if exp is not None:
                    profile['years_experience'] = exp
                    response = f"{exp} years - excellent! What position are you interested in?"
                else:
                    response = "Please provide the number of years of experience (e.g., 5 or 5 years)."
            
            elif 'desired_position' not in profile:
                position = extract_info_from_message(user_input, 'position')
                if position:
                    profile['desired_position'] = position
                    response = f"{position} - great choice! Where are you currently located?"
                else:
                    response = "What position are you looking for? (e.g., Full Stack Developer, Data Scientist)"
            
            elif 'location' not in profile:
                location = extract_info_from_message(user_input, 'location')
                if location:
                    profile['location'] = location
                    response = """Perfect! Now, please tell me about your tech stack.

List the technologies, programming languages, frameworks, databases, and tools you're proficient in.

For example: "Python, Django, PostgreSQL, Docker, AWS" """
                else:
                    response = "Where are you located? (City, Country)"
            
            elif 'tech_stack' not in profile:
                # Parse tech stack
                tech_list = [t.strip() for t in re.split(r'[,;]', user_input) if t.strip()]
                if tech_list:
                    profile['tech_stack'] = {'technologies': tech_list}
                    
                    # Generate questions
                    with st.spinner("Generating technical questions..."):
                        questions = generate_tech_questions(
                            profile['tech_stack'],
                            profile.get('desired_position', 'Software Engineer'),
                            profile.get('years_experience', 3)
                        )
                        profile['technical_questions'] = questions
                    
                    response = f"""Excellent! I've noted your tech stack: {', '.join(tech_list[:5])}

Based on your experience and skills, here are some technical questions:

"""
                    for i, q in enumerate(questions, 1):
                        response += f"{i}. {q}\n\n"
                    
                    response += "\nFeel free to answer these now, or type 'goodbye' when you're ready to finish."
                else:
                    response = "Please list your technologies separated by commas."
            
            else:
                # General conversation
                response = get_ai_response(user_input, st.session_state.stage, profile)
            
            # Update profile
            st.session_state.profile = profile
            
            # Add response
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    else:
        st.success("✅ Screening completed!")
        
        if st.button("📥 Download Summary"):
            summary = {
                "profile": st.session_state.profile,
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
