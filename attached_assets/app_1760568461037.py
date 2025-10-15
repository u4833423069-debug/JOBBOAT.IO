"""
AI JobBot - Production-Grade Flask Application
Steve Jobs-level design with ethical AI career assistance
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import json

# Import modules
from src.profile_manager import (
    create_user, authenticate_user, get_user, update_user,
    save_cv_data, use_credits, add_credits, add_application,
    get_user_stats, delete_user_data
)
from src.cv_parser import parse_cv_file, parse_cv_text
from src.letter_generator import generate_cover_letter, get_sample_letter
from src.scraper_manager import ScraperManager
from src.auto_apply.apply_manager import ApplyManager
from src.ai_client import get_ai_client
from config.translations import get_translation, TRANSLATIONS

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'data/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS
CORS(app)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# Initialize managers
scraper_manager = ScraperManager()
apply_manager = ApplyManager()

# ============================================
# TEMPLATE CONTEXT PROCESSORS
# ============================================

@app.context_processor
def inject_global_context():
    """Inject common variables into all templates"""
    user_email = session.get('user_email')
    user = get_user(user_email) if user_email else None
    current_lang = session.get('language', 'en')
    
    return {
        'user': user,
        'current_lang': current_lang,
        't': get_translation(current_lang),
        'now': datetime.now()
    }

# ============================================
# AUTHENTICATION ROUTES
# ============================================

@app.route('/')
def index():
    """Landing page"""
    if 'user_email' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login/Register page"""
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    # Handle POST (login or register)
    data = request.get_json()
    action = data.get('action')
    
    if action == 'login':
        email = data.get('email')
        password = data.get('password')
        
        user = authenticate_user(email, password)
        if user:
            session['user_email'] = email
            session['username'] = user.get('username')
            
            # Check for Marcus Aurelius quote cookie
            show_quote = request.cookies.get('aurelius_shown') is None
            
            response = jsonify({
                'success': True,
                'message': 'Login successful',
                'show_quote': show_quote
            })
            
            if show_quote:
                # Set cookie for 2-3 hours
                response.set_cookie('aurelius_shown', 'true', max_age=9000)
            
            return response
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    
    elif action == 'register':
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        location = data.get('location', '')
        experience_years = data.get('experience_years', 0)
        
        result = create_user(email, username, password, location, experience_years)
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 400
        
        # Auto-login after registration
        session['user_email'] = email
        session['username'] = username
        
        return jsonify({
            'success': True,
            'message': f'Account created! You received {result.get("credits", 5)} free credits.'
        })
    
    return jsonify({'success': False, 'error': 'Invalid action'}), 400

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/language/<lang>')
def set_language(lang):
    """Set user language preference"""
    if lang in ['en', 'fr']:
        session['language'] = lang
    return redirect(request.referrer or url_for('index'))

# ============================================
# MAIN APPLICATION ROUTES
# ============================================

@app.route('/dashboard')
def dashboard():
    """Main dashboard"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user = get_user(session['user_email'])
    stats = get_user_stats(session['user_email'])
    
    # Get recent applications
    applications = user.get('applications', [])[-5:]  # Last 5
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         applications=applications,
                         user=user)

@app.route('/cv-upload')
def cv_upload():
    """CV upload page"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user = get_user(session['user_email'])
    return render_template('cv_upload.html', user=user)

@app.route('/job-search')
def job_search():
    """Job search page"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user = get_user(session['user_email'])
    return render_template('job_search.html', user=user)

@app.route('/letter-generator')
def letter_generator():
    """Cover letter generator page"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user = get_user(session['user_email'])
    sample_letter = get_sample_letter()
    
    return render_template('letter_generator.html', 
                         user=user,
                         sample_letter=sample_letter)

@app.route('/applications')
def applications():
    """Applications tracking page"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user = get_user(session['user_email'])
    all_applications = user.get('applications', [])
    
    return render_template('applications.html', 
                         applications=all_applications,
                         user=user)

@app.route('/activity')
def activity():
    """Activity timeline page"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user = get_user(session['user_email'])
    
    # Load activity log
    activity_file = 'data/activity.json'
    activities = []
    
    if os.path.exists(activity_file):
        try:
            with open(activity_file, 'r') as f:
                all_activities = json.load(f)
                activities = [a for a in all_activities if a.get('user') == session['user_email']][-20:]
        except Exception as e:
            logger.error(f"Activity load error: {e}")
    
    return render_template('activity.html', 
                         activities=activities,
                         user=user)

@app.route('/my-consultant')
def my_consultant():
    """Zby AI Consultant page"""
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user = get_user(session['user_email'])
    
    return render_template('my_consultant.html', user=user)

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/parse-cv', methods=['POST'])
def api_parse_cv():
    """Parse uploaded CV"""
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    if 'cv_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['cv_file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Save file
    filename = f"{session['user_email']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Parse CV
    cv_data = parse_cv_file(filepath)
    
    if 'error' in cv_data:
        return jsonify(cv_data), 400
    
    # Save to user profile
    save_cv_data(session['user_email'], cv_data)
    
    # Log activity
    log_activity(session['user_email'], 'cv_upload', 'CV uploaded and parsed successfully')
    
    return jsonify({
        'success': True,
        'cv_data': cv_data
    })

@app.route('/api/search-jobs', methods=['POST'])
def api_search_jobs():
    """Search for jobs"""
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    query = data.get('query', '')
    location = data.get('location', '')
    limit = data.get('limit', 20)
    
    user = get_user(session['user_email'])
    cv_data = user.get('cv_data') if user else None
    
    # Search jobs
    jobs = scraper_manager.search_jobs(query, location, limit, cv_data)
    
    # Log activity
    log_activity(session['user_email'], 'job_search', f'Searched: {query}')
    
    return jsonify({
        'success': True,
        'jobs': jobs,
        'count': len(jobs)
    })

@app.route('/api/generate-letter', methods=['POST'])
def api_generate_letter():
    """Generate cover letter"""
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Check credits
    user = get_user(session['user_email'])
    cost = int(os.getenv('CREDIT_COST_PER_LETTER', 1))
    
    if user.get('credits', 0) < cost:
        return jsonify({
            'error': 'Insufficient credits',
            'credits_needed': cost,
            'credits_available': user.get('credits', 0)
        }), 402
    
    data = request.get_json()
    job_info = data.get('job_info', {})
    
    cv_data = user.get('cv_data')
    
    if not cv_data:
        return jsonify({'error': 'Please upload your CV first'}), 400
    
    # Generate letter
    result = generate_cover_letter(job_info, cv_data)
    
    if 'error' in result:
        return jsonify(result), 500
    
    # Deduct credits
    use_credits(session['user_email'], cost)
    
    # Log activity
    log_activity(session['user_email'], 'letter_generated', 
                f'Generated letter for {job_info.get("company", "Unknown")}')
    
    return jsonify({
        'success': True,
        'letter': result
    })

@app.route('/api/apply', methods=['POST'])
def api_apply():
    """Apply to job (with CAPTCHA handling)"""
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Check credits
    user = get_user(session['user_email'])
    cost = int(os.getenv('CREDIT_COST_PER_APPLY', 1))
    
    if user.get('credits', 0) < cost:
        return jsonify({
            'error': 'Insufficient credits',
            'credits_needed': cost
        }), 402
    
    data = request.get_json()
    job_url = data.get('job_url')
    platform = data.get('platform', 'linkedin')
    job_data = data.get('job_data', {})
    
    if not job_url:
        return jsonify({'error': 'Job URL required'}), 400
    
    # Attempt application
    result = apply_manager.apply_to_job(job_url, platform, user)
    
    # If successful or CAPTCHA, deduct credits
    if result['status'] in ['success', 'captcha_required']:
        use_credits(session['user_email'], cost)
        
        # Add to applications
        add_application(session['user_email'], {
            **job_data,
            'url': job_url,
            'platform': platform
        })
        
        # Log activity
        log_activity(session['user_email'], 'job_apply', 
                    f'Applied to {job_data.get("title", "job")} at {job_data.get("company", "company")}')
    
    return jsonify(result)

@app.route('/api/consult', methods=['POST'])
def api_consult():
    """Zby AI Consultant chat"""
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Message required'}), 400
    
    user = get_user(session['user_email'])
    stats = get_user_stats(session['user_email'])
    
    # Build context
    context = {
        'cv_uploaded': user.get('cv_uploaded', False),
        'skills': user.get('cv_data', {}).get('skills', []) if user.get('cv_data') else [],
        'applications_count': stats.get('total_applications', 0),
        'credits_remaining': user.get('credits', 0)
    }
    
    # Get AI response
    try:
        ai_client = get_ai_client()
        response = ai_client.consultant_chat(user_message, context)
        
        # Append business card to response occasionally (every 3rd message)
        if 'business_card_count' not in session:
            session['business_card_count'] = 0
        
        session['business_card_count'] += 1
        
        if session['business_card_count'] % 3 == 0:
            response += "\n\n---\n💼 **Azer Rached** — AI Career Consultant & Developer of AIJobBot\n🌐 www.ai-jobbot.com | 📧 contact@ai-jobbot.com"
        
        # Log activity
        log_activity(session['user_email'], 'consultant_chat', f'Asked Zby: {user_message[:50]}...')
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        logger.error(f"Consultant error: {e}")
        return jsonify({
            'success': False,
            'error': 'Zby is temporarily unavailable. Please ensure Ollama is running.'
        }), 500

@app.route('/api/account/delete', methods=['POST'])
def api_delete_account():
    """Delete user account (GDPR compliance)"""
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    confirm = data.get('confirm', False)
    
    if not confirm:
        return jsonify({'error': 'Confirmation required'}), 400
    
    email = session['user_email']
    
    if delete_user_data(email):
        session.clear()
        return jsonify({'success': True, 'message': 'Account deleted'})
    
    return jsonify({'error': 'Deletion failed'}), 500

@app.route('/api/stripe/checkout', methods=['POST'])
def api_stripe_checkout():
    """Create Stripe checkout session (stub for MVP)"""
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # TODO: Implement Stripe checkout
    # For now, return placeholder
    return jsonify({
        'success': False,
        'message': 'Payment integration coming soon',
        'note': 'Contact support for manual credit purchase'
    })

# ============================================
# HELPER FUNCTIONS
# ============================================

def log_activity(user_email: str, activity_type: str, description: str):
    """Log user activity"""
    activity_file = 'data/activity.json'
    
    activity_entry = {
        'user': user_email,
        'type': activity_type,
        'description': description,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        activities = []
        if os.path.exists(activity_file):
            with open(activity_file, 'r') as f:
                activities = json.load(f)
        
        activities.append(activity_entry)
        
        # Keep last 1000 activities
        activities = activities[-1000:]
        
        with open(activity_file, 'w') as f:
            json.dump(activities, f, indent=2)
            
    except Exception as e:
        logger.error(f"Activity logging error: {e}")

@app.route('/health')
def health():
    """Health check endpoint"""
    ai_client = get_ai_client()
    ollama_status = ai_client.check_connection()
    
    return jsonify({
        'status': 'healthy',
        'ollama': 'connected' if ollama_status else 'disconnected',
        'timestamp': datetime.now().isoformat()
    })

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"Server error: {e}")
    return jsonify({'error': 'Internal server error'}), 500

# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
