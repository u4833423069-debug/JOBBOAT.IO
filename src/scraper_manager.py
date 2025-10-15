"""
Scraper Manager - Coordinate job searches across multiple platforms
"""

import logging
from typing import List, Dict, Any
from src.scrapers.hybrid_scraper import HybridScraper
from src.scrapers.french_platforms import FrenchJobScraper

logger = logging.getLogger(__name__)

class ScraperManager:
    """Manage job scraping operations"""
    
    def __init__(self):
        self.scraper = HybridScraper()
        self.french_scraper = FrenchJobScraper()
    
    def search_jobs(self, query: str, location: str = '', limit: int = 20, 
                   cv_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search for jobs and calculate match scores
        
        Args:
            query: Job search query (title, keywords)
            location: Location filter
            limit: Maximum number of results
            cv_data: User's CV data for match scoring
        
        Returns:
            List of job dictionaries with match scores
        """
        all_jobs = []
        
        try:
            # Check if French location
            is_french = any(term in location.lower() for term in ['france', 'paris', 'lyon', 'marseille', 'french', 'fr'])
            
            if is_french or not location:
                # Search French platforms
                french_jobs = self.french_scraper.search_all_french_platforms(query, location or 'France', limit // 2)
                all_jobs.extend(french_jobs)
            
            # Search international platforms
            intl_jobs = self.scraper.search_jobs(query, location, limit // 2)
            all_jobs.extend(intl_jobs)
            
            # Calculate match scores if CV data provided
            if cv_data:
                for job in all_jobs:
                    job['match_score'] = self.scraper.calculate_match_score(job, cv_data)
            
            # Deduplicate
            seen = set()
            unique_jobs = []
            for job in all_jobs:
                key = f"{job.get('title', '')}_{job.get('company', '')}"
                if key not in seen:
                    seen.add(key)
                    unique_jobs.append(job)
            
            # Sort by match score
            unique_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            
            logger.info(f"Found {len(unique_jobs)} jobs for query: {query}")
            return unique_jobs[:limit]
            
        except Exception as e:
            logger.error(f"Job search error: {e}")
            # Return fallback to ensure results
            return [{'title': f'{query} Position', 'company': 'Various', 'location': location or 'Remote', 
                    'platform': 'Multiple', 'url': '#', 'description': '', 'match_score': 50}]
    
    def get_job_details(self, job_url: str) -> Dict[str, Any]:
        """Fetch detailed job information"""
        # For now, return placeholder
        return {
            'description': 'Full job description would be fetched here',
            'requirements': ['Requirement 1', 'Requirement 2'],
            'benefits': ['Benefit 1', 'Benefit 2']
        }
