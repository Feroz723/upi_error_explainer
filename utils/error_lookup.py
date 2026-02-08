"""
Static error lookup from JSON database.
"""
import json
import os

# Path to errors.json
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "errors.json")

# Cache loaded errors
_errors_cache = None


def _load_errors():
    """Load errors from JSON file (cached)."""
    global _errors_cache
    if _errors_cache is None:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            _errors_cache = json.load(f)
    return _errors_cache


def normalize_input(raw_input):
    """
    Normalize user input to a standard format.
    - Strip whitespace
    - Convert to lowercase for matching
    """
    if not raw_input:
        return ""
    return raw_input.strip().lower()


def get_error_by_input(user_input):
    """
    Look up error by user input (code, alias, or scenario text).
    
    Args:
        user_input: Raw user input (error code, phrase, or message)
    
    Returns:
        Tuple of (slug, error_dict) if found, else (None, None)
    """
    if not user_input:
        return None, None
    
    normalized = normalize_input(user_input)
    normalized_upper = normalized.upper()
    errors = _load_errors()
    
    # 1. Direct match by key (slug)
    if normalized in errors:
        return normalized, errors[normalized]
    
    # 2. Match against error code field
    for slug, error_data in errors.items():
        code = error_data.get("code", "").upper()
        if code == normalized_upper:
            return slug, error_data
    
    # 3. Match against aliases (exact match)
    for slug, error_data in errors.items():
        aliases = error_data.get("aliases", [])
        for alias in aliases:
            if alias.lower() == normalized:
                return slug, error_data
    
    # 4. Partial match - input contains error code
    for slug, error_data in errors.items():
        code = error_data.get("code", "").upper()
        if code and code in normalized_upper:
            return slug, error_data
    
    # 5. Partial match - input matches part of alias
    for slug, error_data in errors.items():
        aliases = error_data.get("aliases", [])
        for alias in aliases:
            if alias.lower() in normalized or normalized in alias.lower():
                return slug, error_data
    
    # 6. Match against scenarios text
    for slug, error_data in errors.items():
        scenarios = error_data.get("scenarios", [])
        for scenario in scenarios:
            if normalized in scenario.lower():
                return slug, error_data
    
    # No match found
    return None, None


def get_error_by_slug(slug):
    """
    Get error data by its URL slug.
    
    Args:
        slug: URL slug like 'u28' or 'bank-declined'
    
    Returns:
        Error dict if found, else None
    """
    if not slug:
        return None
    
    errors = _load_errors()
    return errors.get(slug.lower())


def get_all_errors():
    """Get all errors for listing on homepage."""
    return _load_errors()


def get_related_errors_smart(current_slug, limit=5):
    """
    Get related errors based on similar aliases.
    Falls back to random selection if no similarities found.
    
    Args:
        current_slug: Current error's slug to exclude
        limit: Maximum number of errors to return
    
    Returns:
        Dict of slug -> error_data
    """
    all_errors = _load_errors()
    current_error = all_errors.get(current_slug, {})
    current_aliases = set(a.lower() for a in current_error.get("aliases", []))
    
    # Extract keywords from current aliases
    current_keywords = set()
    for alias in current_aliases:
        current_keywords.update(alias.split())
    
    # Remove common words
    stop_words = {"upi", "error", "the", "a", "an", "is", "are", "was", "were", "by", "on", "in", "not"}
    current_keywords -= stop_words
    
    # Score other errors by keyword overlap
    scored = []
    for slug, data in all_errors.items():
        if slug == current_slug:
            continue
        
        aliases = data.get("aliases", [])
        error_keywords = set()
        for alias in aliases:
            error_keywords.update(alias.lower().split())
        error_keywords -= stop_words
        
        # Calculate overlap score
        overlap = len(current_keywords & error_keywords)
        scored.append((overlap, slug, data))
    
    # Sort by score (highest first), then take top ones
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # Return top scoring or fallback to first N if no overlaps
    related = {}
    for _, slug, data in scored[:limit]:
        related[slug] = data
    
    return related
