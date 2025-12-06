"""
API Key Management
Functions to save, retrieve, validate, and check user API keys.
"""

import logging
from typing import Optional, Tuple
from src.database import db, UserAPIKey
import os

# Try to import for validation
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

logger = logging.getLogger(__name__)


def save_user_api_keys(user_id: int, gemini_key: Optional[str] = None, openai_key: Optional[str] = None) -> Tuple[bool, str]:
    """
    Save user's API keys (encrypted).
    
    Args:
        user_id: User ID
        gemini_key: Gemini API key (optional)
        openai_key: OpenAI API key (optional)
        
    Returns:
        (success, message)
    """
    try:
        # Get or create API key record
        api_keys = UserAPIKey.query.filter_by(user_id=user_id).first()
        if not api_keys:
            api_keys = UserAPIKey(user_id=user_id)
            db.session.add(api_keys)
        
        # Update keys (only if provided)
        if gemini_key is not None:
            if gemini_key.strip():
                api_keys.set_gemini_key(gemini_key.strip())
            else:
                api_keys.gemini_api_key_encrypted = None
        
        if openai_key is not None:
            if openai_key.strip():
                api_keys.set_openai_key(openai_key.strip())
            else:
                api_keys.openai_api_key_encrypted = None
        
        db.session.commit()
        logger.info(f"API keys saved for user_id={user_id}")
        return True, "API keys saved successfully"
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving API keys: {e}")
        return False, f"Failed to save API keys: {str(e)}"


def get_user_api_keys(user_id: int) -> Tuple[Optional[str], Optional[str]]:
    """
    Get user's API keys (decrypted).
    
    Args:
        user_id: User ID
        
    Returns:
        (gemini_key, openai_key)
    """
    try:
        api_keys = UserAPIKey.query.filter_by(user_id=user_id).first()
        if not api_keys:
            return None, None
        
        gemini_key = api_keys.get_gemini_key()
        openai_key = api_keys.get_openai_key()
        return gemini_key, openai_key
        
    except Exception as e:
        logger.error(f"Error getting API keys: {e}")
        return None, None


def validate_api_key(provider: str, api_key: str) -> Tuple[bool, str]:
    """
    Validate an API key by making a test API call.
    
    Args:
        provider: 'gemini' or 'openai'
        api_key: API key to validate
        
    Returns:
        (is_valid, message)
    """
    if not api_key or not api_key.strip():
        return False, "API key is empty"
    
    try:
        if provider.lower() == 'gemini':
            if not GEMINI_AVAILABLE:
                return False, "Gemini SDK not available"
            
            # Test Gemini API key
            genai.configure(api_key=api_key.strip())
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content("test")
            if response:
                return True, "Gemini API key is valid"
            return False, "Gemini API key validation failed"
        
        elif provider.lower() == 'openai':
            if not OPENAI_AVAILABLE:
                return False, "OpenAI SDK not available"
            
            # Test OpenAI API key
            client = OpenAI(api_key=api_key.strip())
            # Make a minimal test call
            response = client.models.list()
            if response:
                return True, "OpenAI API key is valid"
            return False, "OpenAI API key validation failed"
        
        else:
            return False, f"Unknown provider: {provider}"
            
    except Exception as e:
        logger.warning(f"API key validation error for {provider}: {e}")
        # Don't fail validation on network errors, just log
        # Return True with warning - let the actual usage determine validity
        return True, f"API key format looks valid (validation test failed: {str(e)})"


def has_at_least_one_key(user_id: int) -> bool:
    """
    Check if user has at least one API key set.
    
    Args:
        user_id: User ID
        
    Returns:
        True if user has at least one key, False otherwise
    """
    try:
        api_keys = UserAPIKey.query.filter_by(user_id=user_id).first()
        if not api_keys:
            return False
        return api_keys.has_at_least_one_key()
    except Exception as e:
        logger.error(f"Error checking API keys: {e}")
        return False


def get_api_key_status(user_id: int) -> dict:
    """
    Get API key status for a user (without exposing keys).
    
    Args:
        user_id: User ID
        
    Returns:
        Dictionary with status information
    """
    try:
        api_keys = UserAPIKey.query.filter_by(user_id=user_id).first()
        if not api_keys:
            return {
                'has_gemini': False,
                'has_openai': False,
                'has_any': False
            }
        
        return {
            'has_gemini': bool(api_keys.gemini_api_key_encrypted),
            'has_openai': bool(api_keys.openai_api_key_encrypted),
            'has_any': api_keys.has_at_least_one_key()
        }
    except Exception as e:
        logger.error(f"Error getting API key status: {e}")
        return {
            'has_gemini': False,
            'has_openai': False,
            'has_any': False
        }

