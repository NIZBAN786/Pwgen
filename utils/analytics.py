import logging
import json
import asyncio
import datetime
import httpx
import os
from telegram import Bot, Update
from config import (
    ANALYTICS_BOT_TOKEN, 
    ANALYTICS_CHAT_ID, 
    ENABLE_ANALYTICS,
    USER_BOT_NAME,
    TEMP_DIR
)

logger = logging.getLogger(__name__)

class AnalyticsCollector:
    def __init__(self):
        self.analytics_bot = None
        self.enabled = ENABLE_ANALYTICS
        self.chat_id_validated = False
        
        if not ANALYTICS_CHAT_ID or ANALYTICS_CHAT_ID == "YOUR_CHAT_ID":
            logger.warning("Analytics chat ID not configured. Analytics will be disabled.")
            self.enabled = False
            return
            
        if self.enabled:
            try:
                self.analytics_bot = Bot(token=ANALYTICS_BOT_TOKEN)
                logger.info("Analytics collector initialized")
            except Exception as e:
                logger.error(f"Error initializing analytics bot: {str(e)}")
                self.enabled = False
    
    async def _validate_chat_id(self):
        """
        Validate that the chat ID is correct by attempting to send a test message.
        This is only called once.
        """
        if not self.enabled or self.chat_id_validated:
            return True
            
        try:
            # Try to send a simple message to verify the chat ID
            await self.analytics_bot.send_message(
                chat_id=ANALYTICS_CHAT_ID, 
                text="*Analytics system initialized successfully.*",
                parse_mode="Markdown"
            )
            self.chat_id_validated = True
            logger.info(f"Analytics chat ID verified: {ANALYTICS_CHAT_ID}")
            return True
        except Exception as e:
            logger.error(f"Invalid analytics chat ID: {str(e)}")
            self.enabled = False  # Disable analytics if chat ID is invalid
            self.chat_id_validated = False
            return False
    
    async def send_analytics_event(self, event_type, data=None, user_id=None, user_info=None):
        """
        Send analytics event to the analytics bot.
        
        Args:
            event_type (str): Type of event (e.g., 'password_analysis', 'wordlist_generation')
            data (dict, optional): Event data
            user_id (int, optional): User ID
            user_info (dict, optional): Additional user information
        """
        if not self.enabled or not self.analytics_bot:
            logger.debug("Analytics disabled or bot not initialized")
            return
        
        # Validate chat ID on first use
        if not self.chat_id_validated:
            chat_valid = await self._validate_chat_id()
            if not chat_valid:
                logger.warning("Skipping analytics event due to invalid chat ID")
                return
            
        try:
            # Create timestamp
            timestamp = datetime.datetime.now().isoformat()
            
            # Prepare data for markdown formatting
            md_content = f"# Analytics Event: {event_type}\n\n"
            md_content += f"**Timestamp:** {timestamp}\n"
            md_content += f"**Source:** {USER_BOT_NAME}\n"
            
            # Include user information
            if user_id:
                md_content += f"**User ID:** {user_id}\n"
            
            # Format user_info as a table if available
            if user_info and isinstance(user_info, dict):
                md_content += "\n## User Information\n\n"
                for key, value in user_info.items():
                    md_content += f"**{key}:** {value}\n"
            
            # Format event data as a table if available
            if data and isinstance(data, dict):
                md_content += "\n## Event Data\n\n"
                for key, value in data.items():
                    if isinstance(value, list):
                        md_content += f"**{key}:**\n"
                        for item in value:
                            md_content += f"- {item}\n"
                    else:
                        md_content += f"**{key}:** {value}\n"
            
            # Generate a filename with timestamp for the .md file
            timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp_str}_{event_type}.md"
            filepath = os.path.join(TEMP_DIR, filename)
            
            # Ensure the temp directory exists
            os.makedirs(TEMP_DIR, exist_ok=True)
            
            # Save content to a temporary file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            # Send the file as a document
            with open(filepath, 'rb') as doc:
                await self.analytics_bot.send_document(
                    chat_id=ANALYTICS_CHAT_ID,
                    document=doc,
                    filename=filename,
                    caption=f"Analytics: {event_type} event from {USER_BOT_NAME}"
                )
            
            # Delete the temporary file
            try:
                os.remove(filepath)
            except Exception as e:
                logger.warning(f"Could not delete temporary file {filepath}: {str(e)}")
                
            logger.debug(f"Analytics event sent as markdown document: {event_type}")
        except Exception as e:
            logger.error(f"Error sending analytics: {str(e)}")
            # Disable analytics if there's a persistent error
            if "chat not found" in str(e).lower() or "chat_id is empty" in str(e).lower():
                logger.warning("Disabling analytics due to invalid chat ID")
                self.enabled = False
    
    def _sanitize_data(self, data):
        """
        Sanitize data to ensure no sensitive information is included.
        
        Args:
            data (dict): Data to sanitize
            
        Returns:
            dict: Sanitized data
        """
        # For educational purposes, we're not sanitizing the data
        # WARNING: In a production environment, you should sanitize sensitive data
        return data

# Create a singleton instance
analytics = AnalyticsCollector()

# Helper functions for common analytics events
async def log_password_analysis(user_id, score, warnings_count):
    """Log a password analysis event with user data."""
    try:
        # Get user info if available through the update object
        user_info = None
        
        await analytics.send_analytics_event(
            event_type="password_analysis",
            data={
                "score": score,
                "warnings_count": warnings_count,
            },
            user_id=user_id,
            user_info=user_info
        )
    except Exception as e:
        # Never let analytics failures affect the main app
        logger.error(f"Error in log_password_analysis: {str(e)}")

async def log_hash_generation(user_id, hash_types=None):
    """Log a hash generation event."""
    try:
        await analytics.send_analytics_event(
            event_type="hash_generation",
            data={
                "hash_algorithms": hash_types or [],
            },
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Error in log_hash_generation: {str(e)}")

async def log_wordlist_generation(user_id, wordlist_size, categories_provided=None):
    """Log a wordlist generation event."""
    try:
        await analytics.send_analytics_event(
            event_type="wordlist_generation",
            data={
                "wordlist_size": wordlist_size,
                "categories_provided": categories_provided or [],
            },
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Error in log_wordlist_generation: {str(e)}")

async def log_bot_start(user_id, user_info=None):
    """Log a bot start event."""
    try:
        await analytics.send_analytics_event(
            event_type="bot_start",
            user_id=user_id,
            user_info=user_info
        )
    except Exception as e:
        logger.error(f"Error in log_bot_start: {str(e)}")

async def log_password_generation(user_id, password_type, length, options=None):
    """Log a password generation event."""
    try:
        await analytics.send_analytics_event(
            event_type="password_generation",
            data={
                "password_type": password_type,
                "length": length,
                "options": options or {},
            },
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Error in log_password_generation: {str(e)}")

async def log_error(user_id, command, error_type):
    """Log an error event."""
    try:
        await analytics.send_analytics_event(
            event_type="error",
            data={
                "command": command,
                "error_type": error_type,
            },
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Error in log_error: {str(e)}") 