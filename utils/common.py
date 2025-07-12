import datetime

def apply_leetspeak(word):
    """
    Apply leetspeak transformations to a word.
    
    Args:
        word (str): The word to transform
        
    Returns:
        list: List of leetspeak variations
    """
    leetspeak_map = {
        'a': ['4', '@'],
        'b': ['8'],
        'e': ['3'],
        'g': ['6', '9'],
        'i': ['1', '!'],
        'l': ['1'],
        'o': ['0'],
        's': ['5', '$'],
        't': ['7', '+'],
        'z': ['2']
    }
    
    variations = [word]
    
    # Apply leetspeak transformations one character at a time
    for char, replacements in leetspeak_map.items():
        current_variations = list(variations)  # Make a copy
        
        for variation in current_variations:
            if char in variation.lower():
                for replacement in replacements:
                    # Replace the character with its leetspeak equivalent
                    new_variation = variation.lower().replace(char, replacement)
                    variations.append(new_variation)
    
    # Remove duplicates and the original word
    return list(set(variations))

def append_years(word):
    """
    Append common years to a word.
    
    Args:
        word (str): The word to append years to
        
    Returns:
        list: List of variations with years appended
    """
    variations = []
    current_year = datetime.datetime.now().year
    
    # Common years: last 30 years and next 5 years
    years = list(range(current_year - 30, current_year + 6))
    
    # Also add common two-digit year formats
    two_digit_years = [str(year)[-2:] for year in years]
    
    # Generate variations with full years
    for year in years:
        variations.append(f"{word}{year}")
    
    # Generate variations with two-digit years
    for year in two_digit_years:
        variations.append(f"{word}{year}")
    
    # Also include common year patterns
    for pattern in ["123", "1234", "12345", "123456"]:
        variations.append(f"{word}{pattern}")
    
    return variations

def create_case_variations(word):
    """
    Create variations of a word with different casing.
    
    Args:
        word (str): The word to create case variations for
        
    Returns:
        list: List of case variations
    """
    variations = []
    
    # Skip if the word doesn't have alphabetic characters
    if not any(c.isalpha() for c in word):
        return [word]
    
    # Original word
    variations.append(word)
    
    # All lowercase
    variations.append(word.lower())
    
    # All uppercase
    variations.append(word.upper())
    
    # Capitalize first letter
    variations.append(word.capitalize())
    
    # Capitalize each word
    if ' ' in word:
        variations.append(word.title())
    
    # Remove duplicates
    return list(set(variations))

def append_special_chars(word):
    """
    Append common special characters to a word.
    
    Args:
        word (str): The word to append special characters to
        
    Returns:
        list: List of variations with special characters appended
    """
    variations = []
    special_chars = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '+', '=', '.', ',', '?']
    
    # Append single special characters
    for char in special_chars:
        variations.append(f"{word}{char}")
    
    # Append common combinations of special characters
    common_combinations = ['!@', '!@#', '123', '123!', '!123', '!!!', '###']
    for combo in common_combinations:
        variations.append(f"{word}{combo}")
    
    return variations
