"""
Unified Ollama AI Client - Single interface for all AI operations
Supports CV parsing, letter generation, and consultant chat
"""

import os
import logging
from typing import Optional, Dict, Any
import ollama

logger = logging.getLogger(__name__)

class AIClient:
    """Unified client for Ollama AI operations"""
    
    def __init__(self, model: str = None, base_url: str = None):
        """
        Initialize AI client
        
        Args:
            model: Ollama model name (default from env)
            base_url: Ollama server URL (default from env)
        """
        self.model = model or os.getenv('OLLAMA_MODEL', 'mistral')
        self.base_url = base_url or os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.client = ollama.Client(host=self.base_url)
        logger.info(f"AI Client initialized with model: {self.model}")
    
    def query_ai(self, prompt: str, system: Optional[str] = None, temperature: float = 0.7) -> str:
        """
        Send a query to Ollama and get response
        
        Args:
            prompt: User prompt
            system: System instruction (optional)
            temperature: Response creativity (0-1)
        
        Returns:
            AI response text
        """
        try:
            messages = []
            
            if system:
                messages.append({
                    'role': 'system',
                    'content': system
                })
            
            messages.append({
                'role': 'user',
                'content': prompt
            })
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={'temperature': temperature}
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"AI query error: {e}")
            return f"I apologize, but I'm having trouble connecting to the AI service. Please ensure Ollama is running with the {self.model} model."
    
    def parse_cv_text(self, cv_text: str) -> Dict[str, Any]:
        """
        Parse CV text and extract structured information
        
        Args:
            cv_text: Raw CV text
        
        Returns:
            Dictionary with parsed CV data
        """
        system_prompt = """You are a CV parsing assistant. Extract information from the CV text and return it in this JSON format:
{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "phone number",
    "location": "city, country",
    "skills": ["skill1", "skill2", ...],
    "experience": ["job title at company (years)", ...],
    "education": ["degree from institution", ...],
    "summary": "brief professional summary"
}

Be precise and only extract information that is explicitly present in the CV."""
        
        prompt = f"Parse this CV and extract the information:\n\n{cv_text[:3000]}"
        
        response = self.query_ai(prompt, system=system_prompt, temperature=0.3)
        
        # Try to extract JSON from response
        try:
            import json
            # Find JSON in response (handle markdown code blocks)
            if '```json' in response:
                json_str = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                json_str = response.split('```')[1].split('```')[0].strip()
            elif '{' in response:
                json_str = response[response.find('{'):response.rfind('}')+1]
            else:
                json_str = response
            
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"CV parse JSON error: {e}")
            # Return fallback structure
            return {
                'name': 'Unknown',
                'email': '',
                'phone': '',
                'location': '',
                'skills': [],
                'experience': [],
                'education': [],
                'summary': cv_text[:500],
                'raw_response': response
            }
    
    def generate_cover_letter(self, job_info: Dict[str, Any], cv_data: Dict[str, Any]) -> str:
        """
        Generate personalized cover letter
        
        Args:
            job_info: Job details (title, company, description, requirements)
            cv_data: Parsed CV data
        
        Returns:
            Cover letter text
        """
        system_prompt = """You are an expert cover letter writer. Create compelling, personalized cover letters that:
- Highlight relevant skills and experience
- Show genuine interest in the specific role
- Are professional but personable
- Are concise (250-350 words)
- Follow proper business letter format"""
        
        prompt = f"""Write a cover letter for this job application:

Job Title: {job_info.get('title', 'Position')}
Company: {job_info.get('company', 'Company')}
Job Description: {job_info.get('description', '')[:500]}

Applicant Information:
Name: {cv_data.get('name', 'Applicant')}
Skills: {', '.join(cv_data.get('skills', [])[:10])}
Experience: {'; '.join(cv_data.get('experience', [])[:3])}
Education: {'; '.join(cv_data.get('education', [])[:2])}

Write a professional cover letter that demonstrates why this candidate is a great fit."""
        
        return self.query_ai(prompt, system=system_prompt, temperature=0.7)
    
    def consultant_chat(self, user_message: str, context: Dict[str, Any] = None) -> str:
        """
        Zby consultant chat response
        
        Args:
            user_message: User's question/message
            context: User context (CV data, activity, etc.)
        
        Returns:
            Zby's response
        """
        system_prompt = """You are Zby, an AI career consultant for AIJobBot. You are:
- Helpful, insightful, and professional
- Knowledgeable about job search strategies, CV optimization, and career development
- Subtly persuasive about the value of paid features when appropriate
- Ethical and never misleading
- Supportive and encouraging

Your goal is to help users succeed in their job search while gently highlighting when premium features could accelerate their progress. Always be genuine and put the user's success first."""
        
        # Add context if available
        context_str = ""
        if context:
            if context.get('cv_uploaded'):
                context_str += f"\nUser has uploaded their CV with skills: {', '.join(context.get('skills', [])[:5])}"
            if context.get('applications_count'):
                context_str += f"\nUser has applied to {context.get('applications_count')} jobs"
            if context.get('credits_remaining'):
                context_str += f"\nUser has {context.get('credits_remaining')} credits remaining"
        
        full_prompt = user_message
        if context_str:
            full_prompt += f"\n\n[Context: {context_str}]"
        
        return self.query_ai(full_prompt, system=system_prompt, temperature=0.8)
    
    def check_connection(self) -> bool:
        """Check if Ollama is accessible"""
        try:
            self.client.list()
            return True
        except Exception as e:
            logger.warning(f"Ollama connection check failed: {e}")
            return False


# Global AI client instance
_ai_client = None

def get_ai_client() -> AIClient:
    """Get global AI client instance"""
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client
