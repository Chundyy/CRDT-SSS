"""
Login Window for NetGuardian
Handles user authentication interface
"""

import customtkinter as ctk
from tkinter import messagebox
import logging

logger = logging.getLogger(__name__)

class LoginWindow:
    def __init__(self, parent, auth_manager, login_callback, colors):
        self.parent = parent
        self.auth_manager = auth_manager
        self.login_callback = login_callback
        self.colors = colors
        
        # Create main container
        self.main_frame = ctk.CTkFrame(parent, fg_color=colors['dark'])
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        try:
            self.create_login_interface()
        except Exception as e:
            logger.error(f"Failed to create login interface: {e}")
            # Show a simple error message if the fancy interface fails
            error_label = ctk.CTkLabel(
                self.main_frame,
                text=f"Failed to load login interface:\n{str(e)}\n\nPlease check the application logs.",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            error_label.pack(expand=True)
            raise
    
    def create_login_interface(self):
        """Create the modern login interface"""
        
        # Create two-column layout
        left_panel = ctk.CTkFrame(self.main_frame, fg_color="#2A3A5A", corner_radius=0)
        left_panel.pack(side="left", fill="both", expand=True)
        
        right_panel = ctk.CTkFrame(self.main_frame, fg_color=self.colors['dark'], corner_radius=0)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Left panel - Branding
        branding_frame = ctk.CTkFrame(left_panel, fg_color="#2A3A5A")
        branding_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo/Icon
        logo_label = ctk.CTkLabel(
            branding_frame,
            text="🛡️",
            font=ctk.CTkFont(size=80)
        )
        logo_label.pack(pady=(0, 20))
        
        # Title
        title_label = ctk.CTkLabel(
            branding_frame,
            text="NetGuardian",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ctk.CTkLabel(
            branding_frame,
            text="Secure Cloud File Management",
            font=ctk.CTkFont(size=16),
            text_color="#CCCCCC"
        )
        subtitle_label.pack()
        
        features_label = ctk.CTkLabel(
            branding_frame,
            text="✓ End-to-end encryption\n✓ Unlimited storage\n✓ Fast file sharing",
            font=ctk.CTkFont(size=13),
            text_color="#AAAAAA",
            justify="left"
        )
        features_label.pack(pady=(30, 0))
        
        # Right panel - Login form
        login_container = ctk.CTkFrame(right_panel, fg_color=self.colors['dark'])
        login_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Login form title
        form_title = ctk.CTkLabel(
            login_container,
            text="Welcome Back",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        form_title.pack(pady=(0, 10))
        
        form_subtitle = ctk.CTkLabel(
            login_container,
            text="Sign in to your account",
            font=ctk.CTkFont(size=14),
            text_color="#888888"
        )
        form_subtitle.pack(pady=(0, 40))
        
        # Username field with label
        username_label = ctk.CTkLabel(
            login_container,
            text="Username",
            font=ctk.CTkFont(size=13),
            text_color="#AAAAAA",
            anchor="w"
        )
        username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            login_container,
            placeholder_text="Enter your username",
            width=350,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color="#2A2A2A",
            border_color="#404040",
            border_width=1
        )
        self.username_entry.pack(pady=(0, 20))
        
        # Password field with label
        password_label = ctk.CTkLabel(
            login_container,
            text="Password",
            font=ctk.CTkFont(size=13),
            text_color="#AAAAAA",
            anchor="w"
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            login_container,
            placeholder_text="Enter your password",
            show="●",
            width=350,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color="#2A2A2A",
            border_color="#404040",
            border_width=1
        )
        self.password_entry.pack(pady=(0, 10))
        
        # Forgot password link
        forgot_btn = ctk.CTkButton(
            login_container,
            text="Forgot password?",
            command=lambda: messagebox.showinfo("Reset", "Password reset coming soon!"),
            width=350,
            height=25,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['dark'],
            text_color=self.colors['primary'],
            hover_color="#2A2A2A",
            anchor="e"
        )
        forgot_btn.pack(pady=(0, 25))
        
        # Login button
        login_btn = ctk.CTkButton(
            login_container,
            text="Sign In",
            command=self.handle_login,
            width=350,
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary'],
            corner_radius=8
        )
        login_btn.pack(pady=(0, 20))
        
        # Divider
        divider_frame = ctk.CTkFrame(login_container, fg_color=self.colors['dark'])
        divider_frame.pack(fill="x", pady=15)
        
        ctk.CTkFrame(divider_frame, fg_color="#404040", height=1).pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkLabel(divider_frame, text="OR", font=ctk.CTkFont(size=11), text_color="#666666").pack(side="left")
        ctk.CTkFrame(divider_frame, fg_color="#404040", height=1).pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Register section
        register_frame = ctk.CTkFrame(login_container, fg_color=self.colors['dark'])
        register_frame.pack(pady=15)
        
        register_label = ctk.CTkLabel(
            register_frame,
            text="Don't have an account?",
            font=ctk.CTkFont(size=13),
            text_color="#888888"
        )
        register_label.pack(side="left", padx=(0, 5))
        
        register_btn = ctk.CTkButton(
            register_frame,
            text="Create Account",
            command=self.show_register,
            width=120,
            height=30,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=self.colors['dark'],
            text_color=self.colors['primary'],
            hover_color="#2A2A2A",
            border_width=1,
            border_color=self.colors['primary'],
            corner_radius=6
        )
        register_btn.pack(side="left")
        
        # Bind Enter key to login
        self.parent.bind('<Return>', lambda event: self.handle_login())
        
        # Focus on username field
        self.username_entry.focus()
    
    def handle_login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        try:
            success, message = self.auth_manager.login_user(username, password)
            
            if success:
                user_data = self.auth_manager.get_current_user()
                self.login_callback(user_data)
            else:
                messagebox.showerror("Login Failed", message)
                self.password_entry.delete(0, 'end')
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            messagebox.showerror("Error", "An error occurred during login")
    
    def show_register(self):
        """Show registration dialog"""
        RegisterDialog(self.parent, self.auth_manager, self.colors)
    
    def destroy(self):
        """Clean up the login window"""
        self.main_frame.destroy()


class RegisterDialog:
    def __init__(self, parent, auth_manager, colors):
        self.auth_manager = auth_manager
        self.colors = colors
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Register New Account")
        self.dialog.geometry("400x560")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        try:
            self.dialog.transient(parent)
        except:
            pass  # transient may not work with all window types
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (200)
        y = (self.dialog.winfo_screenheight() // 2) - (280)
        self.dialog.geometry(f'400x560+{x}+{y}')
        
        self.create_register_form()
    
    def create_register_form(self):
        """Create modern registration form"""
        
        # Main container
        container = ctk.CTkFrame(self.dialog, fg_color=self.colors['dark'])
        container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Title
        title_label = ctk.CTkLabel(
            container,
            text="Create Account",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="white"
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ctk.CTkLabel(
            container,
            text="Join NetGuardian today",
            font=ctk.CTkFont(size=13),
            text_color="#888888"
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Username field
        username_label = ctk.CTkLabel(
            container,
            text="Username",
            font=ctk.CTkFont(size=12),
            text_color="#AAAAAA",
            anchor="w"
        )
        username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            container,
            placeholder_text="Choose a username",
            width=340,
            height=42,
            font=ctk.CTkFont(size=13),
            fg_color="#2A2A2A",
            border_color="#404040",
            border_width=1
        )
        self.username_entry.pack(pady=(0, 15))
        
        # Email field
        email_label = ctk.CTkLabel(
            container,
            text="Email Address",
            font=ctk.CTkFont(size=12),
            text_color="#AAAAAA",
            anchor="w"
        )
        email_label.pack(anchor="w", pady=(0, 5))
        
        self.email_entry = ctk.CTkEntry(
            container,
            placeholder_text="your@email.com",
            width=340,
            height=42,
            font=ctk.CTkFont(size=13),
            fg_color="#2A2A2A",
            border_color="#404040",
            border_width=1
        )
        self.email_entry.pack(pady=(0, 15))
        
        # Password field
        password_label = ctk.CTkLabel(
            container,
            text="Password",
            font=ctk.CTkFont(size=12),
            text_color="#AAAAAA",
            anchor="w"
        )
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            container,
            placeholder_text="Create a password",
            show="●",
            width=340,
            height=42,
            font=ctk.CTkFont(size=13),
            fg_color="#2A2A2A",
            border_color="#404040",
            border_width=1
        )
        self.password_entry.pack(pady=(0, 15))
        
        # Confirm password field
        confirm_label = ctk.CTkLabel(
            container,
            text="Confirm Password",
            font=ctk.CTkFont(size=12),
            text_color="#AAAAAA",
            anchor="w"
        )
        confirm_label.pack(anchor="w", pady=(0, 5))
        
        self.confirm_password_entry = ctk.CTkEntry(
            container,
            placeholder_text="Confirm your password",
            show="●",
            width=340,
            height=42,
            font=ctk.CTkFont(size=13),
            fg_color="#2A2A2A",
            border_color="#404040",
            border_width=1
        )
        self.confirm_password_entry.pack(pady=(0, 25))
        
        # Register button
        register_btn = ctk.CTkButton(
            container,
            text="Create Account",
            command=self.handle_register,
            width=340,
            height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary'],
            corner_radius=8
        )
        register_btn.pack(pady=(0, 15))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            container,
            text="Cancel",
            command=self.dialog.destroy,
            width=340,
            height=44,
            font=ctk.CTkFont(size=13),
            fg_color="#2A2A2A",
            hover_color="#3A3A3A",
            border_width=1,
            border_color="#404040",
            corner_radius=8
        )
        cancel_btn.pack()
        
        # Focus on username field
        self.username_entry.focus()
    
    def handle_register(self):
        """Handle registration attempt"""
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # Validation
        if not all([username, email, password, confirm_password]):
            messagebox.showerror("Error", "Please fill in all fields")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        
        if "@" not in email:
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        
        try:
            success, message = self.auth_manager.register_user(username, email, password)
            
            if success:
                messagebox.showinfo("Success", "Account created successfully! You can now login.")
                self.dialog.destroy()
            else:
                messagebox.showerror("Registration Failed", message)
                
        except Exception as e:
            logger.error(f"Registration error: {e}")
            messagebox.showerror("Error", "An error occurred during registration")