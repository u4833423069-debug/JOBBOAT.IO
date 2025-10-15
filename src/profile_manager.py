"""
Profile Manager - Handle user profiles, authentication, and data persistence
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from passlib.hash import bcrypt

logger = logging.getLogger(__name__)

DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def safe_bcrypt_hash(password: str) -> str:
    """Hash a password safely, truncating over 72 bytes"""
    return bcrypt.hash(password[:72])

def load_users() -> Dict[str, Any]:
    """Load all users from JSON file"""
    if not os.path.exists(USERS_FILE):
        # Create demo user
        demo_users = {
            'demo@aijobbot.com': {
                'username': 'demo_user',
                'email': 'demo@aijobbot.com',
                'password': safe_bcrypt_hash('demo123'),
                'location': 'San Francisco, CA',
                'experience_years': 5,
                'credits': 5,
                'cv_data': {
                    'name': 'Demo User',
                    'email': 'demo@aijobbot.com',
                    'phone': '+1 (555) 123-4567',
                    'location': 'San Francisco, CA',
                    'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'SQL', 'Docker', 'AWS'],
                    'experience': [
                        'Senior Software Engineer at TechCorp (3 years)',
                        'Full Stack Developer at StartupXYZ (2 years)'
                    ],
                    'education': [
                        'BS in Computer Science from Stanford University'
                    ],
                    'summary': 'Experienced software engineer with 5+ years building scalable web applications'
                },
                'cv_uploaded': True,
                'created_at': datetime.now().isoformat(),
                'applications': []
            }
        }
        save_users(demo_users)
        return demo_users
    
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        return {}

def save_users(users: Dict[str, Any]):
    """Save users to JSON file"""
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving users: {e}")

def create_user(email: str, username: str, password: str, 
                location: str = '', experience_years: int = 0) -> Dict[str, Any]:
    """
    Create new user account
    
    Returns:
        User data dict or error dict with 'error' key
    """
    users = load_users()
    
    # Check if user exists
    if email in users:
        return {'error': 'Email already registered'}
    
    # Hash password
    hashed_password = safe_bcrypt_hash(password)
    
    # Create user
    user_data = {
        'username': username,
        'email': email,
        'password': hashed_password,
        'location': location,
        'experience_years': experience_years,
        'credits': 5,  # Free credits on signup
        'cv_data': None,
        'cv_uploaded': False,
        'created_at': datetime.now().isoformat(),
        'applications': []
    }
    
    users[email] = user_data
    save_users(users)
    
    logger.info(f"Created new user: {email}")
    return user_data

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Authenticate user
    
    Returns:
        User data if successful, None otherwise
    """
    users = load_users()
    
    if email not in users:
        return None
    
    user = users[email]
    
    # Verify password (truncate to 72 bytes)
    if bcrypt.verify(password[:72], user['password']):
        return user
    
    return None

def get_user(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    users = load_users()
    return users.get(email)

def update_user(email: str, updates: Dict[str, Any]) -> bool:
    """Update user data"""
    users = load_users()
    
    if email not in users:
        return False
    
    users[email].update(updates)
    save_users(users)
    return True

def save_cv_data(email: str, cv_data: Dict[str, Any]) -> bool:
    """Save parsed CV data for user"""
    return update_user(email, {
        'cv_data': cv_data,
        'cv_uploaded': True
    })

def use_credits(email: str, amount: int = 1) -> bool:
    """
    Use credits from user account
    
    Returns:
        True if successful, False if insufficient credits
    """
    users = load_users()
    user = users.get(email)
    
    if not user or user.get('credits', 0) < amount:
        return False
    
    user['credits'] = user.get('credits', 0) - amount
    save_users(users)
    return True

def add_credits(email: str, amount: int):
    """Add credits to user account"""
    users = load_users()
    user = users.get(email)
    
    if user:
        user['credits'] = user.get('credits', 0) + amount
        save_users(users)

def add_application(email: str, job_data: Dict[str, Any]):
    """Add job application to user's history"""
    users = load_users()
    user = users.get(email)
    
    if user:
        if 'applications' not in user:
            user['applications'] = []
        
        application = {
            **job_data,
            'applied_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        user['applications'].append(application)
        save_users(users)

def get_user_stats(email: str) -> Dict[str, Any]:
    """Get user statistics"""
    user = get_user(email)
    
    if not user:
        return {}
    
    applications = user.get('applications', [])
    
    return {
        'total_applications': len(applications),
        'pending': len([a for a in applications if a.get('status') == 'pending']),
        'interviews': len([a for a in applications if a.get('status') == 'interview']),
        'credits': user.get('credits', 0),
        'cv_uploaded': user.get('cv_uploaded', False)
    }

def delete_user_data(email: str) -> bool:
    """Delete user data (GDPR compliance)"""
    users = load_users()
    
    if email in users:
        del users[email]
        save_users(users)
        logger.info(f"Deleted user data: {email}")
        return True
    
    return False
