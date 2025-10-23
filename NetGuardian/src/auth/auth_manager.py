"""
Authentication Manager for NetGuardian
Handles user registration, login, and session management with bcrypt password hashing
"""

import bcrypt
import hashlib
import secrets
from typing import Tuple, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from config.settings import ValidationRules, UIConstants

logger = logging.getLogger(__name__)

class AuthManager:
    """
    Manages user authentication, session handling, and password security.
    
    Attributes:
        db_manager: Database manager instance for data operations
        current_user: Currently authenticated user data (dict or None)
        current_session: Active session token (str or None)
    """
    
    def __init__(self, db_manager) -> None:
        """
        Initialize AuthManager with database connection.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager
        self.current_user: Optional[Dict[str, Any]] = None
        self.current_session: Optional[str] = None
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt with salt.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            str: Bcrypt hashed password or SHA256 fallback
            
        Raises:
            ValueError: If password is empty
        """
        if not password:
            raise ValueError("Password cannot be empty")
            
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Bcrypt hashing failed: {e}, using SHA256 fallback")
            # Fallback to simple hash for development only
            return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its stored hash.
        
        Supports both bcrypt and SHA256 (legacy) hashing.
        
        Args:
            password: Plain text password to verify
            hashed_password: Stored password hash (string or bytes)
            
        Returns:
            bool: True if password matches, False otherwise
        """
        if not password or not hashed_password:
            return False
            
        try:
            # Normalize to string
            if isinstance(hashed_password, bytes):
                hp = hashed_password.decode('utf-8', errors='ignore')
            else:
                hp = str(hashed_password)

            hp = hp.strip()

            # bcrypt hashes start with $2a$ / $2b$ / $2y$
            if hp.startswith('$2'):
                try:
                    return bcrypt.checkpw(password.encode('utf-8'), hp.encode('utf-8'))
                except Exception as e:
                    logger.error(f"Bcrypt verification failed: {e}")
                    return False

            # SHA256 hex (64 hex chars)
            import re
            if re.fullmatch(r'[0-9a-fA-F]{64}', hp):
                return hashlib.sha256(password.encode()).hexdigest() == hp.lower()

            # Not a known hash format -> assume plaintext stored in DB. Compare directly.
            try:
                return password == hp
            except Exception:
                return False

        except Exception as e:
            logger.error(f"Unexpected error during password verification: {e}")
            return False
    
    def register_user(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """
        Register a new user account.
        
        Args:
            username: Desired username (3-50 characters)
            email: User's email address
            password: Plain text password (min 6 characters)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Validate input presence
            if not all([username, email, password]):
                return False, "All fields are required"
            
            # Validate username length
            if not (ValidationRules.MIN_USERNAME_LENGTH <= len(username) <= ValidationRules.MAX_USERNAME_LENGTH):
                return False, f"Username must be {ValidationRules.MIN_USERNAME_LENGTH}-{ValidationRules.MAX_USERNAME_LENGTH} characters"
            
            # Validate password length
            if len(password) < ValidationRules.MIN_PASSWORD_LENGTH:
                return False, f"Password must be at least {ValidationRules.MIN_PASSWORD_LENGTH} characters"
            
            if len(password) > ValidationRules.MAX_PASSWORD_LENGTH:
                return False, f"Password too long (max {ValidationRules.MAX_PASSWORD_LENGTH} characters)"
            
            # Check if user already exists
            existing_user = self.db_manager.execute_query(
                "SELECT id FROM users WHERE name = ? OR email = ?",
                (username, email)
            )
            
            if existing_user:
                return False, "Username or email already exists"
            
            # Hash password and create user
            password_hash = self.hash_password(password)
            
            self.db_manager.execute_query(
                """INSERT INTO users (name, email, password) 
                   VALUES (?, ?, ?)""",
                (username, email, password_hash)
            )
            
            logger.info(f"User registered successfully: {username}")
            return True, UIConstants.SUCCESS_REGISTER
            
        except ValueError as e:
            logger.error(f"Validation error during registration: {e}")
            return False, str(e)
        except Exception as e:
            logger.error(f"User registration failed: {e}", exc_info=True)
            return False, UIConstants.ERROR_REGISTER
    
    def login_user(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate user login credentials.
        
        Args:
            username: User's username
            password: Plain text password
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not username or not password:
            return False, UIConstants.ERROR_LOGIN
            
        try:
            # Get user from database
            user = self.db_manager.execute_query(
                "SELECT * FROM users WHERE name = ?",
                (username,)
            )
            
            if not user:
                logger.warning(f"Login attempt for non-existent user: {username}")
                return False, UIConstants.ERROR_LOGIN
            
            user = user[0]
            
            # Verify password
            stored_pw = user.get('password')
            if not self.verify_password(password, stored_pw):
                logger.warning(f"Invalid password attempt for user: {username}")
                return False, UIConstants.ERROR_LOGIN
            
            # Create session
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(days=ValidationRules.SESSION_EXPIRY_DAYS)
            
            self.db_manager.execute_query(
                """INSERT INTO sessions (user_id, session_token, expires_at) 
                   VALUES (?, ?, ?)""",
                (user['id'], session_token, expires_at)
            )
            
            # Update last login (skip if column doesn't exist)
            try:
                self.db_manager.execute_query(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (datetime.now(), user['id'])
                )
            except Exception:
                pass  # Column might not exist in older schemas
            
            # After successful auth: if stored password was plaintext, upgrade to bcrypt
            try:
                sp = stored_pw or ''
                if not (isinstance(sp, str) and sp.strip().startswith('$2')):
                    # treat as plaintext or non-bcrypt: replace with bcrypt hash
                    new_hash = self.hash_password(password)
                    try:
                        self.db_manager.execute_query(
                            "UPDATE users SET password = ? WHERE id = ?",
                            (new_hash, user['id'])
                        )
                    except Exception:
                        logger.warning('Failed to upgrade stored plaintext password to bcrypt')
            except Exception:
                pass

            # Set current user and session
            # normalize current_user to include 'username' for compatibility
            u = dict(user)
            u['username'] = u.get('name')
            self.current_user = u
            self.current_session = session_token
            
            logger.info(f"User logged in successfully: {username}")
            return True, UIConstants.SUCCESS_LOGIN
            
        except Exception as e:
            logger.error(f"Login failed for user {username}: {e}", exc_info=True)
            return False, UIConstants.ERROR_LOGIN
    
    def logout_user(self) -> bool:
        """
        Logout current user and invalidate their session.
        
        Returns:
            bool: True if logout successful, False otherwise
        """
        try:
            if self.current_session:
                self.db_manager.execute_query(
                    "UPDATE sessions SET is_active = 0 WHERE session_token = ?",
                    (self.current_session,)
                )
            
            username = self.current_user.get('username', 'unknown') if self.current_user else 'unknown'
            self.current_user = None
            self.current_session = None
            
            logger.info(f"User logged out successfully: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Logout failed: {e}", exc_info=True)
            return False
    
    def is_authenticated(self) -> bool:
        """
        Check if a user is currently authenticated.
        
        Returns:
            bool: True if user is logged in, False otherwise
        """
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current authenticated user data.
        
        Returns:
            dict or None: User data dictionary or None if not authenticated
        """
        return self.current_user
    
    def validate_session(self, session_token: str) -> bool:
        """
        Validate and restore a session from token.
        
        Args:
            session_token: Session token to validate
            
        Returns:
            bool: True if session is valid and restored, False otherwise
        """
        if not session_token:
            return False
            
        try:
            session = self.db_manager.execute_query(
                """SELECT s.*, u.* FROM sessions s 
                   JOIN users u ON s.user_id = u.id 
                   WHERE s.session_token = ? AND s.is_active = 1 AND s.expires_at > ?""",
                (session_token, datetime.now())
            )
            
            if session:
                session = session[0]
                # session row contains user columns prefixed as in query; normalize
                self.current_user = {
                    'id': session['user_id'],
                    'username': session.get('name') or session.get('username'),
                    'email': session.get('email')
                }
                self.current_session = session_token
                logger.info(f"Session restored for user: {self.current_user['username']}")
                return True
            
            logger.warning("Invalid or expired session token")
            return False
            
        except Exception as e:
            logger.error(f"Session validation failed: {e}", exc_info=True)
            return False
