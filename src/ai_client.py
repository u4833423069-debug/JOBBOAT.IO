"""
Unified AI Client - Ollama Qwen2 for CV parsing, Anthropic Claude for consultant
Enhanced for faster, more human responses
"""

import os
import logging
from typing import Optional, Dict, Any
import ollama
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class AIClient:
    """Unified client for AI operations"""
    
    def __init__(self, ollama_model: str = None, anthropic_key: str = None):
        """Initialize AI client with Ollama and Anthropic"""
        # Ollama for CV parsing
        self.ollama_model = ollama_model or os.getenv('OLLAMA_MODEL', 'qwen2:latest')
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.ollama_client = ollama.Client(host=self.ollama_url)
        
        # Anthropic Claude for consultant
        anthropic_key = anthropic_key or os.getenv('ANTHROPIC_API_KEY')
        self.anthropic_client = Anthropic(api_key=anthropic_key) if anthropic_key else None
        
        # Store conversation history for context
        self.conversation_history = {}
        
        logger.info(f"AI Client initialized - Ollama: {self.ollama_model}, Claude: {'enabled' if self.anthropic_client else 'disabled'}")
    
    def query_ollama(self, prompt: str, system: Optional[str] = None, temperature: float = 0.7) -> str:
        """Query Ollama (for CV parsing)"""
        try:
            messages = []
            
            if system:
                messages.append({'role': 'system', 'content': system})
            
            messages.append({'role': 'user', 'content': prompt})
            
            response = self.ollama_client.chat(
                model=self.ollama_model,
                messages=messages,
                options={'temperature': temperature}
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Ollama query error: {e}")
            return f"Error: Unable to connect to Ollama. Please ensure it's running with {self.ollama_model} model."
    
    def query_claude(self, user_message: str, user_id: str = 'default', system_prompt: str = None) -> str:
        """Query Anthropic Claude (for consultant) with conversation history"""
        try:
            if not self.anthropic_client:
                # Fallback to Ollama if Claude not available
                return self.query_ollama(user_message, system_prompt, temperature=0.8)
            
            # Get or create conversation history
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # Add user message
            self.conversation_history[user_id].append({
                "role": "user",
                "content": user_message
            })
            
            # Keep last 10 messages for context
            messages = self.conversation_history[user_id][-10:]
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=system_prompt or "You are Zby, a helpful AI career consultant.",
                messages=messages
            )
            
            assistant_message = response.content[0].text
            
            # Store assistant response
            self.conversation_history[user_id].append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Claude query error: {e}")
            # Fallback to Ollama
            return self.query_ollama(user_message, system_prompt, temperature=0.8)
    
    def parse_cv_text(self, cv_text: str) -> Dict[str, Any]:
        """Parse CV using Ollama Qwen2"""
        system_prompt = """You are an expert CV parser. Extract information and return ONLY valid JSON in this exact format:
{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "phone number",
    "location": "city, country",
    "skills": ["skill1", "skill2"],
    "experience": [{"title": "Job Title", "company": "Company Name", "duration": "2020-2023"}],
    "education": [{"degree": "Degree", "institution": "School", "year": "2020"}],
    "summary": "professional summary"
}

Extract only information explicitly present. Return ONLY the JSON, no other text."""
        
        prompt = f"Parse this CV and extract information:\n\n{cv_text[:4000]}"
        
        response = self.query_ollama(prompt, system=system_prompt, temperature=0.2)
        
        # Extract JSON from response
        try:
            import json
            # Clean response
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
            elif '{' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
            else:
                json_str = response
            
            parsed = json.loads(json_str)
            
            # Ensure all fields exist
            default_data = {
                'name': 'Unknown',
                'email': '',
                'phone': '',
                'location': '',
                'skills': [],
                'experience': [],
                'education': [],
                'summary': ''
            }
            
            return {**default_data, **parsed}
            
        except Exception as e:
            logger.error(f"CV parse JSON error: {e}")
            return {
                'name': 'Parsing Error',
                'email': '',
                'phone': '',
                'location': '',
                'skills': [],
                'experience': [],
                'education': [],
                'summary': cv_text[:500],
                'error': str(e)
            }
    
    def generate_cover_letter(self, job_info: Dict[str, Any], cv_data: Dict[str, Any]) -> str:
        """Generate cover letter using Ollama"""
        system_prompt = """You are an expert cover letter writer. Create compelling, personalized cover letters that:
- Highlight relevant skills and experience
- Show genuine interest in the role
- Are professional yet personable
- Are 250-350 words
- Follow proper business letter format"""
        
        # Format experience
        exp_str = ""
        if cv_data.get('experience'):
            for exp in cv_data['experience'][:3]:
                if isinstance(exp, dict):
                    exp_str += f"{exp.get('title', '')} at {exp.get('company', '')} ({exp.get('duration', '')}); "
                else:
                    exp_str += str(exp) + "; "
        
        prompt = f"""Write a cover letter for:

Job Title: {job_info.get('title', 'Position')}
Company: {job_info.get('company', 'Company')}
Description: {job_info.get('description', '')[:500]}

Applicant:
Name: {cv_data.get('name', 'Applicant')}
Skills: {', '.join(cv_data.get('skills', [])[:10])}
Experience: {exp_str}
Education: {'; '.join([str(e) for e in cv_data.get('education', [])][:2])}

Write a professional cover letter."""
        
        return self.query_ollama(prompt, system=system_prompt, temperature=0.7)
    
    def consultant_chat(self, user_message: str, user_id: str, context: Dict[str, Any] = None) -> str:
        """Zby consultant using Claude - NO repetitive greetings"""
        system_prompt = """You are Zby, an AI career consultant for AI JobBot. You are:

- Direct and helpful - NO repetitive greetings or "I've analyzed your CV" phrases
- Professional yet warm and personable
- Knowledgeable about job search, CVs, and career growth
- Subtly persuasive about premium features when relevant
- Focused on actionable advice

IMPORTANT: Do NOT start every response with greetings or "I've analyzed..." - be conversational and get straight to the helpful advice.

Your responses should feel like talking to a smart friend, not a corporate chatbot."""
        
        # Add context if available
        context_str = user_message
        if context and any(context.values()):
            context_notes = []
            if context.get('cv_uploaded'):
                skills = context.get('skills', [])
                if skills:
                    context_notes.append(f"User has skills: {', '.join(skills[:5])}")
            if context.get('applications_count', 0) > 0:
                context_notes.append(f"Has applied to {context['applications_count']} jobs")
            
            if context_notes:
                context_str += f"\n[Context: {'; '.join(context_notes)}]"
        
        return self.query_claude(context_str, user_id=user_id, system_prompt=system_prompt)
    
    def clear_history(self, user_id: str):
        """Clear conversation history for a user"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
    
    def check_connection(self) -> Dict[str, bool]:
        """Check AI services status"""
        status = {}
        
        try:
            self.ollama_client.list()
            status['ollama'] = True
        except:
            status['ollama'] = False
        
        status['claude'] = self.anthropic_client is not None
        
        return status


# Global AI client
_ai_client = None

def get_ai_client() -> AIClient:
    """Get global AI client instance"""
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client
