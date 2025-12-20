# 🎯 TalentScout - AI Hiring Assistant

**An intelligent chatbot for initial candidate screening using Google Gemini 2.0 Flash**

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Features](#-features)
- [Technology Stack](#️-technology-stack)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Prompt Engineering](#-prompt-engineering)
- [Data Privacy & Security](#-data-privacy--security)
- [Challenges & Solutions](#-challenges--solutions)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Demo](#-demo)
- [License](#-license)

---

## 🎯 Project Overview

**TalentScout** is an AI-powered hiring assistant built for "TalentScout," a fictional recruitment agency specializing in technology placements. The chatbot performs initial candidate screening by:

1. **Gathering Essential Information**: Collects candidate details (name, contact, experience, etc.)
2. **Tech Stack Declaration**: Prompts candidates to specify their technical proficiencies
3. **Dynamic Question Generation**: Creates 3-5 tailored technical questions based on declared tech stack
4. **Contextual Conversations**: Maintains conversation flow with semantic search and context awareness
5. **Graceful Completion**: Ends conversations appropriately with next-step guidance

This project demonstrates advanced prompt engineering, LLM integration, and modern web development practices.

---

## ✨ Features

### Core Functionality ✅

- ✅ **Intelligent Greeting**: Warm welcome with clear purpose explanation
- ✅ **Information Gathering**: Collects 7 essential fields:
  - Full Name
  - Email Address
  - Phone Number
  - Years of Experience
  - Desired Position(s)
  - Current Location
  - Tech Stack (categorized: languages, frameworks, databases, tools)
  
- ✅ **Smart Tech Stack Processing**: Understands and categorizes various technologies
- ✅ **Dynamic Question Generation**: Creates 3-5 relevant technical questions per tech category
- ✅ **Context-Aware Conversations**: Uses ChromaDB for semantic search and conversation history
- ✅ **Fallback Mechanisms**: 
  - Retry logic for LLM failures
  - Rule-based responses for common scenarios
  - Graceful error handling
- ✅ **Conversation End Detection**: Recognizes exit keywords (goodbye, bye, exit, quit, etc.)
- ✅ **Data Privacy Compliance**: GDPR-compliant data handling

### Bonus Features ⭐

- ⭐ **Premium Streamlit UI**: Custom CSS with glassmorphism, gradients, and animations
- ⭐ **Vector Database Integration**: ChromaDB for semantic context storage and retrieval
- ⭐ **RESTful API**: FastAPI backend with full API documentation
- ⭐ **Real-time Profile Updates**: Live sidebar showing collected information
- ⭐ **Conversation Export**: Download screening summary as JSON
- ⭐ **Comprehensive Logging**: Structured logging for debugging and monitoring
- ⭐ **Docker Support**: Easy deployment with Docker Compose
- ⭐ **Automated Testing**: Test suite for all components

---

## 🛠️ Technology Stack

### Frontend
- **Streamlit 1.29.0**: Modern, responsive UI framework
- **Custom CSS**: Premium design with glassmorphism and smooth animations

### Backend
- **FastAPI 0.109.0**: High-performance async web framework
- **SQLAlchemy 2.0**: ORM for database operations
- **PostgreSQL**: Production-ready relational database

### AI & LLM
- **Google Gemini 2.0 Flash (`gemini-2.0-flash-exp`)**: Latest FREE LLM from Google
  - Why Gemini 2.0 Flash?
    - ✅ **Completely FREE** (no credit card required)
    - ✅ **Latest Model** (Released Dec 2024)
    - ✅ **Fast Response Times** (<2s average)
    - ✅ **Large Context Window** (8K tokens)
    - ✅ **Excellent Question Generation**
- **ChromaDB 0.4.22**: Vector database for semantic search and context storage

### Authentication & Security
- **JWT Tokens**: Secure session management
- **Pydantic Validation**: Input validation and sanitization
- **Environment Variables**: Secure credential management

### Data Processing
- **Pandas & NumPy**: Data manipulation
- **Email Validator**: Email format validation
- **Phone Numbers**: International phone number validation

### DevOps
- **Docker & Docker Compose**: Containerization
- **Git**: Version control
- **Pytest**: Automated testing

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     STREAMLIT UI (Frontend)                  │
│  - Chat Interface                                            │
│  - Profile Sidebar                                           │
│  - Real-time Updates                                         │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Auth API    │  │   Chat API   │  │ Candidate API│      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│  ┌──────▼──────────────────▼──────────────────▼───────┐    │
│  │              Services Layer                          │    │
│  │  - ChatService (Orchestration)                       │    │
│  │  - LLMService (Gemini Integration)                   │    │
│  │  - VectorDBService (Context Management)              │    │
│  └──────┬──────────────────┬──────────────────┬────────┘    │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
┌─────────▼─────┐  ┌────────▼────────┐  ┌──────▼──────────┐
│  PostgreSQL   │  │ Google Gemini   │  │   ChromaDB      │
│  (Candidates, │  │  2.0 Flash API  │  │ (Conversation   │
│  Conversations)│  │                 │  │  Context)       │
└───────────────┘  └─────────────────┘  └─────────────────┘
```

### Component Breakdown

1. **Frontend (Streamlit)**
   - Chat interface with message history
   - Real-time profile updates in sidebar
   - Session management
   - Export functionality

2. **API Layer (FastAPI)**
   - `/api/v1/auth/*`: Authentication endpoints
   - `/api/v1/chat/*`: Chat operations
   - `/api/v1/candidates/*`: Candidate profile management

3. **Services Layer**
   - **ChatService**: Orchestrates conversation flow, validates information
   - **LLMService**: Manages Gemini API calls with retry logic
   - **VectorDBService**: Stores and retrieves conversation context

4. **Data Layer**
   - **PostgreSQL**: Persistent storage for candidates and conversations
   - **ChromaDB**: Vector storage for semantic context search

---

## 📦 Installation

### Prerequisites

- **Python 3.9+** (Recommended: 3.10 or 3.11)
- **PostgreSQL 14+** (or use SQLite for development)
- **Git** (for cloning)
- **Google Gemini API Key** (FREE - Get from [Google AI Studio](https://aistudio.google.com/app/apikey))

### Step 1: Clone the Repository

```bash
cd C:\Users\benug\Downloads
# Already have the project in "aiml inern assignment" folder
```

### Step 2: Install Dependencies

**Option A: Using the Automated Script (Recommended for Windows)**

```powershell
# Run the automated installer
.\INSTALL.bat
```

This will:
- Check Python version
- Install all requirements
- Create `.env` file from template
- Set up the database

**Option B: Manual Installation**

```bash
# Install backend dependencies
pip install -r requirements.txt

# Install Streamlit dependencies (if not included)
pip install -r requirements-streamlit.txt
```

### Step 3: Configure Environment Variables

1. **Copy the example environment file**:
```bash
copy backend\.env.example backend\.env
```

2. **Edit `backend/.env`** and configure:

```env
# Most Important: Get your FREE Gemini API key
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Database (Use default for local SQLite, or configure PostgreSQL)
DATABASE_URL=postgresql://postgres:password@localhost:5432/talentscout

# JWT Secret (Change in production)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
```

**🔑 Getting Your FREE Gemini API Key:**
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it into `backend/.env`

### Step 4: Set Up the Database

**Option A: PostgreSQL (Production)**

```bash
# Install PostgreSQL locally or use cloud service (ElephantSQL, Neon, etc.)

# Create database
createdb talentscout

# Run migrations (auto-creates tables on first run)
python -c "from backend.app.core.database import init_db; init_db()"
```

**Option B: SQLite (Development - Easier)**

Just update `backend/.env`:
```env
DATABASE_URL=sqlite:///./talentscout.db
```

### Step 5: Test the Setup

```bash
python test_setup.py
```

This will verify:
- ✅ Python version
- ✅ All dependencies installed
- ✅ Environment variables configured
- ✅ Database connection
- ✅ Gemini API working
- ✅ ChromaDB initialized

---

## 🚀 Usage Guide

### Starting the Application

**Option 1: Automated Startup Script (Recommended)**

```powershell
# Windows PowerShell
.\START.ps1

# or Windows CMD
START.bat
```

This will:
1. Start the FastAPI backend on `http://localhost:8000`
2. Start the Streamlit UI on `http://localhost:8501`
3. Open your browser automatically

**Option 2: Manual Startup**

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
streamlit run streamlit_app.py --server.port 8501
```

### Using the Application

1. **Open the Streamlit UI**: [http://localhost:8501](http://localhost:8501)

2. **Start Chatting**: The assistant will greet you and start gathering information

3. **Provide Your Details**: Answer the questions naturally:
   - Full Name
   - Email Address
   - Phone Number
   - Years of Experience
   - Desired Position(s)
   - Current Location
   - Tech Stack

4. **Tech Stack Format**: You can list technologies in various formats:
   ```
   "Python, Django, PostgreSQL, Docker, AWS"
   or
   "Languages: Python, JavaScript
    Frameworks: Django, React
    Databases: PostgreSQL"
   ```

5. **Answer Technical Questions**: The AI will generate 3-5 questions based on your tech stack

6. **End Conversation**: Say "goodbye", "that's all", or "exit" to conclude

7. **Download Summary**: Click "Download Summary" to export your screening as JSON

### Accessing API Documentation

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📚 API Documentation

### Authentication

#### Mock Login (Development)
```http
POST /api/v1/auth/mock-login
Content-Type: application/json

{
  "email": "candidate@example.com"
}

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Chat Operations

#### Start Conversation
```http
POST /api/v1/chat/start
Authorization: Bearer {token}

Response:
{
  "conversation_id": "uuid",
  "message": "Welcome message..."
}
```

#### Send Message
```http
POST /api/v1/chat/message
Authorization: Bearer {token}
Content-Type: application/json

{
  "conversation_id": "uuid",
  "message": "I have 5 years of experience in Python"
}

Response:
{
  "response": "Great! What technologies...",
  "profile": { "years_experience": 5 },
  "conversation_ended": false
}
```

### Candidate Profile

#### Get Current Profile
```http
GET /api/v1/candidates/me
Authorization: Bearer {token}

Response:
{
  "id": "uuid",
  "full_name": "John Doe",
  "email": "john@example.com",
  "tech_stack": {...},
  "technical_questions": [...]
}
```

---

## 🎨 Prompt Engineering

### System Prompt Design

The core system prompt is located in `backend/app/prompts/system_prompts.py`:

```python
HIRING_ASSISTANT_PROMPT = """
You are TalentScout's AI Hiring Assistant...

OBJECTIVES:
1. Gather candidate information naturally
2. Generate relevant technical questions
3. Maintain conversation context
4. End conversations gracefully

CONVERSATION FLOW:
[GREETING] → [INFO GATHERING] → [TECH QUESTIONS] → [CLOSURE]
"""
```

### Key Prompt Engineering Techniques

1. **Role Definition**: Clearly defines the AI as a hiring assistant
2. **Structured Objectives**: Lists specific goals and constraints
3. **Conversation Flow Guidance**: Provides state machine logic
4. **Output Formatting**: Specifies JSON response structure
5. **Context Injection**: Includes conversation history and profile data
6. **Few-Shot Examples**: Demonstrates expected question quality

### Information Extraction Prompts

Located in `backend/app/services/chat_service.py`:

```python
# Example: Email extraction
f"Extract the email from: '{message}'. If valid, return JSON: {{'email': 'address'}}"

# Example: Tech stack parsing
f"Categorize these technologies: {tech_list}
  Return JSON with: languages, frameworks, databases, tools"
```

### Question Generation Prompts

Dynamic prompts based on tech stack:

```python
f"""Generate 3-5 technical interview questions for a {position} 
with expertise in {', '.join(technologies)}.

Focus on:
- Practical problem-solving
- Real-world scenarios
- Appropriate difficulty for {experience} years experience

Return as JSON array of strings."""
```

### Optimization Strategies

- **Temperature**: Set to 0.7 for balanced creativity and consistency
- **Max Tokens**: Limited to 8192 to stay within free tier
- **Retry Logic**: 3 attempts with exponential backoff
- **Fallback Responses**: Rule-based alternatives if LLM fails

---

## 🔒 Data Privacy & Security

### GDPR Compliance

1. **Data Minimization**: Only collect essential information
2. **Purpose Limitation**: Data used solely for screening
3. **Storage Limitation**: Configurable retention policies
4. **User Rights**: Export and deletion capabilities

### Security Measures

- ✅ **JWT Authentication**: Secure token-based sessions
- ✅ **Input Validation**: Pydantic schemas for all inputs
- ✅ **SQL Injection Protection**: SQLAlchemy ORM parameterization
- ✅ **XSS Prevention**: Streamlit auto-escapes HTML
- ✅ **Environment Variables**: Secrets stored outside codebase
- ✅ **HTTPS Ready**: Production deployment with SSL/TLS

### Data Storage

- **PostgreSQL**: Encrypted at rest (in production)
- **ChromaDB**: Local vector storage with access controls
- **Session Tokens**: Expire after 30 minutes
- **Logs**: Sanitized to remove PII

---

## 🧪 Challenges & Solutions

### Challenge 1: Context Management

**Problem**: Maintaining conversation context across multiple turns

**Solution**:
- Implemented ChromaDB for semantic search
- Store last 5 messages + full profile
- Inject relevant context into each prompt
- Use conversation state machine (STATE enum)

### Challenge 2: Flexible Tech Stack Parsing

**Problem**: Candidates provide tech stacks in various formats

**Solution**:
- Multi-format parsing (comma-separated, categorized, natural language)
- LLM-based categorization into languages/frameworks/databases/tools
- Fallback regex patterns for common formats
- Validation and confirmation with user

### Challenge 3: Question Quality

**Problem**: Generated questions sometimes too generic or off-topic

**Solution**:
- Detailed prompt engineering with examples
- Temperature tuning (0.7 for balance)
- Experience-level adaptation
- Position-specific focus
- Post-processing validation

### Challenge 4: Conversation Flow

**Problem**: Knowing when to move between stages

**Solution**:
- State machine with 5 states (GREETING, GATHERING, TECH_STACK, QUESTIONS, ENDED)
- Validation checks before state transitions
- Clear state persistence in database
- Retry logic for incomplete information

### Challenge 5: LLM Reliability

**Problem**: Occasional API failures or unexpected responses

**Solution**:
- Exponential backoff retry (3 attempts)
- Rule-based fallbacks for critical functions
- Response validation with Pydantic
- Comprehensive error logging
- User-friendly error messages

---

## ✅ Testing

### Manual Testing

```bash
# Run the test suite
python test_setup.py
```

Tests cover:
- ✅ Python version compatibility
- ✅ Dependency installation
- ✅ Environment configuration
- ✅ Database connectivity
- ✅ Gemini API functionality
- ✅ ChromaDB initialization
- ✅ Streamlit availability

### Automated Tests

```bash
# Run pytest suite
pytest backend/tests/ -v

# Run with coverage
pytest --cov=backend/app --cov-report=html
```

### Test Scenarios

1. **Happy Path**: Complete screening flow
2. **Invalid Inputs**: Email/phone validation
3. **Exit Keywords**: Conversation termination
4. **Tech Stack Variations**: Different input formats
5. **API Failures**: Retry and fallback mechanisms

---

## 🚢 Deployment

### Local Deployment (Current)

```bash
# Start both services
.\START.ps1
```

- Frontend: `http://localhost:8501`
- Backend: `http://localhost:8000`

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at:
# - Frontend: http://localhost:8501
# - Backend: http://localhost:8000
```

### Cloud Deployment (Bonus)

**Option 1: Railway.app (Recommended - Free Tier)**

1. Connect GitHub repository
2. Add environment variables
3. Deploy backend and frontend as separate services

**Option 2: Render.com**

1. Create Web Service for FastAPI
2. Create Web Service for Streamlit
3. Configure environment variables
4. Use Free PostgreSQL instance

**Option 3: Google Cloud Run**

```bash
# Deploy backend
gcloud run deploy talentscout-api \
  --source backend \
  --platform managed \
  --region us-central1

# Deploy frontend
gcloud run deploy talentscout-ui \
  --source . \
  --platform managed \
  --region us-central1
```

**Environment Variables for Production**:
- Set `ENV=production`
- Use managed PostgreSQL (Cloud SQL, ElephantSQL, Neon)
- Configure CORS origins
- Use strong JWT secrets
- Enable HTTPS

---

## 🎬 Demo

### Video Walkthrough

📹 **Demo Video**: [Link to video demonstration]

The video demonstrates:
1. Starting the application
2. Complete screening conversation
3. Profile building in real-time
4. Technical question generation
5. Conversation export

### Screenshots

*Full application interface with chat and profile sidebar*

---

## 📝 License

This project is created as an assignment submission for TalentScout recruitment.

**MIT License** - See [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Project Assignment**: AI/ML Internship - TalentScout  
**Submission Date**: December 2025  
**Implementation**: 100% Python (FastAPI + Streamlit)

---

## 📞 Support

For issues or questions:
1. Check this README thoroughly
2. Review the test output: `python test_setup.py`
3. Check API docs: `http://localhost:8000/docs`
4. Review logs in `backend/logs/`

---

## ✨ Acknowledgments

- **Google Gemini 2.0 Flash**: For providing free, powerful LLM API
- **Streamlit**: For the excellent UI framework
- **FastAPI**: For the modern web framework
- **ChromaDB**: For vector database capabilities

---

**🎯 Ready to find the perfect tech talent with AI!**