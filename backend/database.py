"""
Supabase Database Connection
"""
import logging
from supabase import create_client, Client
from config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

try:
    logger.info(f"Connecting to Supabase at {settings.SUPABASE_URL}")
    supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    raise


def get_db() -> Client:
    """Get Supabase client instance"""
    return supabase
