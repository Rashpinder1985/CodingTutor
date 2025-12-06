"""
Database Models and Connection
SQLAlchemy models for user authentication and API key management.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from cryptography.fernet import Fernet
import os
import base64
import logging
from typing import Optional

logger = logging.getLogger(__name__)

db = SQLAlchemy()

# Generate encryption key for API keys (use environment variable or generate)
def get_encryption_key():
    """Get or generate encryption key for API keys."""
    key = os.getenv('API_KEY_ENCRYPTION_KEY')
    if not key:
        # Generate a key and store it (in production, set this as env var)
        key = Fernet.generate_key()  # Returns bytes
        logger.warning("API_KEY_ENCRYPTION_KEY not set. Generated new key. Set this in production!")
    else:
        # Ensure key is bytes
        if isinstance(key, str):
            key = key.encode()
    return key

# Initialize Fernet cipher (lazy initialization)
_cipher = None

def get_cipher():
    """Get or create the Fernet cipher instance."""
    global _cipher
    if _cipher is None:
        try:
            encryption_key = get_encryption_key()
            _cipher = Fernet(encryption_key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            _cipher = None
    return _cipher

# For backward compatibility - initialize on module load
try:
    cipher = get_cipher()
except Exception as e:
    logger.error(f"Failed to initialize cipher: {e}")
    cipher = None


class User(db.Model):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to API keys
    api_keys = db.relationship('UserAPIKey', backref='user', lazy=True, uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'


class UserAPIKey(db.Model):
    """User API keys model (encrypted storage)."""
    __tablename__ = 'user_api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    gemini_api_key_encrypted = db.Column(db.Text, nullable=True)
    openai_api_key_encrypted = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def encrypt_api_key(self, api_key: str) -> Optional[str]:
        """Encrypt an API key."""
        if not api_key:
            return None
        cipher_instance = get_cipher()
        if not cipher_instance:
            logger.error("Encryption cipher not available")
            return None
        try:
            encrypted = cipher_instance.encrypt(api_key.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Failed to encrypt API key: {e}")
            return None
    
    def decrypt_api_key(self, encrypted_key: str) -> Optional[str]:
        """Decrypt an API key."""
        if not encrypted_key:
            return None
        cipher_instance = get_cipher()
        if not cipher_instance:
            logger.error("Encryption cipher not available")
            return None
        try:
            decrypted = cipher_instance.decrypt(encrypted_key.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt API key: {e}")
            return None
    
    def set_gemini_key(self, api_key: str):
        """Set and encrypt Gemini API key."""
        if api_key:
            self.gemini_api_key_encrypted = self.encrypt_api_key(api_key)
        else:
            self.gemini_api_key_encrypted = None
    
    def set_openai_key(self, api_key: str):
        """Set and encrypt OpenAI API key."""
        if api_key:
            self.openai_api_key_encrypted = self.encrypt_api_key(api_key)
        else:
            self.openai_api_key_encrypted = None
    
    def get_gemini_key(self) -> str:
        """Get and decrypt Gemini API key."""
        if self.gemini_api_key_encrypted:
            return self.decrypt_api_key(self.gemini_api_key_encrypted)
        return None
    
    def get_openai_key(self) -> str:
        """Get and decrypt OpenAI API key."""
        if self.openai_api_key_encrypted:
            return self.decrypt_api_key(self.openai_api_key_encrypted)
        return None
    
    def has_at_least_one_key(self) -> bool:
        """Check if user has at least one API key set."""
        return bool(self.gemini_api_key_encrypted or self.openai_api_key_encrypted)
    
    def __repr__(self):
        return f'<UserAPIKey user_id={self.user_id}>'


def init_db(app):
    """Initialize database with Flask app."""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        logger.info("Database tables created/verified")


def get_db_uri():
    """Get database URI from environment or use SQLite for local dev."""
    # Railway provides DATABASE_URL
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        # Railway's DATABASE_URL might be postgres://, convert to postgresql://
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        return db_url
    
    # Local development: use SQLite
    return 'sqlite:///app.db'

