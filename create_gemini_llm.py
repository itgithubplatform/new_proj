"""Script to create the complete Gemini LLM service"""

llm_service_code = '''"""LLM Service for interacting with Google Gemini and managing prompts"""
from typing import List, Dict, Any, Optional
import google.generativeai as genai
import json
import re
from app.core.config import settings
from app.prompts.templates import (
    SYSTEM_PROMPT,
    GREETING_PROMPT,
    TECH_STACK_PARSER_PROMPT,
    QUESTION_GENERATION_PROMPT,
    VALIDATION_PROMPT,
    FALLBACK_RESPONSE_PROMPT,
    CLOSING_PROMPT
)


class LLMService:
    """Service for interacting with Google Gemini Language Model"""
    
    def __init__(self):
        """Initialize Google Gemini client"""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.temperature = settings.GEMINI_TEMPERATURE
        self.max_tokens = settings.GEMINI_MAX_TOKENS
    
    def _call_llm(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_instruction: Optional[str] = None
    ) -> str:
        """Call Google Gemini API"""
        try:
            generation_config = {
                "temperature": temperature or self.temperature,
                "max_output_tokens": max_tokens or self.max_tokens,
            }
            
            if system_instruction:
                model = genai.GenerativeModel(
                    settings.GEMINI_MODEL,
                    system_instruction=system_instruction
                )
            else:
                model = self.model
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {str(e)}")
            return ""
    
    def generate_greeting(self) -> str:
        """Generate initial greeting"""
        return self._call_llm(GREETING_PROMPT, temperature=0.8, system_instruction=SYSTEM_PROMPT)
    
    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        candidate_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate chatbot response"""
        context = ""
        for msg in conversation_history[-10:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg["content"]}\\n"
        
        if candidate_data:
            context += f"\\n\\nCandidate Info:\\n{json.dumps(candidate_data, indent=2)}\\n"
        
        full_prompt = f"""Conversation History:
{context}

User: {user_message}

Please respond as the TalentScout assistant. Remember to ask only ONE question at a time and be professional yet friendly."""
        
        return self._call_llm(full_prompt, system_instruction=SYSTEM_PROMPT)
    
    def parse_tech_stack(self, tech_stack_raw: str) -> Dict[str, List[str]]:
        """Parse tech stack into structured format"""
        prompt = TECH_STACK_PARSER_PROMPT.format(tech_stack_raw=tech_stack_raw)
        response = self._call_llm(prompt, temperature=0.3)
        
        try:
            json_match = re.search(r"\\{.*\\}", response, re.DOTALL)
            if json_match:
                tech_stack = json.loads(json_match.group())
                return tech_stack
            else:
                return self._fallback_tech_stack_parse(tech_stack_raw)
        except json.JSONDecodeError:
            return self._fallback_tech_stack_parse(tech_stack_raw)
    
    def _fallback_tech_stack_parse(self, tech_stack_raw: str) -> Dict[str, List[str]]:
        """Fallback tech stack parsing"""
        text_lower = tech_stack_raw.lower()
        
        common_languages = ["python", "javascript", "java", "c++", "c#", "go", "rust", "typescript", "php", "ruby", "swift", "kotlin"]
        common_frameworks = ["django", "flask", "fastapi", "react", "vue", "angular", "next.js", "express", "spring", "laravel", ".net"]
        common_databases = ["postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sqlite", "cassandra", "dynamodb"]
        common_tools = ["docker", "kubernetes", "git", "aws", "gcp", "azure", "jenkins", "terraform", "ansible"]
        
        return {
            "languages": [lang for lang in common_languages if lang in text_lower],
            "frameworks": [fw for fw in common_frameworks if fw in text_lower],
            "databases": [db for db in common_databases if db in text_lower],
            "tools": [tool for tool in common_tools if tool in text_lower]
        }
    
    def generate_technical_questions(
        self,
        tech_stack: Dict[str, List[str]],
        years_exp: int,
        position: str,
        num_questions: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate technical questions"""
        tech_stack_str = json.dumps(tech_stack, indent=2)
        prompt = QUESTION_GENERATION_PROMPT.format(
            tech_stack=tech_stack_str,
            years_exp=years_exp,
            position=position,
            num_questions=num_questions
        )
        
        response = self._call_llm(prompt, temperature=0.7, max_tokens=2048)
        
        try:
            json_match = re.search(r"\\[.*\\]", response, re.DOTALL)
            if json_match:
                questions = json.loads(json_match.group())
                return questions[:num_questions]
            else:
                return self._generate_fallback_questions(tech_stack, num_questions)
        except json.JSONDecodeError:
            return self._generate_fallback_questions(tech_stack, num_questions)
    
    def _generate_fallback_questions(
        self,
        tech_stack: Dict[str, List[str]],
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """Generate simple fallback questions"""
        questions = []
        
        for lang in tech_stack.get("languages", [])[:2]:
            questions.append({
                "technology": lang,
                "question": f"Explain your experience with {lang} and a challenging problem you solved.",
                "difficulty": "medium"
            })
        
        for framework in tech_stack.get("frameworks", [])[:2]:
            questions.append({
                "technology": framework,
                "question": f"What are the key features of {framework} and why did you choose it?",
                "difficulty": "medium"
            })
        
        for db in tech_stack.get("databases", [])[:1]:
            questions.append({
                "technology": db,
                "question": f"How do you optimize queries in {db} for large-scale applications?",
                "difficulty": "medium"
            })
        
        return questions[:num_questions]
    
    def validate_field(self, field_type: str, value: str) -> Dict[str, Any]:
        """Validate a field"""
        prompt = VALIDATION_PROMPT.format(field_type=field_type, value=value)
        response = self._call_llm(prompt, temperature=0.1)
        
        try:
            json_match = re.search(r"\\{.*\\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        return {"is_valid": True, "corrected_value": value, "message": ""}
    
    def generate_fallback_response(self, user_input: str) -> str:
        """Generate fallback response"""
        prompt = FALLBACK_RESPONSE_PROMPT.format(user_input=user_input)
        return self._call_llm(prompt, system_instruction=SYSTEM_PROMPT)
    
    def generate_closing_message(self) -> str:
        """Generate closing message"""
        return self._call_llm(CLOSING_PROMPT, temperature=0.8, system_instruction=SYSTEM_PROMPT)
    
    def detect_conversation_end(self, user_message: str) -> bool:
        """Detect if user wants to end"""
        end_keywords = [
            "bye", "goodbye", "exit", "quit", "stop", "end", "thanks bye",
            "thank you bye", "that\\'s all", "thats all", "no thanks", "done"
        ]
        message_lower = user_message.lower().strip()
        return any(keyword in message_lower for keyword in end_keywords)


# Global LLM service instance
llm_service = LLMService()
'''

# Write to file
with open("backend/app/services/llm_service.py", "w") as f:
    f.write(llm_service_code)

print("[SUCCESS] LLM service file created successfully with Google Gemini!")
