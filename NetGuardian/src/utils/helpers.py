"""
Utility functions for NetGuardian
Common helper functions used across the application
"""

import os
import logging
import hashlib
from datetime import datetime
import json

logger = logging.getLogger(__name__)

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    size_index = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and size_index < len(size_names) - 1:
        size /= 1024.0
        size_index += 1
    
    return f"{size:.1f} {size_names[size_index]}"

def validate_email(email):
    """Simple email validation"""
    return "@" in email and "." in email.split("@")[-1]

def validate_username(username):
    """Validate username format"""
    if not username:
        return False, "Username cannot be empty"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username must be less than 50 characters"
    
    # Check for valid characters (alphanumeric and underscore)
    if not username.replace("_", "").isalnum():
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, "Valid username"

def validate_password(password):
    """Validate password strength"""
    if not password:
        return False, "Password cannot be empty"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    # Check for at least one letter and one number
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    
    if not (has_letter and has_number):
        return False, "Password must contain at least one letter and one number"
    
    return True, "Valid password"

def generate_session_token():
    """Generate a secure session token"""
    import secrets
    return secrets.token_urlsafe(32)

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file"""
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Failed to calculate file hash: {e}")
        return None

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename

def ensure_directory_exists(directory_path):
    """Ensure a directory exists, create if it doesn't"""
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            logger.info(f"Created directory: {directory_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory_path}: {e}")
        return False

def get_file_extension(filename):
    """Get file extension in lowercase"""
    return os.path.splitext(filename)[1].lower()

def is_allowed_file_type(filename, allowed_extensions=None):
    """Check if file type is allowed"""
    if allowed_extensions is None:
        # Default allowed extensions
        allowed_extensions = {
            '.txt', '.doc', '.docx', '.pdf', '.rtf',  # Documents
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg',  # Images
            '.mp3', '.wav', '.m4a', '.flac',  # Audio
            '.mp4', '.avi', '.mkv', '.mov', '.wmv',  # Video
            '.zip', '.rar', '.7z', '.tar', '.gz',  # Archives
            '.xlsx', '.xls', '.csv', '.ppt', '.pptx',  # Office
            '.py', '.js', '.html', '.css', '.json', '.xml'  # Code
        }
    
    file_ext = get_file_extension(filename)
    return file_ext in allowed_extensions

def format_datetime(dt):
    """Format datetime for display"""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return dt
    
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    return str(dt)

def load_json_file(file_path):
    """Load JSON data from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON file {file_path}: {e}")
        return None

def save_json_file(data, file_path):
    """Save data to JSON file"""
    try:
        ensure_directory_exists(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON file {file_path}: {e}")
        return False

def get_system_info():
    """Get basic system information"""
    import platform
    return {
        'system': platform.system(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version()
    }

class Timer:
    """Simple timer for performance measurement"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start the timer"""
        self.start_time = datetime.now()
    
    def stop(self):
        """Stop the timer"""
        self.end_time = datetime.now()
    
    def elapsed(self):
        """Get elapsed time in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0

def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed: {e}")
            raise
    return wrapper