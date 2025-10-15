"""
CV Parser - Extract structured data from PDF/DOCX resumes
"""

import logging
import os
from typing import Dict, Any, Optional
import PyPDF2
from docx import Document
from src.ai_client import get_ai_client

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return ""

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    try:
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        return ""

def parse_cv_file(file_path: str) -> Dict[str, Any]:
    """
    Parse CV file and extract structured information
    
    Args:
        file_path: Path to CV file (PDF or DOCX)
    
    Returns:
        Dictionary with parsed CV data
    """
    # Check file exists
    if not os.path.exists(file_path):
        return {'error': 'File not found'}
    
    # Extract text based on file extension
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif file_ext in ['.docx', '.doc']:
        text = extract_text_from_docx(file_path)
    else:
        return {'error': f'Unsupported file type: {file_ext}'}
    
    if not text:
        return {'error': 'Could not extract text from file'}
    
    # Use AI to parse the CV
    try:
        ai_client = get_ai_client()
        cv_data = ai_client.parse_cv_text(text)
        cv_data['raw_text'] = text[:1000]  # Store first 1000 chars
        cv_data['file_path'] = file_path
        return cv_data
    except Exception as e:
        logger.error(f"CV parsing error: {e}")
        return {
            'error': str(e),
            'raw_text': text[:500],
            'file_path': file_path
        }

def parse_cv_text(text: str) -> Dict[str, Any]:
    """Parse CV from raw text"""
    try:
        ai_client = get_ai_client()
        return ai_client.parse_cv_text(text)
    except Exception as e:
        logger.error(f"CV text parsing error: {e}")
        return {'error': str(e)}
