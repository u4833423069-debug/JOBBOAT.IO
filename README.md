# 🤖 AI JobBot

**Your AI-Powered Career Automation Platform**

AI JobBot is an emotionally intelligent SaaS platform that automates your job search across French and international job platforms. Featuring Zby - your AI career consultant powered by Claude, CV parsing with Ollama Qwen2, and automated job applications.

## ✨ Features

### 🎯 Core Capabilities
- **Dual AI Intelligence**
  - Ollama Qwen2 for CV parsing (local, fast)
  - Anthropic Claude for consultant chat (natural, empathetic)
- **French Job Platforms** (Primary)
  - Indeed France
  - Welcome to the Jungle
  - Apec
  - JobTeaser
- **International Platforms**
  - LinkedIn
  - Glassdoor
  - Indeed International

### 💼 Automation Features
- Automatic CV parsing and skill extraction
- Personalized cover letter generation
- Auto-apply to matching jobs
- Real-time job matching with score calculation
- Application tracking and analytics

### 🎨 Design
- Glassmorphism UI with Palestine-inspired colors
  - Red: #E53E3E
  - Turquoise: #00F0FF
  - Green: #00FF88
- Cinematic animations and neon effects
- Responsive design for all devices

### 💳 Subscription
- €5/month recurring subscription
- 1-month free trial
- Stripe payment integration

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Ollama installed locally
- Anthropic API key (optional, for Claude consultant)

### Installation

1. **Clone and install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up Ollama**
```bash
# Install Ollama from https://ollama.ai
ollama pull qwen2:latest
ollama serve
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run the application**
```bash
python app.py
```

Visit `http://localhost:5000`

## 📁 Project Structure

```
ai-jobbot/
├── app.py                 # Main Flask application
├── src/
│   ├── ai_client.py      # Dual AI client (Ollama + Claude)
│   ├── cv_parser.py      # CV parsing with Qwen2
│   ├── letter_generator.py  # Cover letter generation
│   ├── profile_manager.py    # User management
│   ├── scraper_manager.py    # Job search coordination
│   ├── scrapers/
│   │   ├── french_platforms.py  # French job scrapers
│   │   └── hybrid_scraper.py    # International scrapers
│   └── auto_apply/
│       ├── apply_manager.py     # Application automation
│       ├── base_auto_apply.py   # Base auto-apply class
│       ├── linkedin_apply.py    # LinkedIn automation
│       ├── indeed_apply.py      # Indeed automation
│       └── glassdoor_apply.py   # Glassdoor automation
├── config/
│   └── translations.py    # Multi-language support
├── templates/             # HTML templates
├── static/               # CSS, JS, images
└── data/                 # User data and uploads
```

## 🔧 Configuration

### Environment Variables

```bash
# Session
SESSION_SECRET=your-secret-key

# Ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2:latest

# Anthropic (optional)
ANTHROPIC_API_KEY=your-anthropic-key

# Stripe
STRIPE_SECRET_KEY=your-stripe-key
STRIPE_PRICE_ID=price_xxxxx

# Flask
FLASK_ENV=development
PORT=5000
```

## 🌐 API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### CV Management
- `POST /api/parse-cv` - Parse CV file (uses Ollama Qwen2)
- `GET /api/cv-data` - Get parsed CV data

### Job Search
- `POST /api/search-jobs` - Search jobs across platforms
- `GET /api/job-details/<job_id>` - Get job details

### AI Consultant
- `POST /api/consult` - Chat with Zby (uses Claude)
- `GET /api/chat-history` - Get chat history

### Applications
- `POST /api/auto-apply` - Auto-apply to job
- `GET /api/applications` - Get user applications
- `POST /api/generate-letter` - Generate cover letter

### Subscription
- `POST /api/create-checkout` - Create Stripe checkout
- `GET /api/subscription-status` - Check subscription

## 🎭 Zby AI Consultant

Zby is your emotionally intelligent career consultant powered by Anthropic Claude. Features include:

- Natural, empathetic conversations
- Career advice and guidance
- CV improvement suggestions
- Interview preparation
- Job market insights

**Business Card**: Azer Rached's contact information is embedded in the consultant interface with neon effects.

## 🇫🇷 French Job Platforms

Priority integration with French job boards:

1. **Indeed France** - Largest French job board
2. **Welcome to the Jungle** - Modern French tech jobs
3. **Apec** - Executive and manager positions
4. **JobTeaser** - Student and graduate jobs

All scrapers include fallback strategies to ensure results.

## 💰 Pricing

- **Free Trial**: 1 month free
- **Monthly**: €5/month
- **Credits System**: 
  - 100 credits on signup
  - 500 credits per month for subscribers
  - CV parsing: 5 credits
  - Job search: 2 credits
  - Auto-apply: 10 credits
  - Consultant chat: 3 credits

## 🔐 Security

- Secure session management
- Password hashing with bcrypt
- Environment-based secrets
- CORS protection
- File upload validation

## 🚢 Deployment

### Replit Deployment
```bash
# Project is ready for Replit deployment
# Click "Deploy" and configure environment variables
```

### Manual Deployment
```bash
# Use production WSGI server
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

## 📊 Technologies

- **Backend**: Flask, SQLAlchemy
- **AI**: Ollama (Qwen2), Anthropic Claude
- **Scraping**: BeautifulSoup, Selenium
- **Payment**: Stripe
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

## 🤝 Support

For issues, feature requests, or questions:
- Email: support@aijobbot.com
- Contact: Azer Rached (see consultant page)

## 📜 License

Proprietary - © 2025 AI JobBot

---

**Built with ❤️ for job seekers worldwide**
