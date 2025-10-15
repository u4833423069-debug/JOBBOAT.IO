# AI JobBot - Replit Code Agent Guide

## Overview

AI JobBot is an emotionally intelligent career automation SaaS platform that combines local AI (Ollama Qwen2) and cloud AI (Anthropic Claude) to automate job searching and applications across French and international job platforms. The platform features Zby - an AI career consultant - and provides CV parsing, automated cover letter generation, multi-platform job search, and auto-apply functionality with human-in-the-loop CAPTCHA handling.

**Core Value Proposition:** Users upload their CV once, and the platform automatically searches, matches, and applies to relevant jobs while providing personalized career guidance through an empathetic AI consultant.

**Monetization:** Freemium credit system (5 free credits on signup) with €5/month subscription and Stripe integration readiness.

## User Preferences

Preferred communication style: Simple, everyday language.

**Additional User Expectations:**
- CV parsing must be done with Ollama Qwen2 (local, fast, free)
- Users should be able to navigate freely between pages without interrupting background processes (parsing, job search, auto-apply)
- The CV parsing interface should follow the "cinematic design" approach with frame-by-frame display of parsed results
- Design philosophy: "Apple-level" - minimal, intuitive, emotionally engaging
- Palestine-inspired color palette (Red #E53E3E, Turquoise #00F0FF, Green #00FF88) with glassmorphism UI
- All interactions should feel smooth with 60fps animations and microinteractions

## System Architecture

### Dual AI Intelligence System

**Architecture Decision:** Hybrid AI approach using two specialized models instead of a single general-purpose AI.

**Rationale:**
- **Ollama Qwen2** for CV parsing: Runs locally, zero API costs, fast response times, privacy-preserving (CV data never leaves user's machine)
- **Anthropic Claude** for consultant chat: Superior natural language understanding, empathetic tone, conversation memory, better at career advice

**Implementation:**
- `src/ai_client.py` provides unified `AIClient` class with separate methods for Ollama and Claude
- Conversation history stored in-memory for context-aware responses
- Graceful fallback: Claude unavailable → use Ollama for consultant (degraded experience but functional)

**Trade-offs:**
- **Pro:** Optimal cost/performance ratio, privacy for sensitive CV data
- **Con:** Requires Ollama installation locally (mitigated by clear setup docs)

### Flask-Based Monolithic Architecture

**Architecture Decision:** Single Flask application serving both frontend (Jinja2 templates) and backend (API endpoints).

**Rationale:**
- Simplicity: Faster development, easier deployment, single codebase
- Session-based auth sufficient for MVP (no need for JWT complexity)
- Server-side rendering for initial page loads (better SEO, faster first paint)
- AJAX for dynamic operations (CV parsing, job search, consultant chat)

**Structure:**
```
app.py (main Flask app)
├── Routes (HTML pages): /dashboard, /cv-upload, /jobs, /consultant, etc.
├── API Routes (JSON): /api/parse-cv, /api/search-jobs, /api/consult, /api/apply
└── Context Processors: Inject user data, translations into all templates
```

**Trade-offs:**
- **Pro:** Easy to reason about, fast prototyping, minimal DevOps overhead
- **Con:** Harder to scale horizontally (acceptable for MVP stage)

### File-Based Data Persistence (JSON)

**Architecture Decision:** User profiles, CV data, and applications stored in `data/users.json` instead of a traditional database.

**Rationale:**
- Zero database setup/maintenance for MVP
- Human-readable data format (easy debugging)
- Sufficient for <1000 users
- Fast read/write for single-user operations

**Schema:**
```json
{
  "user@email.com": {
    "username": "string",
    "password": "bcrypt_hash",
    "credits": 5,
    "cv_data": {...},
    "applications": [...],
    "activity": [...]
  }
}
```

**Migration Path:** When scaling beyond MVP, migrate to PostgreSQL using same data structure (already designed for relational model).

**Trade-offs:**
- **Pro:** Instant setup, no DB connection issues, easy backups (just copy file)
- **Con:** Concurrent writes can cause race conditions (acceptable for MVP single-user sessions)

### Selenium-Based Auto-Apply with Human-in-the-Loop

**Architecture Decision:** Headful Selenium automation with CAPTCHA detection triggers, not fully autonomous.

**Rationale:**
- CAPTCHAs are unavoidable on job platforms (LinkedIn, Indeed, Glassdoor)
- Fully headless automation gets blocked immediately
- Human-in-the-loop maintains ethical standards and reliability

**Flow:**
1. Selenium opens browser (visible to user)
2. Navigates to job posting
3. If CAPTCHA detected → pause, notify user, save session
4. User solves CAPTCHA in browser
5. User clicks "Done" → automation resumes from saved session

**Implementation:**
- `src/auto_apply/base_auto_apply.py`: Shared CAPTCHA detection logic
- `src/auto_apply/linkedin_apply.py`, `indeed_apply.py`, `glassdoor_apply.py`: Platform-specific apply logic
- Session persistence: Cookies/localStorage saved to `data/sessions/{user_email}_{platform}.pkl`

**Trade-offs:**
- **Pro:** Reliable, ethical, passes platform anti-bot measures
- **Con:** Not fully automated (mitigated by clear UX messaging)

### Multi-Platform Job Scraping

**Architecture Decision:** Unified `ScraperManager` coordinating platform-specific scrapers with intelligent deduplication.

**Rationale:**
- French platforms (Indeed FR, Welcome to the Jungle, Apec, JobTeaser) require specialized scrapers
- International platforms (LinkedIn, Glassdoor, Indeed) have different HTML structures
- Users benefit from aggregated results across all platforms

**Implementation:**
```
ScraperManager
├── FrenchJobScraper (French platforms)
│   ├── indeed_fr, wttj, apec, jobteaser methods
│   └── RSS feeds + BeautifulSoup scraping
└── HybridScraper (International platforms)
    ├── indeed, glassdoor methods
    └── BeautifulSoup + requests
```

**Match Scoring Algorithm:**
- Compare job description against user's CV skills (keyword matching)
- Score: (matched_skills / total_cv_skills) * 100
- Sort results by match score descending

**Deduplication:** Hash key = `f"{job_title}_{company_name}"` to remove duplicates across platforms.

**Trade-offs:**
- **Pro:** Comprehensive job coverage, smart matching, single search UX
- **Con:** Scrapers break when platforms update HTML (mitigated by modular design for easy fixes)

### Glassmorphism + Palestine Palette Design System

**Architecture Decision:** CSS-based design system with custom properties and animations, no UI framework.

**Rationale:**
- Unique brand identity (Palestine colors symbolize hope, peace, growth)
- Glassmorphism creates depth and modernity without heavy images
- Custom cursor and starfield effects = "living design" emotional connection
- Zero framework bloat (faster page loads)

**Implementation:**
```css
:root {
    --palestine-red: #E53E3E;
    --turquoise: #00F0FF;
    --green: #00FF88;
    --dark-bg: #0A0E27;
    --card-bg: rgba(255, 255, 255, 0.02);
}

.glass {
    background: var(--card-bg);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
}
```

**Animations:**
- Logo pulse: 3-circle logo breathing effect (2s duration)
- Custom cursor: Follows mouse with turquoise ring, scales on click
- Starfield: CSS-only animated stars background (no canvas for performance)
- Neon glow: Text-shadow on buttons/headings for sci-fi aesthetic

**Trade-offs:**
- **Pro:** Unique brand, memorable UX, fast rendering
- **Con:** Custom design requires manual responsive breakpoints (no Bootstrap grid)

### Internationalization (i18n) System

**Architecture Decision:** Python dictionary-based translations with template injection.

**Rationale:**
- Support French market (primary) and international users (English)
- Simple key-value system avoids external i18n library overhead
- Language toggle in navbar without page reload (via session)

**Implementation:**
```python
# config/translations.py
TRANSLATIONS = {
    'en': {'welcome': 'Welcome', ...},
    'fr': {'welcome': 'Bienvenue', ...}
}

# Template usage
{{ t.welcome }}  # Outputs "Welcome" or "Bienvenue"
```

**Trade-offs:**
- **Pro:** Zero dependencies, easy to add languages, template-friendly
- **Con:** Manual translation updates (acceptable for MVP with limited strings)

## External Dependencies

### AI & Machine Learning Services

**Ollama (Local AI Server):**
- **Purpose:** CV parsing with Qwen2 model (runs locally on user's machine or server)
- **Integration:** Python `ollama` library via HTTP API (default: `http://localhost:11434`)
- **Configuration:** `OLLAMA_MODEL=qwen2:latest`, `OLLAMA_URL` in `.env`
- **Data Flow:** User uploads CV → Extract text → Send to Ollama → Receive JSON with skills, experience, education
- **Requirement:** Ollama must be installed and running (documented in README quick start)

**Anthropic Claude (Cloud AI):**
- **Purpose:** Zby AI consultant for empathetic career advice and conversation
- **Integration:** Python `anthropic` library with API key
- **Configuration:** `ANTHROPIC_API_KEY` in `.env` (optional)
- **Data Flow:** User message → Send to Claude with conversation history → Stream response back
- **Fallback:** If unavailable, use Ollama for consultant (degraded but functional)

### Web Scraping & Automation

**Selenium + WebDriver:**
- **Purpose:** Auto-apply to jobs across platforms (LinkedIn, Indeed, Glassdoor)
- **Integration:** Python `selenium` library with `webdriver-manager` for Chrome
- **Configuration:** Runs in headful mode (browser visible) for CAPTCHA handling
- **Session Persistence:** Cookies saved to `data/sessions/` for resume after CAPTCHA

**BeautifulSoup4 + Requests:**
- **Purpose:** Job scraping from French platforms (Indeed FR, Welcome to the Jungle, Apec, JobTeaser)
- **Integration:** `beautifulsoup4` for HTML parsing, `requests` for HTTP
- **Rate Limiting:** Random delays between requests (1-3s) to avoid IP bans

### Payment Processing

**Stripe (Ready for Integration):**
- **Purpose:** €5/month subscriptions and credit purchases
- **Integration:** Python `stripe` library (configured but not active in MVP)
- **Configuration:** `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY` in `.env`
- **Status:** Placeholder endpoints exist in `app.py`, awaiting business activation

### Monitoring & Error Tracking

**Sentry (Optional):**
- **Purpose:** Real-time error tracking and performance monitoring
- **Integration:** Python `sentry-sdk` with Flask integration
- **Configuration:** `SENTRY_DSN` in `.env`
- **Status:** Initialized in `app.py`, sends exceptions automatically when configured

### Document Processing

**PyPDF2 + python-docx + pdfplumber:**
- **Purpose:** Extract text from uploaded CV files (PDF, DOCX)
- **Integration:** Used in `src/cv_parser.py`
- **Flow:** File upload → Detect format → Extract text → Send to Ollama for parsing

**python-docx (Letter Generation):**
- **Purpose:** Create downloadable DOCX cover letters
- **Integration:** Used in `src/letter_generator.py`
- **Output:** Formatted cover letter with user's name, date, company details

### Security & Authentication

**passlib (bcrypt):**
- **Purpose:** Password hashing for user authentication
- **Integration:** `passlib.hash.bcrypt` in `src/profile_manager.py`
- **Security:** Passwords truncated to 72 bytes before hashing (bcrypt limit)

**cryptography (Fernet):**
- **Purpose:** Encrypt stored credentials for job platforms (LinkedIn, Indeed passwords)
- **Integration:** Used in `src/profile_manager.py` for platform connections
- **Configuration:** `ENCRYPTION_KEY` in `.env` (auto-generated if missing)

### Web Framework & Utilities

**Flask 3.0:**
- **Purpose:** Web server, routing, templating
- **Integration:** Core application framework in `app.py`
- **Extensions:** Flask-CORS for API endpoints

**Gunicorn:**
- **Purpose:** Production WSGI server
- **Integration:** Deployment via `gunicorn app:app`
- **Configuration:** Recommended 4 workers for production

**python-dotenv:**
- **Purpose:** Load environment variables from `.env` file
- **Integration:** `load_dotenv()` in `app.py`
- **Required Variables:** `SECRET_KEY`, `OLLAMA_MODEL`, `OLLAMA_URL`, `ANTHROPIC_API_KEY` (optional)

### Data Storage

**File System (JSON):**
- **Location:** `data/users.json` for user profiles
- **Backup Strategy:** Manual copies or Git commits (for MVP)
- **Migration Path:** PostgreSQL schema ready (structure matches relational design)

**Session Storage:**
- **Location:** `data/sessions/` for Selenium browser sessions
- **Format:** Pickled cookie jars per user/platform
- **Cleanup:** Manual deletion after successful apply

### Job Platform APIs (Indirect)

**Note:** No official APIs are used. All job data is scraped via:
- **French Platforms:** BeautifulSoup parsing of HTML/RSS feeds
- **International Platforms:** Selenium automation for search/apply
- **Limitation:** Subject to platform HTML changes (requires maintenance)