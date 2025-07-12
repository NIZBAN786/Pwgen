#!/usr/bin/env python
"""
Entry point to run the Password Strength Analyzer and Wordlist Generator Telegram Bot.

Usage:
    python run.py
"""
import logging
import asyncio
from bot.main import main

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting Password Tool Bot...")
        # In python-telegram-bot v20+, main() doesn't need to be awaited
        # as application.run_polling() handles the event loop
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Error starting bot: {e}", exc_info=True) 