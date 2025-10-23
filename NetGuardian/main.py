"""
NetGuardian - Desktop Cloud File Management System
Main application entry point
"""

import sys
import os
import tkinter as tk
import logging
import threading
from fastapi import FastAPI
import uvicorn

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.gui.main_window import MainWindow
from src.auth.auth_manager import AuthManager
from src.database.db_manager import DatabaseManager
from src.api.file_api import router as file_router

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

def start_api():
    app = FastAPI()
    app.include_router(file_router, prefix="/api/files")
    uvicorn.run(app, host="0.0.0.0", port=51232, log_level="info")

def main():
    """Main application entry point"""
    try:
        # Start API in a separate thread
        api_thread = threading.Thread(target=start_api, daemon=True)
        api_thread.start()

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