#!/usr/bin/env python
"""
Entry point to run the Password Strength Analyzer and Wordlist Generator Telegram Bot.

Usage:
    python run.py
"""
import logging
import threading
from bot.main import main
from app import run_flask

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting Password Tool Bot and Flask App...")
        
        # Start Flask app in a separate thread
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        logger.info("Flask app started on http://0.0.0.0:5000")
        
        # Start the Telegram bot in the main thread
        logger.info("Starting Telegram bot...")
        main()
    except KeyboardInterrupt:
        logger.info("Services stopped by user.")
    except Exception as e:
        logger.error(f"Error starting services: {e}", exc_info=True) 