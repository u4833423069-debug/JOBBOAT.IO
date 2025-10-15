"""
Multi-language translations
"""

TRANSLATIONS = {
    'en': {
        'welcome': 'Welcome',
        'dashboard': 'Dashboard',
        'upload_cv': 'Upload CV',
        'job_search': 'Job Search',
        'applications': 'My Applications',
        'activity': 'Activity',
        'my_consultant': 'My Consultant',
        'letter_generator': 'Cover Letter Generator',
        'login': 'Login',
        'register': 'Register',
        'logout': 'Logout',
        'email': 'Email',
        'password': 'Password',
        'username': 'Username',
        'location': 'Location',
        'experience_years': 'Years of Experience',
        'tagline': 'Your AI-Powered Career Assistant',
        'try_demo': 'Try Demo',
        'consultant_subtitle': 'Your AI Career Consultant',
        'zby_greeting': 'Hello! I\'m Zby, your AI career consultant. How can I help you today?'
    },
    'fr': {
        'welcome': 'Bienvenue',
        'dashboard': 'Tableau de bord',
        'upload_cv': 'Télécharger CV',
        'job_search': 'Recherche d\'emploi',
        'applications': 'Mes candidatures',
        'activity': 'Activité',
        'my_consultant': 'Mon consultant',
        'letter_generator': 'Générateur de lettre',
        'login': 'Connexion',
        'register': 'S\'inscrire',
        'logout': 'Déconnexion',
        'email': 'Email',
        'password': 'Mot de passe',
        'username': 'Nom d\'utilisateur',
        'location': 'Localisation',
        'experience_years': 'Années d\'expérience',
        'tagline': 'Votre assistant de carrière IA',
        'try_demo': 'Essayer la démo',
        'consultant_subtitle': 'Votre consultant IA',
        'zby_greeting': 'Bonjour! Je suis Zby, votre consultant de carrière IA. Comment puis-je vous aider?'
    }
}

def get_translation(lang: str = 'en'):
    """Get translations for language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['en'])
