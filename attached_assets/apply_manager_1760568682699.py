"""
Apply Manager - Coordinate auto-apply across platforms
"""

import logging
from typing import Dict, Any
from src.auto_apply.linkedin_apply import LinkedInApply
from src.auto_apply.indeed_apply import IndeedAutoApply
from src.auto_apply.glassdoor_apply import GlassdoorAutoApply

logger = logging.getLogger(__name__)

class ApplyManager:
    """Manage job application automation"""
    
    def __init__(self):
        self.platforms = {
            'linkedin': LinkedInApply,
            'indeed': IndeedAutoApply,
            'glassdoor': GlassdoorAutoApply
        }
    
    def apply_to_job(self, job_url: str, platform: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply to job on specified platform
        
        Args:
            job_url: Job posting URL
            platform: Platform name (linkedin, indeed, etc.)
            user_data: User credentials and CV data
        
        Returns:
            Status dict with application result
        """
        platform = platform.lower()
        
        if platform not in self.platforms or self.platforms[platform] is None:
            return {
                'status': 'error',
                'message': f'Auto-apply not yet supported for {platform}'
            }
        
        try:
            # Initialize platform-specific applier
            applier_class = self.platforms[platform]
            applier = applier_class(headless=False)  # Always headful for CAPTCHA
            
            # Attempt application
            result = applier.apply_to_job(job_url, user_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Apply manager error: {e}")
            return {
                'status': 'error',
                'message': f'Application failed: {str(e)}'
            }
    
    def resume_application(self, user_email: str, platform: str) -> Dict[str, Any]:
        """Resume application after CAPTCHA solved"""
        # Placeholder for resume logic
        return {
            'status': 'success',
            'message': 'Session resumed. Please continue in browser.'
        }
