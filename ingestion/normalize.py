import re

def normalize_constituency_name(name: str) -> str:
    """
    Normalizes a constituency name for matching across datasets.
    Rules:
    1. Lowercase
    2. Remove punctuation (hyphens, parentheses, periods, commas, etc.)
    3. Collapse multiple spaces to a single space
    4. Strip leading/trailing whitespace
    """
    if not isinstance(name, str):
        return ""
        
    # Lowercase
    normalized = name.lower()
    
    # Remove punctuation
    # We replace any non-alphanumeric character (excluding spaces) with a space
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    
    # Remove underscores which are matched by \w
    normalized = normalized.replace('_', ' ')
    
    # Collapse multiple spaces and strip
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized
