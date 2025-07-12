import itertools
import os
import datetime
import logging
from utils.common import apply_leetspeak, append_years, create_case_variations, append_special_chars

# Set up logger
logger = logging.getLogger(__name__)

class WordlistGenerator:
    def __init__(self):
        self.personal_info = {}
        self.wordlist = set()
        self.min_length = 3  # Reduced minimum length to ensure we get some results
        
    def add_personal_info(self, category, value):
        """
        Add personal information to be used for wordlist generation.
        
        Args:
            category (str): Category of information (e.g., name, birthday, pet)
            value (str): The value for that category
        """
        if not value:
            return
            
        # Split value by spaces to handle multi-word inputs
        if isinstance(value, str):
            values = [v.strip() for v in value.split() if v.strip()]
            
            # Add the original full string
            if value.strip():
                values.append(value.strip())
                
            # Store all values for this category
            self.personal_info[category] = values
        elif isinstance(value, list):
            self.personal_info[category] = [v.strip() for v in value if v.strip()]
        
        logger.info(f"Added {len(values) if isinstance(value, str) and value.strip() else 0} items to category '{category}'")
    
    def generate_base_combinations(self):
        """
        Generate base combinations from personal information.
        """
        # Flatten all personal info into a single list
        all_words = []
        for category, values in self.personal_info.items():
            all_words.extend(values)
        
        logger.info(f"Generating combinations from {len(all_words)} words")
        
        # If we don't have enough words, add some common patterns
        if len(all_words) < 2:
            all_words.extend(['password', 'admin', '123456'])
            logger.info("Added some common words due to insufficient input")
        
        # Generate combinations of 1 and 2 words
        for r in range(1, 3):
            for combo in itertools.permutations(all_words, r):
                word = ''.join(combo)
                if len(word) >= self.min_length:
                    self.wordlist.add(word)
        
        # Add combinations with underscore and dot separators for 2-word combinations
        for combo in itertools.permutations(all_words, 2):
            self.wordlist.add(f"{combo[0]}_{combo[1]}")
            self.wordlist.add(f"{combo[0]}.{combo[1]}")
        
        logger.info(f"Generated {len(self.wordlist)} base combinations")
            
    def apply_transformations(self):
        """
        Apply various transformations to the base words.
        """
        initial_count = len(self.wordlist)
        base_words = list(self.wordlist)
        
        logger.info(f"Applying transformations to {len(base_words)} base words")
        
        # Apply leetspeak transformations
        leet_count = 0
        for word in base_words:
            leet_variations = apply_leetspeak(word)
            self.wordlist.update(leet_variations)
            leet_count += len(leet_variations)
            
        # Apply case variations
        base_words = list(self.wordlist)  # Update base words with new additions
        case_count = 0
        for word in base_words:
            case_variations = create_case_variations(word)
            self.wordlist.update(case_variations)
            case_count += len(case_variations)
            
        # Append years and special characters
        base_words = list(self.wordlist)  # Update base words with new additions
        year_variations = []
        special_char_variations = []
        
        # Limit to reasonable number of base words for transformations
        base_words_for_transforms = base_words[:1000]  # Prevent excessive memory usage
        
        for word in base_words_for_transforms:
            year_variations.extend(append_years(word))
            special_char_variations.extend(append_special_chars(word))
        
        self.wordlist.update(year_variations)
        self.wordlist.update(special_char_variations)
        
        total_added = len(self.wordlist) - initial_count
        logger.info(f"Added {total_added} variations (leetspeak: {leet_count}, case: {case_count}, "
                   f"years: {len(year_variations)}, special chars: {len(special_char_variations)})")
    
    def generate_wordlist(self):
        """
        Generate the complete wordlist based on personal information.
        
        Returns:
            list: The generated wordlist
        """
        # Clear previous wordlist if any
        self.wordlist = set()
        
        # Generate base combinations
        self.generate_base_combinations()
        
        # Check if we have any base combinations
        if not self.wordlist:
            logger.warning("No base combinations generated. Adding fallback words.")
            # Add some fallback words if no combinations were generated
            self.wordlist.update(["password", "admin", "123456", "qwerty", "welcome"])
        
        # Apply transformations
        self.apply_transformations()
        
        # Limit wordlist size to prevent memory issues
        max_size = 50000
        wordlist = list(self.wordlist)
        if len(wordlist) > max_size:
            logger.warning(f"Wordlist too large ({len(wordlist)} words), trimming to {max_size}")
            wordlist = wordlist[:max_size]
        
        # Convert to sorted list and filter by minimum length
        final_list = sorted([word for word in wordlist if len(word) >= self.min_length])
        logger.info(f"Final wordlist contains {len(final_list)} words")
        
        # Ensure we have at least something in the wordlist
        if not final_list:
            logger.warning("Empty wordlist after filtering. Adding fallback words.")
            final_list = ["password", "admin", "123456", "qwerty", "welcome"]
        
        return final_list
    
    def save_wordlist_to_file(self, filepath=None):
        """
        Save the generated wordlist to a file.
        
        Args:
            filepath (str, optional): Path to save the file. If None, generates a default path.
            
        Returns:
            str: The path to the saved file
        """
        if not filepath:
            # Generate a filename based on timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"custom_wordlist_{timestamp}.txt"
        
        # Generate wordlist if not already generated
        if not self.wordlist:
            self.generate_wordlist()
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            for word in sorted(self.wordlist):
                f.write(f"{word}\n")
                
        return filepath
