"""
Authentication System
User registration, login, and session management.
"""

from werkzeug.security import generate_password_hash, check_password_hash
from flask import session, redirect, url_for, request, jsonify
from functools import wraps
from typing import Tuple, Optional
import re
import logging
from src.database import db, User, UserAPIKey

logger = logging.getLogger(__name__)


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if len(password) > 128:
        return False, "Password is too long (max 128 characters)"
    return True, ""


def register_user(email: str, password: str) -> Tuple[bool, str, Optional[User]]:
    """
    Register a new user.
    
    Args:
        email: User email address
        password: User password
        
    Returns:
        (success, message, user_object)
    """
    try:
        # Validate email
        if not email or not email.strip():
            return False, "Email is required", None
        
        email = email.strip().lower()
        if not validate_email(email):
            return False, "Invalid email format", None
        
        # Validate password
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return False, error_msg, None
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return False, "Email already registered", None
        
        # Create new user
        password_hash = generate_password_hash(password)
        user = User(email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User registered: {email}")
        return True, "Registration successful", user
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {e}")
        return False, f"Registration failed: {str(e)}", None


def login_user(email: str, password: str) -> Tuple[bool, str, Optional[User]]:
    """
    Login a user.
    
    Args:
        email: User email address
        password: User password
        
    Returns:
        (success, message, user_object)
    """
    try:
        if not email or not password:
            return False, "Email and password are required", None
        
        email = email.strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return False, "Invalid email or password", None
        
        if not check_password_hash(user.password_hash, password):
            return False, "Invalid email or password", None
        
        logger.info(f"User logged in: {email}")
        return True, "Login successful", user
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return False, f"Login failed: {str(e)}", None


def get_current_user():
    """Get the currently logged-in user from session."""
    user_id = session.get('user_id')
    if not user_id:
        return None
    
    try:
        return User.query.get(user_id)
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        return None


def require_auth(f):
    """Decorator to require authentication for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required', 'redirect': '/login'}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


def require_api_key(f):
    """Decorator to require at least one API key for a route."""
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required', 'redirect': '/login'}), 401
            return redirect(url_for('login_page'))
        
        # Check if user has API keys
        api_keys = UserAPIKey.query.filter_by(user_id=user.id).first()
        if not api_keys or not api_keys.has_at_least_one_key():
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({
                    'error': 'At least one API key (Gemini or OpenAI) is required',
                    'redirect': '/api-keys'
                }), 403
            return redirect(url_for('api_keys_page'))
        
        return f(*args, **kwargs)
    return decorated_function

