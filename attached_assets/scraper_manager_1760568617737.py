"""
Scraper Manager - Coordinate job searches across multiple platforms
"""

import logging
from typing import List, Dict, Any
from src.scrapers.hybrid_scraper import HybridScraper

logger = logging.getLogger(__name__)

class ScraperManager:
    """Manage job scraping operations"""
    
    def __init__(self):
        self.scraper = HybridScraper()
    
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
        try:
            # Search jobs
            jobs = self.scraper.search_jobs(query, location, limit)
            
            # Calculate match scores if CV data provided
            if cv_data:
                for job in jobs:
                    job['match_score'] = self.scraper.calculate_match_score(job, cv_data)
            
            # Sort by match score
            jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            
            logger.info(f"Found {len(jobs)} jobs for query: {query}")
            return jobs
            
        except Exception as e:
            logger.error(f"Job search error: {e}")
            return []
    
    def get_job_details(self, job_url: str) -> Dict[str, Any]:
        """Fetch detailed job information"""
        # For now, return placeholder
        return {
            'description': 'Full job description would be fetched here',
            'requirements': ['Requirement 1', 'Requirement 2'],
            'benefits': ['Benefit 1', 'Benefit 2']
        }
