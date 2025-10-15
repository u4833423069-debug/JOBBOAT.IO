from .base_auto_apply import BaseAutoApply
from typing import Dict, Any
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)

class GlassdoorAutoApply(BaseAutoApply):
    """Glassdoor-specific auto-apply implementation with CAPTCHA detection"""
    
    def __init__(self, headless: bool = False):
        super().__init__("glassdoor", headless)
    
    def apply_to_job(self, job_url: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply to Glassdoor job with CAPTCHA handling
        
        Args:
            job_url: Glassdoor job URL
            user_data: User credentials and CV data
        
        Returns:
            Status dict with application result
        """
        try:
            self.init_driver()
            
            # Navigate to job
            self.driver.get(job_url)
            time.sleep(2)
            
            # Check for CAPTCHA early
            if self.detect_captcha():
                session_file = self.save_session(user_data.get('email', 'user'))
                return {
                    'status': 'captcha_required',
                    'message': 'Please solve the CAPTCHA in the browser, then click Done',
                    'session_file': session_file,
                    'instructions': 'Complete the security check, then return and click Done'
                }
            
            # Find Glassdoor Easy Apply button
            try:
                apply_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Easy Apply') or contains(., 'Apply Now')]"))
                )
                self.safe_click(apply_button)
                time.sleep(2)
                
                # Check for CAPTCHA after clicking
                if self.detect_captcha():
                    session_file = self.save_session(user_data.get('email', 'user'))
                    return {
                        'status': 'captcha_required',
                        'message': 'CAPTCHA detected during application',
                        'session_file': session_file
                    }
                
                # Application initiated
                logger.info(f"Initiated Glassdoor application for {job_url}")
                
                return {
                    'status': 'success',
                    'message': 'Glassdoor application initiated. Please complete in the browser.',
                    'note': 'Form auto-fill requires manual review in MVP'
                }
                
            except TimeoutException:
                return {
                    'status': 'error',
                    'message': 'Easy Apply button not found'
                }
                
        except Exception as e:
            logger.error(f"Glassdoor application error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
        finally:
            if self.driver:
                time.sleep(5)  # Keep browser open briefly
                # Don't close if CAPTCHA - user needs it
