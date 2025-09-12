import re
from typing import Dict, List


class TextCensor:
    """Handles censorship of inappropriate words in text scripts for content creation."""
    
    def __init__(self):
        """Initialize the censor with predefined word replacements."""
        self.censorship_map = {
            # Violence and harm related
            'kill': 'unalive',
            'killed': 'unalived',
            'killing': 'unaliving',
            'kills': 'unalives',
            'murder': 'unalive',
            'murdered': 'unalived',
            'murdering': 'unaliving',
            'murders': 'unalives',
            'death': 'unalived',
            'dead': 'unalived',
            'die': 'unalive',
            'died': 'unalived',
            'dying': 'unaliving',
            'dies': 'unalives',
            'suicide': 'self-unaliving',
            'suicidal': 'self-unaliving',
            
            # Body fluids and substances
            'blood': 'red liquid',
            'bloody': 'red liquid covered',
            'bleeding': 'red liquid flowing',
            'bleed': 'red liquid flow',
            'bleeds': 'red liquid flows',
            'bled': 'red liquid flowed',
            
            # Adult content
            'sex': 'intercourse',
            'sexual': 'intimate',
            'sexy': 'attractive',
            
            # Weapons
            'gun': 'pew pew device',
            'guns': 'pew pew devices',
            'knife': 'sharp object',
            'knives': 'sharp objects',
            'weapon': 'tool',
            'weapons': 'tools',
            'bomb': 'explosive device',
            'bombs': 'explosive devices',
            
            # Drugs and substances
            'drug': 'substance',
            'drugs': 'substances',
            'cocaine': 'white powder',
            'heroin': 'substance',
            'marijuana': 'green plant',
            'weed': 'green plant',
            
            # Profanity (mild replacements)
            'damn': 'darn',
            'hell': 'heck',
            'crap': 'crud',
            
            # Other potentially flagged words
            'virus': 'bug',
            'pandemic': 'global health event',
            'war': 'conflict',
            'terrorist': 'bad person',
            'terrorism': 'bad activities',
        }
        
        # Compile regex patterns for efficient matching
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for word replacement."""
        self.patterns = {}
        for word, replacement in self.censorship_map.items():
            # Create pattern that matches whole words (case insensitive)
            pattern = r'\b' + re.escape(word) + r'\b'
            self.patterns[word] = re.compile(pattern, re.IGNORECASE)
    
    def censor_text(self, text: str) -> str:
        """Apply censorship to the given text.
        
        Args:
            text: The original text to censor
            
        Returns:
            Censored text with replacements applied
        """
        censored_text = text
        
        for word, pattern in self.patterns.items():
            replacement = self.censorship_map[word]
            censored_text = pattern.sub(replacement, censored_text)
        
        return censored_text
    
    def add_censorship_rule(self, word: str, replacement: str):
        """Add a new censorship rule.
        
        Args:
            word: Word to be censored
            replacement: Replacement text
        """
        self.censorship_map[word.lower()] = replacement
        pattern = r'\b' + re.escape(word.lower()) + r'\b'
        self.patterns[word.lower()] = re.compile(pattern, re.IGNORECASE)
    
    def remove_censorship_rule(self, word: str):
        """Remove a censorship rule.
        
        Args:
            word: Word to remove from censorship
        """
        word_lower = word.lower()
        if word_lower in self.censorship_map:
            del self.censorship_map[word_lower]
            del self.patterns[word_lower]
    
    def get_censorship_rules(self) -> Dict[str, str]:
        """Get all current censorship rules.
        
        Returns:
            Dictionary of word -> replacement mappings
        """
        return self.censorship_map.copy()
    
    def find_flagged_words(self, text: str) -> List[str]:
        """Find words in text that would be censored.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of words that would be censored
        """
        flagged_words = []
        text_lower = text.lower()
        
        for word, pattern in self.patterns.items():
            if pattern.search(text):
                flagged_words.append(word)
        
        return flagged_words


def censor_text_file(input_file: str, output_file: str = None) -> str:
    """Censor a text file and optionally save to a new file.
    
    Args:
        input_file: Path to input text file
        output_file: Optional path to output file (if None, overwrites input)
        
    Returns:
        Path to the censored file
    """
    censor = TextCensor()
    
    # Read original text
    with open(input_file, 'r', encoding='utf-8') as f:
        original_text = f.read()
    
    # Apply censorship
    censored_text = censor.censor_text(original_text)
    
    # Determine output file
    if output_file is None:
        output_file = input_file
    
    # Write censored text
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(censored_text)
    
    return output_file


# Global censor instance for easy access
default_censor = TextCensor()