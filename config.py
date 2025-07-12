import os
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
load_dotenv()

# Telegram Bot Configuration
# Get your token from https://t.me/BotFather
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    print("\n⚠️  WARNING: Telegram Bot Token not found!")
    print("Please set your TELEGRAM_BOT_TOKEN environment variable or add it to a .env file.")
    print("You can get a token from https://t.me/BotFather\n")
    # Default to a placeholder for development
    TELEGRAM_BOT_TOKEN = "8161365371:AAFt3ite1QZWXfrMICnslLs57Osg3Gt622s"

# Analytics Bot Configuration
ANALYTICS_BOT_TOKEN = os.getenv("ANALYTICS_BOT_TOKEN")
ANALYTICS_CHAT_ID = os.getenv("ANALYTICS_CHAT_ID")
if ANALYTICS_BOT_TOKEN:
    logger.info("Analytics bot token found. Analytics will be enabled.")
else:
    logger.warning("Analytics bot token not found. Analytics will be disabled.")

# Analytics settings
ENABLE_ANALYTICS = bool(ANALYTICS_BOT_TOKEN and ANALYTICS_CHAT_ID)
USER_BOT_NAME = os.getenv("USER_BOT_NAME", "Pwgen")
ANALYTICS_BOT_NAME = os.getenv("ANALYTICS_BOT_NAME", "Pwgen Data Store")

# Wordlist Generator Configuration
MIN_WORD_LENGTH = 4
MAX_WORDLIST_SIZE = 100000  # Limit the size of generated wordlists for safety

# Temporary file storage
TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "temp")
logger.info(f"Setting temporary directory to: {TEMP_DIR}")

# Create temp directory if it doesn't exist
try:
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR, exist_ok=True)
        logger.info(f"Created temporary directory: {TEMP_DIR}")
    
    # Test write permissions
    test_file = os.path.join(TEMP_DIR, "test_write.txt")
    with open(test_file, 'w') as f:
        f.write("Test write permissions")
    
    # Clean up test file
    if os.path.exists(test_file):
        os.remove(test_file)
        logger.info("Write permissions confirmed for temporary directory")
except Exception as e:
    logger.error(f"Error setting up temporary directory: {str(e)}")
    # Fall back to current directory
    TEMP_DIR = "temp"
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR, exist_ok=True)
    logger.info(f"Falling back to local temp directory: {TEMP_DIR}")
