import zxcvbn
import hashlib
import base64
import logging

# Set up logger
logger = logging.getLogger(__name__)

def analyze_password(password):
    """
    Analyze the strength of a password using zxcvbn.
    
    Args:
        password (str): The password to analyze
        
    Returns:
        dict: A dictionary containing analysis results including:
            - score: Integer from 0 (weak) to 4 (strong)
            - crack_time: Estimated time to crack the password
            - feedback: Dictionary with warnings and suggestions
    """
    if not password:
        return {
            "score": 0,
            "crack_time": "Instant",
            "feedback": {
                "warning": "Empty password",
                "suggestions": ["Please enter a password to analyze"]
            }
        }
    
    result = zxcvbn.zxcvbn(password)
    
    # Extract relevant information
    analysis = {
        "score": result["score"],  # 0-4 (0 = weak, 4 = strong)
        "crack_time": result["crack_times_display"]["offline_slow_hashing_1e4_per_second"],
        "feedback": result["feedback"]
    }
    
    return analysis

def generate_password_hashes(password):
    """
    Generate hashes of a password using various algorithms.
    
    Args:
        password (str): The password to hash
        
    Returns:
        dict: A dictionary of hashes with algorithm names as keys
    """
    if not password:
        return {}
        
    # Convert the password to bytes if it's not already
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password
    
    # Generate hashes using different algorithms
    hashes = {}
    
    # MD5 (not secure, but included for completeness)
    hashes['MD5'] = hashlib.md5(password_bytes).hexdigest()
    
    # SHA family
    hashes['SHA1'] = hashlib.sha1(password_bytes).hexdigest()
    hashes['SHA224'] = hashlib.sha224(password_bytes).hexdigest()
    hashes['SHA256'] = hashlib.sha256(password_bytes).hexdigest()
    hashes['SHA384'] = hashlib.sha384(password_bytes).hexdigest()
    hashes['SHA512'] = hashlib.sha512(password_bytes).hexdigest()
    
    # Blake2
    hashes['BLAKE2b'] = hashlib.blake2b(password_bytes).hexdigest()
    hashes['BLAKE2s'] = hashlib.blake2s(password_bytes).hexdigest()
    
    logger.info(f"Generated {len(hashes)} different hashes for password")
    
    return hashes

def get_strength_description(score):
    """
    Get a human-readable description of password strength based on score.
    
    Args:
        score (int): The score from zxcvbn (0-4)
        
    Returns:
        str: A description of the password strength
    """
    descriptions = {
        0: "Very Weak - Easily cracked",
        1: "Weak - Vulnerable to basic attacks",
        2: "Medium - Could be stronger",
        3: "Strong - Good password",
        4: "Very Strong - Excellent password"
    }
    
    return descriptions.get(score, "Unknown strength")

def format_analysis_for_telegram(analysis, include_hashes=True, password=None):
    """
    Format password analysis results for readable display in Telegram.
    
    Args:
        analysis (dict): The analysis result from analyze_password
        include_hashes (bool): Whether to include password hashes in the output
        password (str, optional): The password to generate hashes for
        
    Returns:
        str: Formatted text for Telegram message
    """
    score = analysis["score"]
    crack_time = analysis["crack_time"]
    feedback = analysis["feedback"]
    
    strength_desc = get_strength_description(score)
    
    # Build the response message
    message = f"📊 *Password Strength Analysis*\n\n"
    message += f"*Strength*: {strength_desc} ({score}/4)\n"
    message += f"*Est. Time to Crack*: {crack_time}\n\n"
    
    # Add warnings if present
    if feedback["warning"]:
        message += f"⚠️ *Warning*: {feedback['warning']}\n\n"
    
    # Add suggestions if present
    if feedback["suggestions"]:
        message += "*Suggestions*:\n"
        for suggestion in feedback["suggestions"]:
            message += f"• {suggestion}\n"
    
    # Add password hashes if requested and password is provided
    if include_hashes and password:
        try:
            hashes = generate_password_hashes(password)
            if hashes:
                message += "\n💾 *Password Hashes*:\n"
                # Add common hashes first
                for algo in ['MD5', 'SHA1', 'SHA256']:
                    if algo in hashes:
                        message += f"*{algo}*: `{hashes[algo]}`\n"
                
                # Add a separator before additional hashes
                message += "\n*Additional Hash Algorithms*:\n"
                for algo, hash_value in hashes.items():
                    if algo not in ['MD5', 'SHA1', 'SHA256']:
                        message += f"*{algo}*: `{hash_value}`\n"
        except Exception as e:
            logger.error(f"Error generating password hashes: {str(e)}")
    
    return message
