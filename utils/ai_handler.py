"""
AI integration for unknown error codes.
Uses Google Gemini API with fallback to None if unavailable.
"""
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Only import and configure if key exists
_model = None
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        _model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception:
        _model = None


def get_ai_explanation(user_input):
    """
    Get AI-generated explanation for an unknown error.
    
    Args:
        user_input: The error code or message from user
    
    Returns:
        Dict with title, explanation, reasons, next_steps if successful
        None if AI unavailable or fails
    """
    if not _model or not user_input:
        return None
    
    prompt = f"""You are a helpful assistant explaining UPI and Indian banking transaction errors.

The user encountered this error: "{user_input}"

Respond with ONLY a valid JSON object (no markdown, no extra text) with these exact keys:
- "title": A short title for this error (5-7 words max)
- "explanation": Plain English explanation of what this error means (2 sentences max, India banking context)
- "reasons": A list of 2-3 likely reasons why this happened (short bullet points)
- "next_steps": A list of 2-3 clear actions the user should take

Rules:
- Use simple, non-technical language
- Assume Indian banking/UPI context
- If unsure, say "This error usually means..."
- Do NOT guess specific bank policies
- Keep each field concise

Return ONLY the JSON object, nothing else."""

    try:
        response = _model.generate_content(prompt)
        
        if not response or not response.text:
            return None
        
        # Clean response text (remove markdown code blocks if present)
        text = response.text.strip()
        if text.startswith("```"):
            # Remove markdown code block
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
        
        # Parse JSON
        data = json.loads(text)
        
        # Validate required keys
        required_keys = ["title", "explanation", "reasons", "next_steps"]
        if not all(key in data for key in required_keys):
            return None
        
        # Ensure reasons and next_steps are lists
        if not isinstance(data["reasons"], list) or not isinstance(data["next_steps"], list):
            return None
        
        return data
        
    except Exception:
        # Any error (API, parsing, etc.) → return None silently
        return None


def is_ai_available():
    """Check if AI is configured and available."""
    return _model is not None
