import random
import string
import logging

# Set up logger
logger = logging.getLogger(__name__)

class PasswordGenerator:
    """Class for generating strong random passwords with customizable parameters."""
    
    @staticmethod
    def generate_password(length=16, 
                         use_lowercase=True,
                         use_uppercase=True,
                         use_digits=True,
                         use_special=True,
                         avoid_ambiguous=False,
                         min_of_each=1):
        """
        Generate a strong random password.
        
        Args:
            length (int): Length of the password to generate
            use_lowercase (bool): Whether to include lowercase letters
            use_uppercase (bool): Whether to include uppercase letters
            use_digits (bool): Whether to include digits
            use_special (bool): Whether to include special characters
            avoid_ambiguous (bool): Whether to avoid ambiguous characters (like 1/l/I, 0/O, etc.)
            min_of_each (int): Minimum number of characters from each selected character set
            
        Returns:
            str: The generated password
        """
        # Validate inputs
        if length < 4:
            raise ValueError("Password length must be at least 4 characters")
        
        # Character sets
        lowercase_chars = string.ascii_lowercase
        uppercase_chars = string.ascii_uppercase
        digit_chars = string.digits
        special_chars = "!@#$%^&*()-_=+[]{}|;:,.<>?/~"
        
        # Remove ambiguous characters if requested
        if avoid_ambiguous:
            ambiguous = "1lI0O"
            lowercase_chars = ''.join(c for c in lowercase_chars if c not in ambiguous)
            uppercase_chars = ''.join(c for c in uppercase_chars if c not in ambiguous)
            digit_chars = ''.join(c for c in digit_chars if c not in ambiguous)
        
        # Determine which character sets to use
        char_sets = []
        min_chars_needed = 0
        
        if use_lowercase:
            char_sets.append(lowercase_chars)
            min_chars_needed += min_of_each
        if use_uppercase:
            char_sets.append(uppercase_chars)
            min_chars_needed += min_of_each
        if use_digits:
            char_sets.append(digit_chars)
            min_chars_needed += min_of_each
        if use_special:
            char_sets.append(special_chars)
            min_chars_needed += min_of_each
        
        # If no character sets selected, use lowercase as default
        if not char_sets:
            char_sets.append(lowercase_chars)
            min_chars_needed = min_of_each
        
        # Check if password length is sufficient for minimum requirements
        if length < min_chars_needed:
            raise ValueError(f"Password length ({length}) is too short for the minimum character requirements ({min_chars_needed})")
        
        # Start with minimum required characters from each set
        password = []
        for char_set in char_sets:
            password.extend(random.choices(char_set, k=min_of_each))
        
        # Fill the rest of the password with random characters from all sets
        all_chars = ''.join(char_sets)
        password.extend(random.choices(all_chars, k=length - len(password)))
        
        # Shuffle the password characters
        random.shuffle(password)
        
        # Convert list to string
        password_str = ''.join(password)
        
        logger.info(f"Generated password of length {length} with specified parameters")
        
        return password_str

    @staticmethod
    def generate_passphrase(num_words=4, separator="-", capitalize=False, append_number=False):
        """
        Generate a memorable passphrase using common words.
        
        Args:
            num_words (int): Number of words in the passphrase
            separator (str): Character to use between words
            capitalize (bool): Whether to capitalize the first letter of each word
            append_number (bool): Whether to append a random number at the end
            
        Returns:
            str: The generated passphrase
        """
        # List of common, easy-to-remember words
        common_words = [
            "apple", "banana", "orange", "grape", "melon", "cherry", "peach", "lemon", "lime", "plum",
            "ocean", "river", "mountain", "forest", "desert", "valley", "cliff", "lake", "island", "beach",
            "happy", "sunny", "rainy", "cloudy", "windy", "snowy", "foggy", "stormy", "calm", "warm",
            "dog", "cat", "bird", "fish", "rabbit", "horse", "tiger", "lion", "bear", "wolf",
            "red", "blue", "green", "yellow", "purple", "orange", "black", "white", "pink", "brown",
            "book", "pen", "chair", "table", "phone", "lamp", "door", "window", "wall", "floor",
            "run", "jump", "swim", "walk", "dance", "sing", "read", "write", "talk", "listen",
            "pizza", "pasta", "salad", "soup", "bread", "cheese", "meat", "fruit", "cake", "cookie"
        ]
        
        # Select random words
        selected_words = random.sample(common_words, num_words)
        
        # Apply capitalization if requested
        if capitalize:
            selected_words = [word.capitalize() for word in selected_words]
        
        # Join words with separator
        passphrase = separator.join(selected_words)
        
        # Append random number if requested
        if append_number:
            random_number = random.randint(100, 999)
            passphrase = f"{passphrase}{separator}{random_number}"
        
        logger.info(f"Generated passphrase with {num_words} words")
        
        return passphrase

    @staticmethod
    def generate_pin(length=4, avoid_patterns=True):
        """
        Generate a random PIN.
        
        Args:
            length (int): Length of the PIN
            avoid_patterns (bool): Whether to avoid common patterns like 1234, repeated digits, etc.
            
        Returns:
            str: The generated PIN
        """
        if length < 3 or length > 12:
            raise ValueError("PIN length must be between 3 and 12 digits")
            
        while True:
            # Generate a random PIN
            pin = ''.join(random.choices(string.digits, k=length))
            
            # If we don't need to avoid patterns, return immediately
            if not avoid_patterns:
                return pin
                
            # Check for sequential digits (like "1234", "9876")
            sequential = False
            for i in range(len(pin) - 2):
                if (int(pin[i+1]) == int(pin[i]) + 1 and int(pin[i+2]) == int(pin[i]) + 2) or \
                   (int(pin[i+1]) == int(pin[i]) - 1 and int(pin[i+2]) == int(pin[i]) - 2):
                    sequential = True
                    break
                    
            # Check for repeated digits (like "1111", "2222")
            repeated = any(pin.count(digit) > length // 2 for digit in set(pin))
            
            # If no patterns found, return the PIN
            if not sequential and not repeated:
                logger.info(f"Generated PIN of length {length}")
                return pin 