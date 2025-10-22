"""
Dashboard for NetGuardian
Main application interface after login - Adobe Creative Cloud inspired design
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import logging
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.file_manager.file_handler import FileHandler

logger = logging.getLogger(__name__)

class Dashboard:
    def __init__(self, parent, auth_manager, db_manager, logout_callback, colors):
        self.parent = parent
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        self.logout_callback = logout_callback
        self.colors = colors
        self.file_handler = FileHandler(db_manager, auth_manager.get_current_user()['id'])
        
        # Current view filter
        self.current_filter = "all"  # all, documents, images, archives
        
        # Create main container
        self.main_frame = ctk.CTkFrame(parent, fg_color=colors['dark'])
        self.main_frame.pack(fill="both", expand=True)
        
        self.create_dashboard_interface()
        self.refresh_file_list()
    
    def create_dashboard_interface(self):
        """Create the main dashboard interface - Adobe CC inspired"""
        
        # Create left sidebar and main content area
        self.create_sidebar()
        self.create_main_content()
    
    def create_sidebar(self):
        """Create left navigation sidebar"""
        sidebar = ctk.CTkFrame(self.main_frame, fg_color=self.colors['sidebar'], width=220)
        sidebar.pack(side="left", fill="y", padx=0, pady=0)
        sidebar.pack_propagate(False)

        # App title in sidebar
        app_title = ctk.CTkLabel(
            sidebar,
            text="NetGuardian",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['primary']
        )
        app_title.pack(pady=(30, 10), padx=20)

        # User info
        user_frame = ctk.CTkFrame(sidebar, fg_color=self.colors['gray'], corner_radius=8)
        user_frame.pack(pady=(0, 20), padx=20, fill="x")

        user_label = ctk.CTkLabel(
            user_frame,
            text=f"  👤  {self.auth_manager.get_current_user()['username']}",
            font=ctk.CTkFont(size=13),
            text_color=self.colors['light'],
            anchor="w"
        )
        user_label.pack(anchor="w", pady=10, padx=5)

        # Separator
        separator1 = ctk.CTkFrame(sidebar, fg_color=self.colors['gray'], height=1)
        separator1.pack(fill="x", padx=20, pady=10)

        # Navigation Section
        nav_label = ctk.CTkLabel(
            sidebar,
            text="NAVIGATION",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=self.colors['secondary'],
            anchor="w"
        )
        nav_label.pack(padx=20, pady=(10, 10), anchor="w")

        # All Files button
        self.nav_all_btn = ctk.CTkButton(
            sidebar,
            text="  📁  All Files",
            command=lambda: self.switch_filter("all"),
            width=180,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary'],
            anchor="w",
            corner_radius=8,
            text_color=self.colors['light']
        )
        self.nav_all_btn.pack(padx=20, pady=5, anchor="w")

        # Upload button
        self.nav_upload_btn = ctk.CTkButton(
            sidebar,
            text="  ⬆️  Upload",
            command=self.upload_files,
            width=180,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color=self.colors['gray'],
            anchor="w",
            corner_radius=8,
            text_color=self.colors['light'],
            border_width=0
        )
        self.nav_upload_btn.pack(padx=20, pady=5, anchor="w")

        # Separator
        separator2 = ctk.CTkFrame(sidebar, fg_color=self.colors['gray'], height=1)
        separator2.pack(fill="x", padx=20, pady=15)
        
        # Categories Section
        cat_label = ctk.CTkLabel(
            sidebar,
            text="CATEGORIES",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#808080",
            anchor="w"
        )
        cat_label.pack(padx=20, pady=(10, 10), anchor="w")
        
        # Documents button
        self.nav_docs_btn = ctk.CTkButton(
            sidebar,
            text="  📄  Documents",
            command=lambda: self.switch_filter("documents"),
            width=180,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color="#3A3A3A",
            anchor="w",
            corner_radius=8,
            text_color="#CCCCCC",
            border_width=0
        )
        self.nav_docs_btn.pack(padx=20, pady=5, anchor="w")
        
        # Images button
        self.nav_images_btn = ctk.CTkButton(
            sidebar,
            text="  🖼️  Images",
            command=lambda: self.switch_filter("images"),
            width=180,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color="#3A3A3A",
            anchor="w",
            corner_radius=8,
            text_color="#CCCCCC",
            border_width=0
        )
        self.nav_images_btn.pack(padx=20, pady=5, anchor="w")
        
        # Archives button
        self.nav_archives_btn = ctk.CTkButton(
            sidebar,
            text="  📦  Archives",
            command=lambda: self.switch_filter("archives"),
            width=180,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color="#3A3A3A",
            anchor="w",
            corner_radius=8,
            text_color="#CCCCCC",
            border_width=0
        )
        self.nav_archives_btn.pack(padx=20, pady=5, anchor="w")
        
        # Spacer
        spacer = ctk.CTkFrame(sidebar, fg_color="transparent")
        spacer.pack(expand=True)
        
        # Separator
        separator3 = ctk.CTkFrame(sidebar, fg_color="#404040", height=1)
        separator3.pack(fill="x", padx=20, pady=15)
        
        # Settings section
        settings_label = ctk.CTkLabel(
            sidebar,
            text="SETTINGS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#808080",
            anchor="w"
        )
        settings_label.pack(padx=20, pady=(10, 10), anchor="w")
        
        # Logout button
        logout_btn = ctk.CTkButton(
            sidebar,
            text="  🚪  Logout",
            command=self.logout_callback,
            width=180,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color="#FF6B6B",
            text_color="#CCCCCC",
            anchor="w",
            corner_radius=8,
            border_width=0
        )
        logout_btn.pack(padx=20, pady=(5, 30), anchor="w")
    
    def create_main_content(self):
        """Create main content area"""
        # Main content container
        content_container = ctk.CTkFrame(self.main_frame, fg_color="#1A1A1A")
        content_container.pack(side="right", fill="both", expand=True)
        
        # Top bar with search
        self.create_top_bar(content_container)
        
        # Tab navigation (Desktop/Mobile/Web style)
        self.create_tab_navigation(content_container)
        
        # Hero banner
        self.create_hero_banner(content_container)
        
        # Files section
        self.create_files_section(content_container)
    
    def create_top_bar(self, parent):
        """Create top bar with search and actions"""
        top_bar = ctk.CTkFrame(parent, fg_color="#2A2A2A", height=60)
        top_bar.pack(fill="x", padx=0, pady=0)
        top_bar.pack_propagate(False)
        
        # Search bar
        search_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        search_frame.pack(side="left", padx=20, pady=15)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search files...",
            width=300,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="#1A1A1A",
            border_color="#404040"
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        # Right side actions
        actions_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        actions_frame.pack(side="right", padx=20, pady=15)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            actions_frame,
            text="🔄",
            command=self.refresh_file_list,
            width=35,
            height=35,
            font=ctk.CTkFont(size=16),
            fg_color="#1A1A1A",
            hover_color="#3A3A3A",
            corner_radius=6
        )
        refresh_btn.pack(side="right", padx=5)
        
        # Settings icon
        settings_btn = ctk.CTkButton(
            actions_frame,
            text="⚙️",
            command=self.show_settings,
            width=35,
            height=35,
            font=ctk.CTkFont(size=16),
            fg_color="#1A1A1A",
            hover_color="#3A3A3A",
            corner_radius=6
        )
        settings_btn.pack(side="right", padx=5)
    
    def create_tab_navigation(self, parent):
        """Create tab navigation (All Apps/Desktop/Mobile/Web style)"""
        tab_frame = ctk.CTkFrame(parent, fg_color="#2A2A2A", height=50)
        tab_frame.pack(fill="x", padx=0, pady=0)
        tab_frame.pack_propagate(False)
        
        # Tabs container
        tabs_container = ctk.CTkFrame(tab_frame, fg_color="transparent")
        tabs_container.pack(pady=10, padx=30)
        
        # All Files tab
        self.tab_all = ctk.CTkButton(
            tabs_container,
            text="All Files",
            command=lambda: self.switch_view_tab("all"),
            width=100,
            height=30,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color="#3A3A3A",
            border_width=0,
            corner_radius=0
        )
        self.tab_all.pack(side="left", padx=5)
        
        # Recent tab
        self.tab_recent = ctk.CTkButton(
            tabs_container,
            text="Recent",
            command=lambda: self.switch_view_tab("recent"),
            width=100,
            height=30,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color="#3A3A3A",
            border_width=0,
            corner_radius=0
        )
        self.tab_recent.pack(side="left", padx=5)
        
        # Shared tab
        self.tab_shared = ctk.CTkButton(
            tabs_container,
            text="Shared",
            command=lambda: self.switch_view_tab("shared"),
            width=100,
            height=30,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color="#3A3A3A",
            border_width=0,
            corner_radius=0
        )
        self.tab_shared.pack(side="left", padx=5)
        
        # Highlight current tab
        self.highlight_tab(self.tab_all)
    
    def create_hero_banner(self, parent):
        """Create hero banner similar to Adobe CC"""
        banner_frame = ctk.CTkFrame(
            parent,
            fg_color="#2A2A2A",
            height=200,
            corner_radius=12
        )
        banner_frame.pack(fill="x", padx=30, pady=(20, 20))
        banner_frame.pack_propagate(False)
        
        # Create gradient effect with overlapping frames
        gradient_frame = ctk.CTkFrame(banner_frame, fg_color="#3A4A6A", corner_radius=12)
        gradient_frame.place(relwidth=1, relheight=1)
        
        # Content overlay
        content_frame = ctk.CTkFrame(gradient_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Welcome text
        welcome_title = ctk.CTkLabel(
            content_frame,
            text="Welcome to NetGuardian",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="white"
        )
        welcome_title.pack(anchor="w", pady=(10, 5))
        
        subtitle = ctk.CTkLabel(
            content_frame,
            text="Secure cloud storage for all your files. Upload, manage and share with ease.",
            font=ctk.CTkFont(size=14),
            text_color="#CCCCCC"
        )
        subtitle.pack(anchor="w", pady=(0, 20))
        
        # Action button
        upload_banner_btn = ctk.CTkButton(
            content_frame,
            text="Upload Files",
            command=self.upload_files,
            width=140,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="white",
            text_color="#1A1A1A",
            hover_color="#E0E0E0",
            corner_radius=8
        )
        upload_banner_btn.pack(anchor="w")
    
    def create_files_section(self, parent):
        """Create files section with card layout"""
        # Files container
        files_container = ctk.CTkFrame(parent, fg_color="transparent")
        files_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        # Section header
        header_frame = ctk.CTkFrame(files_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))
        
        self.section_title = ctk.CTkLabel(
            header_frame,
            text="All Files",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white",
            anchor="w"
        )
        self.section_title.pack(side="left")
        
        # Upload folder button
        upload_folder_btn = ctk.CTkButton(
            header_frame,
            text="📂 Upload Folder",
            command=self.upload_folder,
            width=140,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="#3A3A3A",
            hover_color="#4A4A4A",
            corner_radius=8
        )
        upload_folder_btn.pack(side="right", padx=5)
        
        # Files scrollable area with card grid
        self.files_scrollable = ctk.CTkScrollableFrame(
            files_container,
            fg_color="transparent",
            scrollbar_fg_color="#2A2A2A"
        )
        self.files_scrollable.pack(fill="both", expand=True)
        
        # Configure grid for card layout
        self.files_scrollable.grid_columnconfigure(0, weight=1)
        self.files_scrollable.grid_columnconfigure(1, weight=1)
        self.files_scrollable.grid_columnconfigure(2, weight=1)
    
    def upload_files(self):
        """Handle file upload"""
        try:
            file_paths = filedialog.askopenfilenames(
                title="Select files to upload",
                filetypes=[
                    ("All files", "*.*"),
                    ("Text files", "*.txt"),
                    ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("Documents", "*.pdf *.doc *.docx *.xls *.xlsx"),
                    ("Archives", "*.zip *.rar *.7z")
                ]
            )
            
            if file_paths:
                self.process_uploads(file_paths)
                
        except Exception as e:
            logger.error(f"File upload error: {e}")
            messagebox.showerror("Error", "Failed to upload files")
    
    def upload_folder(self):
        """Handle folder upload"""
        try:
            folder_path = filedialog.askdirectory(title="Select folder to upload")
            
            if folder_path:
                # Get all files in folder and subfolders
                file_paths = []
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_paths.append(os.path.join(root, file))
                
                if file_paths:
                    self.process_uploads(file_paths)
                else:
                    messagebox.showinfo("Info", "Selected folder is empty")
                    
        except Exception as e:
            logger.error(f"Folder upload error: {e}")
            messagebox.showerror("Error", "Failed to upload folder")
    
    def process_uploads(self, file_paths):
        """Process multiple file uploads"""
        try:
            # Create progress dialog
            progress_dialog = UploadProgressDialog(self.parent, len(file_paths), self.colors)
            
            uploaded = 0
            failed = 0
            
            for i, file_path in enumerate(file_paths):
                try:
                    success, message = self.file_handler.upload_file(file_path)
                    if success:
                        uploaded += 1
                    else:
                        failed += 1
                        logger.warning(f"Failed to upload {file_path}: {message}")
                    
                    # Update progress
                    progress_dialog.update_progress(i + 1, os.path.basename(file_path))
                    
                except Exception as e:
                    failed += 1
                    logger.error(f"Upload error for {file_path}: {e}")
            
            progress_dialog.close()
            
            # Show result
            if uploaded > 0:
                messagebox.showinfo("Upload Complete", 
                                  f"Successfully uploaded {uploaded} files.\n"
                                  f"Failed: {failed} files.")
                self.refresh_file_list()
            else:
                messagebox.showerror("Upload Failed", "No files were uploaded successfully.")
                
        except Exception as e:
            logger.error(f"Upload process error: {e}")
            messagebox.showerror("Error", "Upload process failed")
    
    def switch_filter(self, filter_type):
        """Switch file category filter"""
        self.current_filter = filter_type
        
        # Update sidebar button colors
        buttons = {
            "all": self.nav_all_btn,
            "documents": self.nav_docs_btn,
            "images": self.nav_images_btn,
            "archives": self.nav_archives_btn
        }
        
        for key, btn in buttons.items():
            if key == filter_type:
                btn.configure(fg_color=self.colors['primary'])
            else:
                btn.configure(fg_color="transparent")
        
        self.refresh_file_list()
    
    def switch_view_tab(self, tab_name):
        """Switch between view tabs"""
        # Reset all tabs
        self.tab_all.configure(fg_color="transparent", text_color="white")
        self.tab_recent.configure(fg_color="transparent", text_color="white")
        self.tab_shared.configure(fg_color="transparent", text_color="white")
        
        # Highlight selected tab
        if tab_name == "all":
            self.highlight_tab(self.tab_all)
        elif tab_name == "recent":
            self.highlight_tab(self.tab_recent)
        elif tab_name == "shared":
            self.highlight_tab(self.tab_shared)
        
        self.refresh_file_list()
    
    def highlight_tab(self, tab_button):
        """Highlight the active tab"""
        tab_button.configure(text_color=self.colors['primary'])
    
    def on_search(self, event):
        """Handle search input"""
        search_term = self.search_entry.get().lower()
        self.refresh_file_list(search_term)
    
    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings functionality coming soon!")
    
    def refresh_file_list(self, search_term=""):
        """Refresh the file list display with card layout"""
        try:
            # Clear current list
            for widget in self.files_scrollable.winfo_children():
                widget.destroy()
            
            # Get user files
            files = self.file_handler.get_user_files()
            
            # Filter by category
            if self.current_filter != "all":
                files = self.filter_files_by_type(files, self.current_filter)
            
            # Filter by search term
            if search_term:
                files = [f for f in files if search_term in f['original_name'].lower()]
            
            # Update section title
            filter_names = {
                "all": "All Files",
                "documents": "Documents",
                "images": "Images",
                "archives": "Archives"
            }
            self.section_title.configure(text=filter_names.get(self.current_filter, "All Files"))
            
            if not files:
                # Empty state
                empty_frame = ctk.CTkFrame(self.files_scrollable, fg_color="transparent")
                empty_frame.grid(row=0, column=0, columnspan=3, pady=50)
                
                no_files_label = ctk.CTkLabel(
                    empty_frame,
                    text="📁 No files found" if search_term else "📁 No files uploaded yet",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="#666666"
                )
                no_files_label.pack(pady=10)
                
                hint_label = ctk.CTkLabel(
                    empty_frame,
                    text="Upload files to get started!" if not search_term else "Try a different search term",
                    font=ctk.CTkFont(size=13),
                    text_color="#888888"
                )
                hint_label.pack()
                return
            
            # Display files in card grid (3 columns)
            row = 0
            col = 0
            for file_data in files:
                self.create_file_card(file_data, row, col)
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
                
        except Exception as e:
            logger.error(f"Failed to refresh file list: {e}")
    
    def filter_files_by_type(self, files, filter_type):
        """Filter files by type"""
        extensions = {
            "documents": ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx', '.ppt', '.pptx'],
            "images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
            "archives": ['.zip', '.rar', '.7z', '.tar', '.gz']
        }
        
        if filter_type not in extensions:
            return files
        
        valid_extensions = extensions[filter_type]
        return [f for f in files if any(f['original_name'].lower().endswith(ext) for ext in valid_extensions)]
    
    def create_file_card(self, file_data, row, col):
        """Create a file card widget (Adobe CC inspired)"""
        # Card frame
        card_frame = ctk.CTkFrame(
            self.files_scrollable,
            fg_color="#2A2A2A",
            corner_radius=12,
            width=280,
            height=180
        )
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card_frame.grid_propagate(False)
        
        # File icon/preview area
        icon_frame = ctk.CTkFrame(card_frame, fg_color="#3A3A3A", height=100, corner_radius=8)
        icon_frame.pack(fill="x", padx=10, pady=(10, 5))
        icon_frame.pack_propagate(False)
        
        # File type icon
        file_extension = file_data['original_name'].split('.')[-1].lower()
        icon_emoji = self.get_file_icon(file_extension)
        
        icon_label = ctk.CTkLabel(
            icon_frame,
            text=icon_emoji,
            font=ctk.CTkFont(size=48),
            text_color="#B0B0B0"
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # File info area
        info_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # File name (truncated if too long)
        file_name = file_data['original_name']
        if len(file_name) > 28:
            file_name = file_name[:25] + "..."
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=file_name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        name_label.pack(anchor="w", pady=(5, 3))
        
        # File size - use formatted size if available
        if 'file_size_formatted' in file_data:
            size_text = file_data['file_size_formatted']
        else:
            size_mb = file_data['file_size'] / (1024 * 1024)
            size_text = f"{size_mb:.2f} MB" if size_mb >= 0.01 else f"{file_data['file_size'] / 1024:.2f} KB"
        
        size_label = ctk.CTkLabel(
            info_frame,
            text=size_text,
            font=ctk.CTkFont(size=12),
            text_color="#909090",
            anchor="w"
        )
        size_label.pack(anchor="w")
        
        # Action buttons area
        actions_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        actions_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Download button (styled like Adobe CC "Open" button)
        download_btn = ctk.CTkButton(
            actions_frame,
            text="Open",
            command=lambda f=file_data: self.download_file(f),
            width=110,
            height=34,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#FFFFFF",
            text_color="#1A1A1A",
            hover_color="#E0E0E0",
            corner_radius=17
        )
        download_btn.pack(side="left", padx=(0, 8))
        
        # More options button (three dots)
        more_btn = ctk.CTkButton(
            actions_frame,
            text="⋯",
            command=lambda f=file_data: self.show_file_options(f),
            width=34,
            height=34,
            font=ctk.CTkFont(size=20, weight="bold"),
            fg_color="transparent",
            hover_color="#3A3A3A",
            corner_radius=17,
            border_width=1,
            border_color="#505050",
            text_color="#B0B0B0"
        )
        more_btn.pack(side="left", padx=(0, 8))
        
        # Delete button (icon)
        delete_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️",
            command=lambda f=file_data: self.delete_file(f),
            width=34,
            height=34,
            font=ctk.CTkFont(size=16),
            fg_color="transparent",
            hover_color="#FF6B6B",
            corner_radius=17,
            border_width=1,
            border_color="#505050",
            text_color="#FF6B6B"
        )
        delete_btn.pack(side="right")
    
    def get_file_icon(self, extension):
        """Get emoji icon for file type"""
        icons = {
            'pdf': '📄',
            'doc': '📝', 'docx': '📝',
            'xls': '📊', 'xlsx': '📊',
            'ppt': '📊', 'pptx': '📊',
            'txt': '📃',
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'bmp': '🖼️',
            'zip': '📦', 'rar': '📦', '7z': '📦', 'tar': '📦', 'gz': '📦',
            'mp3': '🎵', 'wav': '🎵', 'mp4': '🎬', 'avi': '🎬',
            'py': '🐍', 'js': '📜', 'html': '🌐', 'css': '🎨',
        }
        return icons.get(extension, '📁')
    
    def show_file_options(self, file_data):
        """Show file options menu"""
        # Create a simple options dialog
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("File Options")
        dialog.geometry("300x200")
        dialog.resizable(False, False)
        
        # Make modal
        try:
            dialog.transient(self.parent)
        except:
            pass  # transient may not work with all window types
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 150
        y = (dialog.winfo_screenheight() // 2) - 100
        dialog.geometry(f'300x200+{x}+{y}')
        
        # File name label
        name_label = ctk.CTkLabel(
            dialog,
            text=file_data['original_name'],
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        name_label.pack(pady=20)
        
        # Download button
        download_opt_btn = ctk.CTkButton(
            dialog,
            text="📥 Download",
            command=lambda: [self.download_file(file_data), dialog.destroy()],
            width=200,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color=self.colors['primary'],
            hover_color=self.colors['secondary']
        )
        download_opt_btn.pack(pady=5)
        
        # Share button (placeholder)
        share_btn = ctk.CTkButton(
            dialog,
            text="🔗 Share Link",
            command=lambda: messagebox.showinfo("Share", "Share functionality coming soon!"),
            width=200,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="#3A3A3A",
            hover_color="#4A4A4A"
        )
        share_btn.pack(pady=5)
        
        # Close button
        close_btn = ctk.CTkButton(
            dialog,
            text="Close",
            command=dialog.destroy,
            width=200,
            height=35,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color="#3A3A3A"
        )
        close_btn.pack(pady=5)
    
    def download_file(self, file_data):
        """Download a file"""
        try:
            save_path = filedialog.asksaveasfilename(
                title="Save file as",
                initialname=file_data['original_name'],
                defaultextension=""
            )
            
            if save_path:
                success, message = self.file_handler.download_file(file_data['id'], save_path)
                if success:
                    messagebox.showinfo("Success", "File downloaded successfully!")
                else:
                    messagebox.showerror("Error", f"Download failed: {message}")
                    
        except Exception as e:
            logger.error(f"Download error: {e}")
            messagebox.showerror("Error", "Failed to download file")
    
    def delete_file(self, file_data):
        """Delete a file"""
        try:
            result = messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete '{file_data['original_name']}'?\n\nThis action cannot be undone."
            )
            
            if result:
                success, message = self.file_handler.delete_file(file_data['id'])
                if success:
                    messagebox.showinfo("Success", "File deleted successfully!")
                    self.refresh_file_list()
                else:
                    messagebox.showerror("Error", f"Delete failed: {message}")
                    
        except Exception as e:
            logger.error(f"Delete error: {e}")
            messagebox.showerror("Error", "Failed to delete file")
    
    def destroy(self):
        """Clean up the dashboard"""
        self.main_frame.destroy()


class UploadProgressDialog:
    def __init__(self, parent, total_files, colors):
        self.total_files = total_files
        self.colors = colors
        
        # Create dialog
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Uploading Files")
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        
        # Make modal
        try:
            self.dialog.transient(parent)
        except:
            pass  # transient may not work with all window types
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (200)
        y = (self.dialog.winfo_screenheight() // 2) - (75)
        self.dialog.geometry(f'400x150+{x}+{y}')
        
        # Progress label
        self.progress_label = ctk.CTkLabel(
            self.dialog,
            text="Preparing upload...",
            font=ctk.CTkFont(size=14),
            text_color=colors['light']
        )
        self.progress_label.pack(pady=20)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self.dialog,
            width=350,
            height=20,
            fg_color=colors['gray'],
            progress_color=colors['primary']
        )
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.dialog,
            text="0 / " + str(total_files),
            font=ctk.CTkFont(size=12),
            text_color=colors['light']
        )
        self.status_label.pack(pady=5)
    
    def update_progress(self, current, filename):
        """Update progress display"""
        progress = current / self.total_files
        self.progress_bar.set(progress)
        self.progress_label.configure(text=f"Uploading: {filename}")
        self.status_label.configure(text=f"{current} / {self.total_files}")
        self.dialog.update()
    
    def close(self):
        """Close the progress dialog"""
        self.dialog.destroy()