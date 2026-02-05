"""
Frontend Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")

# App Settings
APP_TITLE = "Assignment Platform"
