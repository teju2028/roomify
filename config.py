import os
from pathlib import Path

# MongoDB Configuration
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "roommate_finder"

# Collections
USERS_COLLECTION = "users"
REQUESTS_COLLECTION = "roommate_requests"
QUESTIONS_COLLECTION = "questions"

# Application Settings
APP_NAME = "Roomify"
AUTH_TOKEN = "dk_prod_XHG9DC6V4EMCB2J8X6GJA01AFJMS"
LOGOUT_BUTTON_NAME = "Logout"
LOTTIE_URL = "https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json"

# Email Settings
EMAIL_FROM = os.environ.get("EMAIL_FROM", "nakulchamariya373@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "gnhcjjvsjznxvodv")

APP_URL = "http://localhost:8501"

# File paths
ROOT_DIR = Path(__file__).parent
SECRET_AUTH_PATH = ROOT_DIR / "_secret_auth_.json"

# Matching Settings
TOP_MATCHES = 5
SIMILARITY_THRESHOLD = 0.3

# Predefined questions for roommate matching
ROOMMATE_QUESTIONS = [
    "What time do you usually go to bed?",
    "How often do you have guests over?",
    "Are you okay with pets in the apartment?",
    "Do you smoke?",
    "How would you describe your cleanliness habits?",
    "What is your typical noise level?",
    "How often do you cook at home?",
    "Do you work from home?",
    "How do you feel about sharing groceries and household items?",
    "What are your hobbies and interests?"
]

# Required user profile fields
REQUIRED_PROFILE_FIELDS = [
    "full_name", 
    "age",
    "gender",
    "occupation",
    "bio",
    "contact_email",
    "phone_number",
    "max_budget"
]

# CSS for UI
CSS = """
<style>
.welcome-box {
    background-color: #000000;
    color: #ffffff;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    text-align: center;
    border-left: 5px solid #4682b4;
}

.section-header {
    background-color: #4682b4;
    color: white;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 10px;
    font-size: 18px;
    font-weight: bold;
}

.match-card {
    background-color: #f9f9f9;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
    border: 1px solid #ddd;
    transition: all 0.3s ease;
}

.match-card:hover {
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}

.request-card {
    background-color: #fff8dc;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 15px;
    border-left: 4px solid #ffd700;
}

.profile-pic {
    border-radius: 50%;
    border: 3px solid #4682b4;
}

.btn-custom {
    background-color: #4682b4;
    color: white;
    border-radius: 5px;
    padding: 8px 16px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border: none;
    transition: all 0.3s ease;
}

.btn-custom:hover {
    background-color: #36648b;
}

.btn-danger {
    background-color: #dc3545;
    color: white;
}

.btn-success {
    background-color: #28a745;
    color: white;
}

.progress-container {
    margin: 20px 0;
}

.alert-info {
    background-color: #e7f5fe;
    color: #0c5460;
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #bee5eb;
}

.alert-success {
    background-color: #d4edda;
    color: #155724;
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #c3e6cb;
}

.alert-warning {
    background-color: #fff3cd;
    color: #856404;
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #ffeeba;
}
</style>
"""