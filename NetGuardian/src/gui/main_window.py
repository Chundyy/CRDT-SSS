"""
Main Window for NetGuardian
Modern desktop interface using CustomTkinter
"""

import customtkinter as ctk
from tkinter import messagebox
import logging
from .login_window import LoginWindow

logger = logging.getLogger(__name__)

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class MainWindow:
    def __init__(self, root, auth_manager, db_manager):
        self.root = root
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        
        # Configure main window
        self.root.title("NetGuardian - Cloud File Manager")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Set window icon (placeholder)
        # self.root.iconbitmap("assets/icons/netguardian.ico")
        
        # Modern Adobe CC inspired color scheme
        self.colors = {
            'primary': '#4A9EFF',      # Blue accent
            'secondary': '#3A7FCC',    # Darker blue
            'accent': '#FF6B6B',       # Soft red accent
            'dark': '#1A1A1A',         # Main background
            'darker': '#121212',       # Darkest background
            'sidebar': '#2A2A2A',      # Sidebar gray
            'light': '#FFFFFF',        # White text
            'gray': '#3A3A3A'          # Gray elements
        }
        
        # Apply custom styling
        self._configure_styles()
        
        # Current window state
        self.current_window = None
        
        # Start with login window
        self.show_login()
        
        # Center window on screen
        self._center_window()
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        logger.info("Main window initialized")
    
    def _configure_styles(self):
        """Configure custom styling for the application"""
        # Configure custom colors
        ctk.set_appearance_mode("dark")
        
        # Main window background
        self.root.configure(bg=self.colors['dark'])
    
    def _center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_login(self):
        """Show the login window"""
        try:
            if self.current_window:
                self.current_window.destroy()
            
            self.current_window = LoginWindow(
                self.root, 
                self.auth_manager, 
                self.on_login_success,
                self.colors
            )
            logger.info("Login window displayed")
            
        except Exception as e:
            logger.error(f"Failed to show login window: {e}")
            messagebox.showerror("Error", "Failed to load login window")
    
    def show_dashboard(self):
        """Show the main dashboard"""
        try:
            # Import Dashboard only when needed to avoid early dependency loading
            from .dashboard import Dashboard
            
            if self.current_window:
                self.current_window.destroy()
            
            self.current_window = Dashboard(
                self.root,
                self.auth_manager,
                self.db_manager,
                self.on_logout,
                self.colors
            )
            logger.info("Dashboard displayed")
            
        except Exception as e:
            logger.error(f"Failed to show dashboard: {e}")
            messagebox.showerror("Error", f"Failed to load dashboard: {str(e)}")
    
    def on_login_success(self, user_data):
        """Handle successful login"""
        logger.info(f"Login successful for user: {user_data.get('username', 'Unknown')}")
        self.show_dashboard()
    
    def on_logout(self):
        """Handle user logout"""
        self.auth_manager.logout_user()
        logger.info("User logged out")
        self.show_login()
    
    def run(self):
        """Start the application main loop"""
        try:
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Application crashed: {e}")
            messagebox.showerror("Critical Error", f"Application crashed: {str(e)}")
    
    def on_closing(self):
        """Handle application closing"""
        try:
            # Cleanup operations
            if self.auth_manager.is_authenticated():
                self.auth_manager.logout_user()
            
            if self.db_manager:
                self.db_manager.disconnect()
            
            self.root.destroy()
            logger.info("Application closed successfully")
            
        except Exception as e:
            logger.error(f"Error during application shutdown: {e}")
            self.root.destroy()