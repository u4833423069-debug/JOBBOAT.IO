"""
Base Auto-Apply System - Safe automation with CAPTCHA detection
Runs in headful mode and uses human-in-the-loop for CAPTCHAs
"""

import logging
import json
import os
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

SESSIONS_DIR = 'data/sessions'
os.makedirs(SESSIONS_DIR, exist_ok=True)

class BaseAutoApply:
    """Base class for platform-specific auto-apply modules"""
    
    def __init__(self, platform_name: str, headless: bool = False):
        """
        Initialize auto-apply system
        
        Args:
            platform_name: Name of the platform (linkedin, indeed, etc.)
            headless: Run in headless mode (default False for CAPTCHA handling)
        """
        self.platform_name = platform_name
        self.headless = headless
        self.driver = None
        self.wait = None
    
    def init_driver(self):
        """Initialize Selenium WebDriver in headful mode"""
        try:
            options = webdriver.ChromeOptions()
            
            # Headful mode for CAPTCHA handling
            if self.headless:
                options.add_argument('--headless')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 10)
            
            logger.info(f"Initialized {self.platform_name} driver (headless={self.headless})")
            
        except Exception as e:
            logger.error(f"Driver initialization error: {e}")
            raise
    
    def detect_captcha(self) -> bool:
        """
        Detect if CAPTCHA is present on the page
        
        Returns:
            True if CAPTCHA detected
        """
        try:
            # Check for common CAPTCHA indicators
            captcha_indicators = [
                "//iframe[contains(@src, 'recaptcha')]",
                "//iframe[contains(@src, 'captcha')]",
                "//*[contains(@class, 'g-recaptcha')]",
                "//*[contains(@class, 'captcha')]",
                "//*[contains(text(), 'verify you are human')]",
                "//*[contains(text(), 'security check')]"
            ]
            
            for xpath in captcha_indicators:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    if elements:
                        logger.warning(f"CAPTCHA detected: {xpath}")
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"CAPTCHA detection error: {e}")
            return False
    
    def save_session(self, user_email: str) -> str:
        """Save browser session (cookies) for later resume"""
        try:
            session_file = os.path.join(SESSIONS_DIR, f"{user_email}_{self.platform_name}.json")
            
            cookies = self.driver.get_cookies()
            session_data = {
                'cookies': cookies,
                'url': self.driver.current_url
            }
            
            # Encrypt session data
            encryption_key = os.getenv('ENCRYPTION_KEY', Fernet.generate_key().decode())
            fernet = Fernet(encryption_key.encode())
            encrypted_data = fernet.encrypt(json.dumps(session_data).encode())
            
            with open(session_file, 'wb') as f:
                f.write(encrypted_data)
            
            logger.info(f"Saved session for {user_email} on {self.platform_name}")
            return session_file
            
        except Exception as e:
            logger.error(f"Session save error: {e}")
            return ""
    
    def load_session(self, user_email: str) -> bool:
        """Load saved browser session"""
        try:
            session_file = os.path.join(SESSIONS_DIR, f"{user_email}_{self.platform_name}.json")
            
            if not os.path.exists(session_file):
                return False
            
            # Decrypt session data
            encryption_key = os.getenv('ENCRYPTION_KEY', Fernet.generate_key().decode())
            fernet = Fernet(encryption_key.encode())
            
            with open(session_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = fernet.decrypt(encrypted_data)
            session_data = json.loads(decrypted_data)
            
            # Navigate to saved URL
            self.driver.get(session_data['url'])
            
            # Load cookies
            for cookie in session_data['cookies']:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    logger.debug(f"Could not add cookie: {e}")
            
            # Refresh page
            self.driver.refresh()
            
            logger.info(f"Loaded session for {user_email} on {self.platform_name}")
            return True
            
        except Exception as e:
            logger.error(f"Session load error: {e}")
            return False
    
    def safe_click(self, element):
        """Safely click an element"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            self.driver.execute_script("arguments[0].click();", element)
        except Exception as e:
            logger.debug(f"Safe click error: {e}")
            element.click()
    
    def type_text(self, element, text: str):
        """Type text into an input field"""
        try:
            element.clear()
            element.send_keys(text)
        except Exception as e:
            logger.error(f"Type text error: {e}")
    
    def cleanup(self):
        """Close browser and cleanup"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def apply_to_job(self, job_url: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply to job - must be implemented by platform-specific classes
        
        Returns:
            Dict with status: 'success', 'captcha_required', or 'error'
        """
        raise NotImplementedError("Platform-specific implementation required")
