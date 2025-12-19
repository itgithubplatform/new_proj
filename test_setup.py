"""
Test Script for TalentScout AI Hiring Assistant
This script tests all components and validates the setup
"""

import os
import sys
from typing import Dict, Any

# Color codes for Windows console
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}[OK] {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}[ERROR] {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.BLUE}[INFO] {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}[WARN] {text}{Colors.END}")

def test_python_version():
    """Test Python version"""
    print_header("Testing Python Version")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} installed")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} - Need 3.9+")
        return False

def test_backend_dependencies():
    """Test backend dependencies"""
    print_header("Testing Backend Dependencies")
    
    required_modules = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('google.generativeai', 'Google Generative AI'),
        ('chromadb', 'ChromaDB'),
        ('pydantic', 'Pydantic'),
    ]
    
    all_ok = True
    for module_name, display_name in required_modules:
        try:
            __import__(module_name)
            print_success(f"{display_name} installed")
        except ImportError:
            print_error(f"{display_name} NOT installed")
            all_ok = False
    
    return all_ok

def test_environment_variables():
    """Test environment variables"""
    print_header("Testing Environment Configuration")
    
    # Try to load from backend/.env
    env_path = os.path.join('backend', '.env')
    if os.path.exists(env_path):
        print_success(f".env file found at {env_path}")
        
        # Read and check for required vars
        with open(env_path, 'r') as f:
            content = f.read()
            
        required_vars = ['GEMINI_API_KEY', 'DATABASE_URL']
        for var in required_vars:
            if var in content and 'your_' not in content.split(var)[1].split('\n')[0]:
                print_success(f"{var} is set")
            else:
                print_warning(f"{var} may not be configured properly")
        
        return True
    else:
        print_error(".env file not found")
        print_info("Copy backend/.env.example to backend/.env and configure it")
        return False

def test_database_connection():
    """Test database connection"""
    print_header("Testing Database Connection")
    
    try:
        from backend.app.core.database import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        print_success("Database connection successful")
        return True
    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        print_info("Make sure PostgreSQL is running and DATABASE_URL is correct")
        return False

def test_gemini_api():
    """Test Gemini API"""
    print_header("Testing Gemini API")
    
    try:
        import google.generativeai as genai
        from backend.app.core.config import Settings
        
        settings = Settings()
        
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "":
            print_error("GEMINI_API_KEY not configured")
            print_info("Get your free API key from: https://aistudio.google.com/app/apikey")
            return False
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        
        response = model.generate_content("Say 'Hello' in one word")
        
        if response and response.text:
            print_success(f"Gemini API working! Response: {response.text[:50]}")
            print_info(f"Using model: {settings.GEMINI_MODEL}")
            return True
        else:
            print_error("Gemini API returned empty response")
            return False
            
    except Exception as e:
        print_error(f"Gemini API test failed: {str(e)}")
        print_info("Check your API key and internet connection")
        return False

def test_vector_database():
    """Test ChromaDB"""
    print_header("Testing Vector Database (ChromaDB)")
    
    try:
        from backend.app.services.vector_db_service import vector_db_service
        
        stats = vector_db_service.get_collection_stats()
        print_success(f"ChromaDB working! Collection: {stats.get('collection_name')}")
        print_info(f"Total contexts stored: {stats.get('total_contexts', 0)}")
        return True
    except Exception as e:
        print_error(f"ChromaDB test failed: {str(e)}")
        return False

def test_streamlit():
    """Test Streamlit"""
    print_header("Testing Streamlit")
    
    try:
        import streamlit
        print_success(f"Streamlit {streamlit.__version__} installed")
        
        if os.path.exists('streamlit_app.py'):
            print_success("streamlit_app.py found")
            return True
        else:
            print_error("streamlit_app.py not found")
            return False
    except ImportError:
        print_error("Streamlit not installed")
        print_info("Install with: pip install -r requirements-streamlit.txt")
        return False

def print_summary(results: Dict[str, bool]):
    """Print test summary"""
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        if result:
            print_success(test_name)
        else:
            print_error(test_name)
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.END}\n")
    
    if passed == total:
        print_success("All tests passed! You're ready to run the application!")
        print_info("Start with: python START.bat  OR  streamlit run streamlit_app.py")
    else:
        print_warning(f"{total - passed} test(s) failed. Please fix the issues above.")

def main():
    """Run all tests"""
    print_header("TalentScout - System Test")
    print_info("Testing all components...")
    
    results = {}
    
    # Run tests
    results["Python Version"] = test_python_version()
    results["Backend Dependencies"] = test_backend_dependencies()
    results["Environment Config"] = test_environment_variables()
    
    # Only test these if basics are working
    if results["Backend Dependencies"] and results["Environment Config"]:
        results["Database Connection"] = test_database_connection()
        results["Gemini API"] = test_gemini_api()
        results["Vector Database"] = test_vector_database()
    
    results["Streamlit"] = test_streamlit()
    
    # Print summary
    print_summary(results)
    
    return all(results.values())

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)
