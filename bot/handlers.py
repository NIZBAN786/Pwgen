import os
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler
import datetime

from core.pwgen_analyser import analyze_password, format_analysis_for_telegram, generate_password_hashes, get_strength_description
from core.wordlist_gen import WordlistGenerator
from core.password_gen import PasswordGenerator
from config import TEMP_DIR
from utils.analytics import (
    log_password_analysis,
    log_hash_generation,
    log_wordlist_generation,
    log_bot_start,
    log_error,
    log_password_generation
)

# Define conversation states
(
    WAITING_FOR_NAME,
    WAITING_FOR_BIRTHDATE,
    WAITING_FOR_PETS,
    WAITING_FOR_PLACES,
    WAITING_FOR_HOBBIES,
    WAITING_FOR_ADDITIONAL,
) = range(6)

# Store user data temporarily
user_data_store = {}

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    if not update or not update.message:
        logger.error("Received update with no message in start")
        return
        
    user = update.effective_user
    if not user:
        logger.error("Received update with no effective_user in start")
        return
        
    message = (
        f"Hi {user.first_name}! I'm a Password Tool Bot.\n\n"
        "Here's what I can do:\n"
        "- /analyze <password> - Analyze the strength of a password\n"
        "- /hash <password> - Generate hashes of a password in various algorithms\n"
        "- /generate - Generate a custom wordlist based on personal information\n"
        "- /generate_password - Create a strong random password\n\n"
        "Please note: Your data is used ONLY for generating the wordlist and "
        "is never stored or shared."
    )
    await update.message.reply_text(message)
    
    # Log bot start for analytics
    try:
        # Collect user information for educational purposes only
        # WARNING: In a production environment, you should NOT collect this data
        user_info = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "language_code": user.language_code,
            "is_premium": user.is_premium,
            "chat_id": update.message.chat_id,
            "chat_type": update.message.chat.type
        }
        
        # Remove None values
        user_info = {k: v for k, v in user_info.items() if v is not None}
        
        await log_bot_start(user.id, user_info)
    except Exception as e:
        logger.error(f"Error logging bot start: {str(e)}")

async def analyze_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Analyze a password when the command /analyze is issued."""
    # Check if update.message exists first (it might be None)
    if not update or not update.message:
        logger.error("Received update with no message in analyze_cmd")
        return
        
    # Check if password was provided
    if not context.args:
        await update.message.reply_text(
            "Please provide a password to analyze.\n"
            "Usage: /analyze <password>"
        )
        return
    
    try:
        # Get password from command arguments
        password = ' '.join(context.args)
        
        # Analyze the password
        analysis = analyze_password(password)
        
        # Format and send the analysis with hashes
        formatted_analysis = format_analysis_for_telegram(analysis, include_hashes=True, password=password)
        await update.message.reply_text(
            formatted_analysis,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # For security, delete the message containing the password if possible
        try:
            await update.message.delete()
        except Exception as e:
            logger.info(f"Couldn't delete message: {e}")
            
        # Log password analysis for analytics (anonymized)
        try:
            warnings_count = len(analysis["feedback"]["suggestions"]) if analysis["feedback"]["suggestions"] else 0
            await log_password_analysis(
                user_id=update.effective_user.id,
                score=analysis["score"],
                warnings_count=warnings_count
            )
        except Exception as e:
            logger.error(f"Error logging password analysis: {str(e)}")
    except Exception as e:
        logger.error(f"Error analyzing password: {e}")
        # Only try to reply if update.message exists
        if update and update.message:
            await update.message.reply_text(
                "Sorry, there was an error analyzing your password. Please try again."
            )
        
        # Log error for analytics
        try:
            if update and update.effective_user:
                await log_error(
                    user_id=update.effective_user.id,
                    command="analyze",
                    error_type=str(type(e).__name__)
                )
        except Exception as log_error:
            logger.error(f"Error logging error: {str(log_error)}")

async def hash_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate and display hashes of a password when the command /hash is issued."""
    # Check if update.message exists first (it might be None)
    if not update or not update.message:
        logger.error("Received update with no message in hash_cmd")
        return
        
    # Check if password was provided
    if not context.args:
        await update.message.reply_text(
            "Please provide a password to hash.\n"
            "Usage: /hash <password>"
        )
        return
    
    try:
        # Get password from command arguments
        password = ' '.join(context.args)
        
        # Generate hashes
        hashes = generate_password_hashes(password)
        
        if not hashes:
            await update.message.reply_text("Could not generate hashes for the provided input.")
            return
        
        # Format the hashes for display
        message = f"💾 *Password Hashes*\n\n"
        
        # Common algorithms first
        message += "*Common Hash Algorithms:*\n"
        for algo in ['MD5', 'SHA1', 'SHA256']:
            if algo in hashes:
                message += f"*{algo}*: `{hashes[algo]}`\n"
        
        # Additional algorithms
        message += "\n*Additional Hash Algorithms:*\n"
        for algo, hash_value in hashes.items():
            if algo not in ['MD5', 'SHA1', 'SHA256']:
                message += f"*{algo}*: `{hash_value}`\n"
        
        message += "\n⚠️ *Note*: These hashes are provided for educational purposes only. Never store passwords as unsalted hashes."
        
        # Send the message
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Log hash generation for analytics
        try:
            if update and update.effective_user:
                await log_hash_generation(
                    user_id=update.effective_user.id,
                    hash_types=list(hashes.keys())
                )
        except Exception as e:
            logger.error(f"Error logging hash generation: {str(e)}")
        
        # For security, delete the message containing the password if possible
        try:
            await update.message.delete()
        except Exception as e:
            logger.info(f"Couldn't delete message: {e}")
    except Exception as e:
        logger.error(f"Error generating password hashes: {str(e)}")
        if update and update.message:
            await update.message.reply_text(
                "Sorry, there was an error generating hashes for your password. Please try again."
            )
        
        # Log error for analytics
        try:
            if update and update.effective_user:
                await log_error(
                    user_id=update.effective_user.id,
                    command="hash",
                    error_type=str(type(e).__name__)
                )
        except Exception as log_error:
            logger.error(f"Error logging error: {str(log_error)}")

async def start_generation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the wordlist generation conversation."""
    # Initialize user data
    user_id = update.effective_user.id
    user_data_store[user_id] = {'generator': WordlistGenerator()}
    
    await update.message.reply_text(
        "I'll help you generate a custom wordlist for password testing.\n\n"
        "This information will ONLY be used to generate wordlist combinations "
        "and will NOT be stored after generation.\n\n"
        "What's your name? (First and/or last name)"
    )
    
    return WAITING_FOR_NAME

async def process_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the name and ask for birthdate."""
    user_id = update.effective_user.id
    name = update.message.text
    
    user_data_store[user_id]['generator'].add_personal_info('name', name)
    
    await update.message.reply_text(
        "Thank you. Please provide your birth date or any significant dates "
        "(e.g., DDMMYYYY, MMDDYYYY, or just the year)."
    )
    
    return WAITING_FOR_BIRTHDATE

async def process_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process the birthdate and ask for pet names."""
    user_id = update.effective_user.id
    birthdate = update.message.text
    
    user_data_store[user_id]['generator'].add_personal_info('birthdate', birthdate)
    
    await update.message.reply_text(
        "Got it. Do you have any pets? If yes, please provide their names."
    )
    
    return WAITING_FOR_PETS

async def process_pets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process pet names and ask for significant places."""
    user_id = update.effective_user.id
    pets = update.message.text
    
    user_data_store[user_id]['generator'].add_personal_info('pets', pets)
    
    await update.message.reply_text(
        "Please provide any significant places (e.g., hometown, favorite city, workplace)."
    )
    
    return WAITING_FOR_PLACES

async def process_places(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process places and ask for hobbies."""
    user_id = update.effective_user.id
    places = update.message.text
    
    user_data_store[user_id]['generator'].add_personal_info('places', places)
    
    await update.message.reply_text(
        "What are your hobbies or interests?"
    )
    
    return WAITING_FOR_HOBBIES

async def process_hobbies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process hobbies and ask for additional information."""
    user_id = update.effective_user.id
    hobbies = update.message.text
    
    user_data_store[user_id]['generator'].add_personal_info('hobbies', hobbies)
    
    await update.message.reply_text(
        "Any additional information you'd like to include? "
        "(e.g., family members, favorite teams, etc.)"
    )
    
    return WAITING_FOR_ADDITIONAL

async def process_additional_and_generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process additional information and generate the wordlist."""
    user_id = update.effective_user.id
    additional = update.message.text
    
    try:
        # Get user data
        if user_id not in user_data_store:
            await update.message.reply_text(
                "Sorry, your session has expired. Please start again with /generate."
            )
            return ConversationHandler.END
            
        user_data = user_data_store[user_id]
        generator = user_data['generator']
        
        # Add final piece of information
        generator.add_personal_info('additional', additional)
        
        # Collect categories provided for analytics
        categories_provided = list(generator.personal_info.keys())
        
        # Inform user that generation has started
        await update.message.reply_text(
            "Generating your custom wordlist... This may take a moment."
        )
        
        # Generate wordlist
        try:
            wordlist = generator.generate_wordlist()
            wordlist_size = len(wordlist)
            
            if not wordlist:
                raise ValueError("Generated wordlist is empty")
                
            # Create a temporary directory if it doesn't exist
            if not os.path.exists(TEMP_DIR):
                os.makedirs(TEMP_DIR, exist_ok=True)
            
            # Generate timestamp for unique filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(TEMP_DIR, f"wordlist_{user_id}_{timestamp}.txt")
            
            logger.info(f"Creating wordlist file at: {filepath}")
            
            # Save to file
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    for word in wordlist:
                        f.write(f"{word}\n")
                
                # Make sure file exists and has content
                file_size = os.path.getsize(filepath)
                logger.info(f"Wordlist file created. Size: {file_size} bytes")
                
                if file_size == 0:
                    raise ValueError("Wordlist file is empty")
                
                # Send the file - using different approach for sending documents
                try:
                    # Simplify document sending by using message.reply_document with open file
                    with open(filepath, 'rb') as file:
                        await update.message.reply_text("Wordlist generated successfully. Sending file now...")
                        await update.message.reply_document(
                            document=file,
                            filename=f"custom_wordlist_{timestamp}.txt",
                            caption=f"Here's your custom wordlist with {len(wordlist)} entries."
                        )
                        logger.info(f"Wordlist file sent successfully to user {user_id}")
                        
                        # Log wordlist generation for analytics
                        try:
                            await log_wordlist_generation(
                                user_id=user_id,
                                wordlist_size=wordlist_size,
                                categories_provided=categories_provided
                            )
                        except Exception as e:
                            logger.error(f"Error logging wordlist generation: {str(e)}")
                except Exception as e:
                    logger.error(f"Error sending document: {str(e)}")
                    # Try an alternative approach with InputFile if available
                    try:
                        from telegram import InputFile
                        await update.message.reply_text("Retrying with alternative method...")
                        with open(filepath, 'rb') as file:
                            await update.message.reply_document(
                                document=InputFile(file),
                                filename=f"custom_wordlist_{timestamp}.txt",
                                caption=f"Here's your custom wordlist with {len(wordlist)} entries."
                            )
                            
                            # Log wordlist generation for analytics
                            try:
                                await log_wordlist_generation(
                                    user_id=user_id,
                                    wordlist_size=wordlist_size,
                                    categories_provided=categories_provided
                                )
                            except Exception as e:
                                logger.error(f"Error logging wordlist generation: {str(e)}")
                    except Exception as inner_e:
                        logger.error(f"Alternative document sending method failed: {str(inner_e)}")
                        
                        # Last resort: Send as text if wordlist is small enough
                        if len(wordlist) <= 100:
                            await update.message.reply_text("Sending wordlist as text message instead...")
                            # Split into chunks to avoid message length limits
                            chunk_size = 20
                            for i in range(0, len(wordlist), chunk_size):
                                chunk = wordlist[i:i + chunk_size]
                                message_text = f"Wordlist (part {i//chunk_size + 1}):\n\n" + "\n".join(chunk)
                                await update.message.reply_text(message_text)
                            
                            await update.message.reply_text(
                                f"Wordlist sent as text. Total entries: {len(wordlist)}"
                            )
                            
                            # Log wordlist generation for analytics
                            try:
                                await log_wordlist_generation(
                                    user_id=user_id,
                                    wordlist_size=wordlist_size,
                                    categories_provided=categories_provided
                                )
                            except Exception as e:
                                logger.error(f"Error logging wordlist generation: {str(e)}")
                        else:
                            # If wordlist is too large, inform the user
                            await update.message.reply_text(
                                "Sorry, there was an error sending your wordlist file. "
                                "The wordlist is too large to send as text. "
                                "Please try again later."
                            )
                
                # Delete the file after sending
                try:
                    os.remove(filepath)
                    logger.info(f"Deleted temporary file: {filepath}")
                except Exception as e:
                    logger.error(f"Error removing temporary file {filepath}: {str(e)}")
            except Exception as e:
                logger.error(f"Error writing wordlist to file: {str(e)}")
                await update.message.reply_text(
                    "Sorry, there was an error saving your wordlist. "
                    "Please try again later."
                )
                
                # Log error for analytics
                try:
                    await log_error(
                        user_id=user_id,
                        command="generate_file",
                        error_type=str(type(e).__name__)
                    )
                except Exception as log_error:
                    logger.error(f"Error logging error: {str(log_error)}")
        except Exception as e:
            logger.error(f"Error generating wordlist: {str(e)}")
            await update.message.reply_text(
                "Sorry, there was an error generating your wordlist. "
                "Please try again or use different information."
            )
            
            # Log error for analytics
            try:
                await log_error(
                    user_id=user_id,
                    command="generate_wordlist",
                    error_type=str(type(e).__name__)
                )
            except Exception as log_error:
                logger.error(f"Error logging error: {str(log_error)}")
    except Exception as e:
        logger.error(f"Unexpected error in wordlist generation: {str(e)}")
        await update.message.reply_text(
            "An unexpected error occurred. Please try again later."
        )
        
        # Log error for analytics
        try:
            await log_error(
                user_id=user_id,
                command="generate",
                error_type=str(type(e).__name__)
            )
        except Exception as log_error:
            logger.error(f"Error logging error: {str(log_error)}")
    finally:
        # Clean up user data
        if user_id in user_data_store:
            del user_data_store[user_id]
    
    return ConversationHandler.END

async def cancel_generation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the wordlist generation conversation."""
    user_id = update.effective_user.id
    
    # Clean up user data if exists
    if user_id in user_data_store:
        del user_data_store[user_id]
    
    await update.message.reply_text(
        "Wordlist generation cancelled. Your information has been discarded."
    )
    
    return ConversationHandler.END

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    if not update or not update.message:
        logger.error("Received update with no message in help_cmd")
        return
    
    help_text = (
        "🔒 *Password Tool Bot Help* 🔒\n\n"
        "*Available Commands:*\n\n"
        
        "🔍 */analyze <password>*\n"
        "Analyzes password strength using the zxcvbn library.\n"
        "Shows estimated crack time, warnings, and suggestions.\n\n"
        
        "📊 */hash <password>*\n"
        "Generates various hash formats for a password.\n"
        "Includes MD5, SHA1, SHA256, and more.\n\n"
        
        "📝 */generate*\n"
        "Creates a custom wordlist based on your information.\n"
        "Perfect for testing your own password security.\n\n"
        
        "🔐 */generate_password [options]*\n"
        "Creates strong random passwords with customizable options.\n"
        "Options: length=N, type=passphrase, type=pin, avoid-ambiguous, etc.\n\n"
        
        "*Security Note:*\n"
        "Your passwords and personal information are never stored."
    )
    
    await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)

async def generate_password_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Generate a strong random password when the command /generate_password is issued."""
    if not update or not update.message:
        logger.error("Received update with no message in generate_password_cmd")
        return
    
    try:
        # Default parameters
        length = 16
        use_lowercase = True
        use_uppercase = True
        use_digits = True
        use_special = True
        avoid_ambiguous = False
        password_type = "random"  # Options: random, passphrase, pin
        
        # Parse command arguments if provided
        if context.args:
            for arg in context.args:
                if arg.startswith("length="):
                    try:
                        length = int(arg.split("=")[1])
                    except (ValueError, IndexError):
                        pass
                elif arg == "no-lowercase":
                    use_lowercase = False
                elif arg == "no-uppercase":
                    use_uppercase = False
                elif arg == "no-digits":
                    use_digits = False
                elif arg == "no-special":
                    use_special = False
                elif arg == "avoid-ambiguous":
                    avoid_ambiguous = True
                elif arg == "type=passphrase":
                    password_type = "passphrase"
                elif arg == "type=pin":
                    password_type = "pin"
        
        # Generate password based on type
        password_generator = PasswordGenerator()
        
        if password_type == "random":
            password = password_generator.generate_password(
                length=length,
                use_lowercase=use_lowercase,
                use_uppercase=use_uppercase,
                use_digits=use_digits,
                use_special=use_special,
                avoid_ambiguous=avoid_ambiguous
            )
            password_description = "random password"
            
        elif password_type == "passphrase":
            num_words = min(max(length // 4, 3), 8)  # Convert length to reasonable word count
            password = password_generator.generate_passphrase(
                num_words=num_words,
                capitalize=True,
                append_number=True
            )
            password_description = f"passphrase with {num_words} words"
            
        elif password_type == "pin":
            length = min(max(length, 4), 12)  # PIN length between 4 and 12
            password = password_generator.generate_pin(
                length=length,
                avoid_patterns=True
            )
            password_description = f"{length}-digit PIN"
        
        # Analyze the generated password for strength information
        analysis = analyze_password(password)
        
        # Prepare the response message
        message = f"🔐 *Generated {password_description}*\n\n"
        message += f"`{password}`\n\n"
        message += f"*Strength*: {get_strength_description(analysis['score'])} ({analysis['score']}/4)\n"
        message += f"*Est. Time to Crack*: {analysis['crack_time']}\n\n"
        
        # Add usage information
        message += "*Usage Options:*\n"
        message += "`/generate_password` - Generate default strong password\n"
        message += "`/generate_password length=20` - Set specific length\n"
        message += "`/generate_password type=passphrase` - Generate a passphrase\n"
        message += "`/generate_password type=pin` - Generate a secure PIN\n"
        message += "`/generate_password no-special avoid-ambiguous` - Customize character sets\n"
        
        await update.message.reply_text(
            message,
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Log password generation for analytics
        try:
            if update and update.effective_user:
                # Collect options for analytics
                options = {
                    "use_lowercase": use_lowercase,
                    "use_uppercase": use_uppercase,
                    "use_digits": use_digits,
                    "use_special": use_special,
                    "avoid_ambiguous": avoid_ambiguous,
                    "strength_score": analysis['score'],
                    "crack_time": analysis['crack_time']
                }
                
                await log_password_generation(
                    user_id=update.effective_user.id,
                    password_type=password_type,
                    length=length,
                    options=options
                )
        except Exception as e:
            logger.error(f"Error logging password generation: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error generating password: {e}")
        await update.message.reply_text(
            "Sorry, there was an error generating your password. Please try again."
        )
        
        # Log error for analytics
        try:
            if update and update.effective_user:
                await log_error(
                    user_id=update.effective_user.id,
                    command="generate_password",
                    error_type=str(type(e).__name__)
                )
        except Exception as log_err:
            logger.error(f"Error logging error: {str(log_err)}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the proper async way for python-telegram-bot v20+."""
    if not context:
        logger.error("Received error with no context")
        return
        
    error_message = f"Exception while handling an update: {context.error}"
    logger.error(error_message)
    
    # Only try to send a message if we have a valid update with an effective_message
    try:
        if update and hasattr(update, 'effective_message') and update.effective_message:
            await update.effective_message.reply_text(
                "Sorry, something went wrong. Please try again later."
            )
            
            # Log error for analytics
            if hasattr(update, 'effective_user') and update.effective_user:
                try:
                    error_type = str(type(context.error).__name__) if context.error else "Unknown"
                    await log_error(
                        user_id=update.effective_user.id,
                        command="unknown",
                        error_type=error_type
                    )
                except Exception as e:
                    logger.error(f"Error logging error: {str(e)}")
    except Exception as e:
        logger.error(f"Error in error handler: {e}")
