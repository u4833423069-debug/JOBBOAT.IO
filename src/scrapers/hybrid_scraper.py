"""
Hybrid Job Scraper - Unified interface for multiple job platforms
Supports LinkedIn, Indeed, Glassdoor, Welcome to the Jungle, and more
"""

import logging
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
import random

logger = logging.getLogger(__name__)

class HybridScraper:
    """Base scraper with common functionality"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search_jobs(self, query: str, location: str = '', limit: int = 20) -> List[Dict[str, Any]]:
        """Search jobs across multiple platforms"""
        all_jobs = []
        
        # Try multiple sources
        try:
            indeed_jobs = self._search_indeed(query, location, limit // 2)
            all_jobs.extend(indeed_jobs)
        except Exception as e:
            logger.error(f"Indeed scraping error: {e}")
        
        try:
            glassdoor_jobs = self._search_glassdoor(query, location, limit // 2)
            all_jobs.extend(glassdoor_jobs)
        except Exception as e:
            logger.error(f"Glassdoor scraping error: {e}")
        
        # Deduplicate by title + company
        seen = set()
        unique_jobs = []
        for job in all_jobs:
            key = f"{job.get('title', '')}_{job.get('company', '')}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs[:limit]
    
    def _search_indeed(self, query: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """Search Indeed jobs"""
        jobs = []
        
        try:
            params = {
                'q': query,
                'l': location,
                'start': 0
            }
            
            url = 'https://www.indeed.com/jobs'
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job_seen_beacon', limit=limit)
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2', class_='jobTitle')
                        company_elem = card.find('span', class_='companyName')
                        location_elem = card.find('div', class_='companyLocation')
                        link_elem = card.find('a', class_='jcs-JobTitle')
                        
                        if title_elem and company_elem:
                            job = {
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True),
                                'location': location_elem.get_text(strip=True) if location_elem else location,
                                'platform': 'Indeed',
                                'url': f"https://www.indeed.com{link_elem['href']}" if link_elem and link_elem.get('href') else '',
                                'description': '',
                                'match_score': 0
                            }
                            jobs.append(job)
                    except Exception as e:
                        logger.debug(f"Error parsing job card: {e}")
                        continue
            
            time.sleep(random.uniform(1, 2))  # Rate limiting
            
        except Exception as e:
            logger.error(f"Indeed search error: {e}")
        
        return jobs
    
    def _search_glassdoor(self, query: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """Search Glassdoor jobs"""
        jobs = []
        
        try:
            # Glassdoor API-like search
            url = f'https://www.glassdoor.com/Job/jobs.htm'
            params = {
                'sc.keyword': query,
                'locT': 'C',
                'locId': '1147401'  # Default location ID
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('li', class_='react-job-listing', limit=limit)
                
                for card in job_cards:
                    try:
                        title_elem = card.find('a', class_='jobLink')
                        company_elem = card.find('div', class_='employer-name')
                        location_elem = card.find('span', class_='job-location')
                        
                        if title_elem:
                            job = {
                                'title': title_elem.get_text(strip=True),
                                'company': company_elem.get_text(strip=True) if company_elem else 'Unknown',
                                'location': location_elem.get_text(strip=True) if location_elem else location,
                                'platform': 'Glassdoor',
                                'url': title_elem.get('href', ''),
                                'description': '',
                                'match_score': 0
                            }
                            jobs.append(job)
                    except Exception as e:
                        logger.debug(f"Error parsing Glassdoor card: {e}")
                        continue
            
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            logger.error(f"Glassdoor search error: {e}")
        
        return jobs
    
    def calculate_match_score(self, job: Dict[str, Any], cv_data: Dict[str, Any]) -> int:
        """
        Calculate match score between job and CV
        
        Returns:
            Match score 0-100
        """
        if not cv_data or not cv_data.get('skills'):
            return 50  # Default score
        
        user_skills = set(skill.lower() for skill in cv_data.get('skills', []))
        job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('requirements', '')}".lower()
        
        # Count skill matches
        matches = sum(1 for skill in user_skills if skill in job_text)
        
        if not user_skills:
            return 50
        
        # Calculate percentage
        score = int((matches / len(user_skills)) * 100)
        return min(score, 100)
