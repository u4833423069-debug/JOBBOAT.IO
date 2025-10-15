"""
AI JobBot - Enhanced Flask Application
Ollama Qwen2 CV parsing + Anthropic Claude consultant + French job platforms
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv
import json

# Import modules
from src.profile_manager import (
    create_user, authenticate_user, get_user, save_cv_data, 
    use_credits, add_application, get_user_stats
)
from src.cv_parser import parse_cv_file
from src.letter_generator import generate_cover_letter, get_sample_letter
from src.scraper_manager import ScraperManager
from src.auto_apply.apply_manager import ApplyManager
from src.ai_client import get_ai_client
from config.translations import get_translation

# Load environment
load_dotenv()

# Initialize Flask
app = Flask(__name__)
app.secret_key = os.getenv('SESSION_SECRET', os.getenv('SECRET_KEY', 'dev-secret-key'))
app.config['UPLOAD_FOLDER'] = 'data/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize managers
scraper_manager = ScraperManager()
apply_manager = ApplyManager()

# Context processor
@app.context_processor
def inject_global_context():
    user_email = session.get('user_email')
    user = get_user(user_email) if user_email else None
    return {
        'user': user,
        'current_lang': session.get('language', 'en'),
        't': get_translation(session.get('language', 'en')),
        'now': datetime.now()
    }

# Routes
@app.route('/')
def index():
    if 'user_email' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.form or request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    
    user = authenticate_user(email, password)
    if user:
        session['user_email'] = email
        return jsonify({'success': True}) if request.is_json else redirect(url_for('dashboard'))
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.form or request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    username = data.get('username', email.split('@')[0])
    location = data.get('location', '')
    
    user = create_user(email, username, password, location)
    if user:
        session['user_email'] = email
        return jsonify({'success': True}) if request.is_json else redirect(url_for('dashboard'))
    
    return jsonify({'error': 'User already exists'}), 400

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user = get_user(session['user_email'])
    stats = get_user_stats(session['user_email'])
    return render_template('dashboard.html', user=user, stats=stats)

@app.route('/consultant')
def consultant():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('consultant.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/parse-cv', methods=['POST'])
def api_parse_cv():
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'cv_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['cv_file']
    filename = f"{session['user_email']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(filepath)
    
    cv_data = parse_cv_file(filepath)
    
    if 'error' not in cv_data:
        # Ensure data is JSON-serializable
        serialized_cv = {
            'name': cv_data.get('name', ''),
            'email': cv_data.get('email', ''),
            'phone': cv_data.get('phone', ''),
            'current_role': cv_data.get('current_role', ''),
            'years_experience': cv_data.get('years_experience', 0),
            'summary': cv_data.get('summary', ''),
            'skills': cv_data.get('skills', []) if isinstance(cv_data.get('skills'), list) else [],
            'education': cv_data.get('education', []) if isinstance(cv_data.get('education'), list) else [],
            'work_experience': cv_data.get('work_experience', []) if isinstance(cv_data.get('work_experience'), list) else [],
            'languages': cv_data.get('languages', []) if isinstance(cv_data.get('languages'), list) else []
        }
        
        save_cv_data(session['user_email'], serialized_cv)
        return jsonify({'success': True, 'redirect': '/cv-results'})
    
    return jsonify({'success': False, 'error': cv_data.get('error', 'Parsing failed')}), 400

@app.route('/cv-results')
def cv_results():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user = get_user(session['user_email'])
    cv_data = user.get('cv_data', {})
    
    if not cv_data:
        return redirect(url_for('dashboard'))
    
    return render_template('cv_results.html', cv_data=cv_data)

@app.route('/api/search-jobs', methods=['POST'])
def api_search_jobs():
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    query = data.get('query', '')
    location = data.get('location', '')
    
    user = get_user(session['user_email'])
    jobs = scraper_manager.search_jobs(query, location, 20, user.get('cv_data'))
    
    return jsonify({'success': True, 'jobs': jobs, 'count': len(jobs)})

@app.route('/api/consult', methods=['POST'])
def api_consult():
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    message = data.get('message', '')
    
    if not message:
        return jsonify({'error': 'Message required'}), 400
    
    user = get_user(session['user_email'])
    stats = get_user_stats(session['user_email'])
    
    context = {
        'cv_uploaded': user.get('cv_uploaded', False),
        'skills': user.get('cv_data', {}).get('skills', []) if user.get('cv_data') else [],
        'applications_count': stats.get('total_applications', 0),
        'credits_remaining': user.get('credits', 0)
    }
    
    try:
        ai_client = get_ai_client()
        response = ai_client.consultant_chat(message, session['user_email'], context)
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        logger.error(f"Consultant error: {e}")
        return jsonify({'error': 'Consultant unavailable'}), 500

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/health')
def health():
    ai_client = get_ai_client()
    status = ai_client.check_connection()
    return jsonify({
        'status': 'healthy',
        'ollama': status.get('ollama', False),
        'claude': status.get('claude', False)
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
