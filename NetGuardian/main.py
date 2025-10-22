"""
NetGuardian - Desktop Cloud File Management System
Main application entry point
"""

import sys
import os
import tkinter as tk
import logging

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.main_window import MainWindow
from src.auth.auth_manager import AuthManager
from src.database.db_manager import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('netguardian.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application entry point"""
    try:
        # Initialize database
        db_manager = DatabaseManager()
        db_manager.initialize_database()
        
        # Initialize authentication manager
        auth_manager = AuthManager(db_manager)
        
        # Create and run the main application
        root = tk.Tk()
        app = MainWindow(root, auth_manager, db_manager)
        
        logger.info("NetGuardian application started")
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

if __name__ == "__main__":
    main()