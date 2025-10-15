"""
LinkedIn Auto-Apply Module
Human-in-the-loop CAPTCHA handling
"""

import logging
import time
from typing import Dict, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from src.auto_apply.base_auto_apply import BaseAutoApply

logger = logging.getLogger(__name__)

class LinkedInApply(BaseAutoApply):
    """LinkedIn job application automation"""
    
    def __init__(self, headless: bool = False):
        super().__init__('linkedin', headless)
    
    def apply_to_job(self, job_url: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply to LinkedIn job with CAPTCHA handling
        
        Args:
            job_url: LinkedIn job URL
            user_data: User credentials and CV data
        
        Returns:
            Status dict with 'status', 'message', and optionally 'session_file'
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
                    'message': 'Please solve the CAPTCHA in the browser window, then click Done',
                    'session_file': session_file,
                    'instructions': 'Complete the security check in the browser, then return here and click Done'
                }
            
            # Try to find "Easy Apply" button
            try:
                easy_apply_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'jobs-apply-button')]"))
                )
                self.safe_click(easy_apply_button)
                time.sleep(2)
                
                # Check for CAPTCHA after clicking
                if self.detect_captcha():
                    session_file = self.save_session(user_data.get('email', 'user'))
                    return {
                        'status': 'captcha_required',
                        'message': 'CAPTCHA detected during application',
                        'session_file': session_file
                    }
                
                # Application form handling would go here
                # For MVP, we stop at the Easy Apply modal
                
                logger.info(f"Initiated Easy Apply for {job_url}")
                
                return {
                    'status': 'success',
                    'message': 'Easy Apply initiated. Please complete the application in the browser.',
                    'note': 'Auto-complete of forms requires manual review in MVP'
                }
                
            except TimeoutException:
                return {
                    'status': 'error',
                    'message': 'Easy Apply button not found. This job may require external application.'
                }
            
        except Exception as e:
            logger.error(f"LinkedIn apply error: {e}")
            return {
                'status': 'error',
                'message': f'Application error: {str(e)}'
            }
        
        finally:
            # Keep browser open for CAPTCHA handling
            if self.driver and not self.detect_captcha():
                self.cleanup()
