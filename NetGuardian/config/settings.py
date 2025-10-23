"""
Configuration settings for NetGuardian
Centralizes all application settings, paths, and constants
"""

import os
from typing import Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # Database settings
    # Defaults set to your Postgres server (override via env if needed)
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'CRDT-SSS-CLOUD')
    DB_USER = os.getenv('DB_USER', 'guardian')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'netguardian')

    # Application settings
    APP_SECRET_KEY = os.getenv('APP_SECRET_KEY', 'dev-secret-key')
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'dev-encryption-key')
    
    # File storage settings
    LOCAL_STORAGE_PATH = os.getenv('LOCAL_STORAGE_PATH', './local_files')
    CLOUD_STORAGE_ENABLED = os.getenv('CLOUD_STORAGE_ENABLED', 'true').lower() == 'true'
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '100'))

    # CRDT / sync folder settings
    # Default to server sync folder at /opt/crdt-cluster/sync_folder (can be overridden via CRDT_SYNC_FOLDER env)
    CRDT_SYNC_FOLDER = os.getenv('CRDT_SYNC_FOLDER', '/opt/crdt-cluster/sync_folder/lww')
    # When True, the dashboard will use files present in the CRDT sync folder as the main source
    USE_CRDT_AS_MAIN = os.getenv('USE_CRDT_AS_MAIN', 'true').lower() == 'true'
    # When True, uploaded files are mirrored into the CRDT sync folder (so CRDT nodes can sync them)
    SYNC_TO_CRDT = os.getenv('SYNC_TO_CRDT', 'true').lower() == 'true'

    # GUI settings
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WINDOW_MIN_WIDTH = 900
    WINDOW_MIN_HEIGHT = 600
    THEME = "dark"
    
    # Adobe CC-inspired color palette
    COLORS: Dict[str, str] = {
        # Primary colors
        'primary': '#4A9EFF',           # Adobe blue
        'primary_hover': '#3A7FCC',     # Darker blue for hover
        'primary_dark': '#2A5F9C',      # Even darker for pressed
        
        # Backgrounds
        'bg_main': '#1A1A1A',           # Main background
        'bg_sidebar': '#2A2A2A',        # Sidebar/cards
        'bg_card': '#2A2A2A',           # File cards
        'bg_hover': '#3A3A3A',          # Hover state
        'bg_input': '#3A3A3A',          # Input fields
        
        # Text colors
        'text_primary': '#FFFFFF',      # Primary text
        'text_secondary': '#B0B0B0',    # Secondary text
        'text_muted': '#808080',        # Muted/disabled text
        
        # Status colors
        'success': '#4CAF50',           # Green
        'warning': '#FF9800',           # Orange
        'error': '#FF6B6B',             # Red/delete
        'info': '#2196F3',              # Info blue
        
        # Borders
        'border': '#3A3A3A',            # Default border
        'border_focus': '#4A9EFF',      # Focused input border
    }
    
    # File type categories and their extensions
    FILE_CATEGORIES: Dict[str, list] = {
        'documents': ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.pptx'],
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico'],
        'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
        'code': ['.py', '.js', '.java', '.cpp', '.c', '.html', '.css', '.json', '.xml']
    }
    
    # UI Layout constants
    SIDEBAR_WIDTH = 220
    HERO_BANNER_HEIGHT = 200
    FILE_CARD_WIDTH = 280
    FILE_CARD_HEIGHT = 180
    GRID_COLUMNS = 3
    SPACING = 20

    # Whether to use the internal CRDT implementation in NetGuardian
    APP_USE_INTERNAL_CRDT = os.getenv('APP_USE_INTERNAL_CRDT', 'false').lower() == 'true'

class DatabaseConfig:
    """Database configuration and connection utilities"""
    
    @staticmethod
    def get_connection_string() -> str:
        """
        Get PostgreSQL connection string.
        
        Returns:
            str: Formatted PostgreSQL connection URI
        """
        return f"postgresql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"
    
    @staticmethod
    def get_connection_params() -> Dict[str, str]:
        """
        Get connection parameters as dictionary.
        
        Returns:
            dict: Database connection parameters
        """
        return {
            'host': Config.DB_HOST,
            'port': Config.DB_PORT,
            'database': Config.DB_NAME,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD
        }


class ValidationRules:
    """Input validation rules and constraints"""
    
    # User validation
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 50
    MIN_PASSWORD_LENGTH = 6
    MAX_PASSWORD_LENGTH = 128
    
    # File validation
    MAX_FILENAME_LENGTH = 255
    ALLOWED_FILENAME_CHARS = r'^[a-zA-Z0-9._\-\s]+$'
    
    # Session settings
    SESSION_EXPIRY_DAYS = 7
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15


class UIConstants:
    """UI-specific constants and messages"""
    
    # Empty state messages
    EMPTY_FILES_MESSAGE = "No files found. Upload your first file to get started!"
    EMPTY_SEARCH_MESSAGE = "No files match your search."
    EMPTY_CATEGORY_MESSAGE = "No files in this category."
    
    # Button labels
    BTN_UPLOAD = "Upload File"
    BTN_OPEN = "Open"
    BTN_DELETE = "Delete"
    BTN_LOGIN = "Login"
    BTN_REGISTER = "Register"
    BTN_LOGOUT = "Logout"
    
    # Success messages
    SUCCESS_UPLOAD = "File uploaded successfully!"
    SUCCESS_DELETE = "File deleted successfully!"
    SUCCESS_LOGIN = "Welcome back!"
    SUCCESS_REGISTER = "Account created successfully!"
    
    # Error messages
    ERROR_UPLOAD = "Failed to upload file"
    ERROR_DELETE = "Failed to delete file"
    ERROR_LOGIN = "Invalid username or password"
    ERROR_REGISTER = "Registration failed"
    ERROR_NETWORK = "Network connection error"
    ERROR_FILE_SIZE = "File size exceeds maximum allowed"