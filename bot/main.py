import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

from config import TELEGRAM_BOT_TOKEN
from bot.handlers import (
    start,
    analyze_cmd,
    help_cmd,
    hash_cmd,
    generate_password_cmd,
    start_generation,
    process_name,
    process_birthdate,
    process_pets,
    process_places,
    process_hobbies,
    process_additional_and_generate,
    cancel_generation,
    error_handler,
    WAITING_FOR_NAME,
    WAITING_FOR_BIRTHDATE,
    WAITING_FOR_PETS,
    WAITING_FOR_PLACES,
    WAITING_FOR_HOBBIES,
    WAITING_FOR_ADDITIONAL,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register basic command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("analyze", analyze_cmd))
    application.add_handler(CommandHandler("hash", hash_cmd))
    application.add_handler(CommandHandler("generate_password", generate_password_cmd))

    # Set up the ConversationHandler for wordlist generation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("generate", start_generation)],
        states={
            WAITING_FOR_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_name)],
            WAITING_FOR_BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_birthdate)],
            WAITING_FOR_PETS: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_pets)],
            WAITING_FOR_PLACES: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_places)],
            WAITING_FOR_HOBBIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_hobbies)],
            WAITING_FOR_ADDITIONAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_additional_and_generate)],
        },
        fallbacks=[CommandHandler("cancel", cancel_generation)],
    )
    application.add_handler(conv_handler)

    # Log all errors
    application.add_error_handler(error_handler)

    # Log that we're about to start
    logger.info("Bot started. Press Ctrl+C to stop.")
    
    # Start the Bot - this will block until the bot is stopped
    application.run_polling()

if __name__ == "__main__":
    main()
