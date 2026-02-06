import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import logging
import json
from datetime import datetime

# ==========================================
# CONFIGURATION AND UTILITIES
# ==========================================

# Set up logging
logging.basicConfig(filename='file_organizer.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Default extensions map
extensions_map = {
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg'],
    'Documents': ['.pdf', '.docx', '.txt', '.xlsx', '.pptx', '.doc', '.xls', '.ppt'],
    'Videos': ['.mp4', '.mkv', '.mov', '.avi', '.wmv', '.flv', '.mpv'],
    'Music': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
    'Programs': ['.exe', '.msi', '.apk', '.dmg', '.deb'],
    'Others': []
}

# Load config
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'theme': 'blue', 'mode': 'Light', 'recent_folders': [], 'activity_history': []}

# Save config
def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)

config = load_config()
# Use a neutral theme - we'll handle colors ourselves
ctk.set_appearance_mode(config.get('mode', 'Light'))

# ==========================================
# CORE LOGIC FUNCTIONS
# ==========================================

def create_folders(target_path):
    """Creates category folders if they don't exist in the target path."""
    for folder_name in extensions_map.keys():
        folder_path = os.path.join(target_path, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logging.info(f"Created folder: {folder_path}")

def organize_files(target_path, progress_callback=None):
    """
    Organizes files in the target path by moving them to category folders.
    Returns the number of files moved and list of (old_path, new_path) tuples.
    """
    create_folders(target_path)
    files = os.listdir(target_path)
    moved_count = 0
    moved_files = []
    total_files = len([f for f in files if os.path.isfile(os.path.join(target_path, f))])

    for i, file in enumerate(files):
        if not os.path.isfile(os.path.join(target_path, file)):
            continue
        filename, extension = os.path.splitext(file)
        if extension == "":
            continue

        moved = False
        for folder_name, ext_list in extensions_map.items():
            if extension.lower() in ext_list:
                old_path = os.path.join(target_path, file)
                new_path = os.path.join(target_path, folder_name, file)
                try:
                    shutil.move(old_path, new_path)
                    moved_count += 1
                    moved = True
                    moved_files.append((old_path, new_path))
                    logging.info(f"Moved {file} to {folder_name}")
                    break
                except Exception as e:
                    logging.error(f"Error moving {file}: {e}")
                    messagebox.showerror("Error", f"Failed to move {file}: {e}")

        if progress_callback:
            progress_callback((i + 1) / total_files * 100)

    return moved_count, moved_files

def search_files(target_path, query):
    """Searches for files containing the query in name."""
    results = []
    for root, dirs, files in os.walk(target_path):
        for file in files:
            if query.lower() in file.lower():
                results.append(os.path.join(root, file))
    return results

def get_folder_stats(target_path):
    """Returns basic stats about the folder."""
    total_files = 0
    total_size = 0
    for root, dirs, files in os.walk(target_path):
        for file in files:
            total_files += 1
            try:
                total_size += os.path.getsize(os.path.join(root, file))
            except:
                pass
    return total_files, total_size

def get_file_breakdown(target_path):
    """Returns a dictionary of category -> file count for files in target path (not in subfolders)."""
    breakdown = {category: 0 for category in extensions_map.keys()}
    breakdown['Others'] = 0
    
    if not target_path or not os.path.exists(target_path):
        return breakdown
    
    try:
        files = [f for f in os.listdir(target_path) if os.path.isfile(os.path.join(target_path, f))]
        for file in files:
            _, extension = os.path.splitext(file)
            if extension == "":
                breakdown['Others'] += 1
                continue
            
            categorized = False
            for folder_name, ext_list in extensions_map.items():
                if extension.lower() in ext_list:
                    breakdown[folder_name] += 1
                    categorized = True
                    break
            
            if not categorized:
                breakdown['Others'] += 1
    except:
        pass
    
    return breakdown

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def get_file_info(file_path):
    """Get file information (size, modified date)"""
    try:
        stat = os.stat(file_path)
        size = stat.st_size
        modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        return size, modified
    except:
        return 0, "Unknown"

# ==========================================
# GUI CLASSES
# ==========================================

class FileOrganizerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("File Organizer")
        self.geometry("1200x750")
        self.current_view = "organize"
        self.target_path = None
        self.recent_folders = config.get('recent_folders', [])
        self.undo_stack = []
        self.activity_history = config.get('activity_history', [])
        
        # Color scheme - subtle teal accent
        self.accent_color = "#4A9E9E"
        self.update_colors()
        
        self.setup_ui()
        self.show_view("organize")
    
    def update_colors(self):
        """Update colors based on current theme"""
        mode = ctk.get_appearance_mode()
        if mode == "Dark":
            self.bg_primary = "#1a1a1a"
            self.bg_secondary = "#2d2d2d"
            self.bg_tertiary = "#3a3a3a"
            self.text_primary = "#e0e0e0"
            self.text_secondary = "#b0b0b0"
            self.border_color = "#404040"
        else:
            self.bg_primary = "#ffffff"
            self.bg_secondary = "#f5f5f5"
            self.bg_tertiary = "#e8e8e8"
            self.text_primary = "#1a1a1a"
            self.text_secondary = "#666666"
            self.border_color = "#d0d0d0"

    def setup_ui(self):
        # Top bar with title and theme toggle
        self.top_bar = ctk.CTkFrame(self, corner_radius=0, height=65, fg_color=self.bg_secondary)
        self.top_bar.pack(fill="x", side="top")
        self.top_bar.pack_propagate(False)
        
        title_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        title_frame.pack(side="left", padx=25, pady=15)
        
        self.title_label = ctk.CTkLabel(
            title_frame, 
            text="File Organizer", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            title_frame, 
            text="Organize your files with ease", 
            font=ctk.CTkFont(size=12),
            text_color=self.text_secondary
        )
        subtitle.pack(anchor="w")
        
        # Theme toggle in top right
        controls_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        controls_frame.pack(side="right", padx=25, pady=15)
        
        current_mode = ctk.get_appearance_mode()
        theme_text = "☀️ Light" if current_mode == "Dark" else "🌙 Dark"
        self.theme_btn = ctk.CTkButton(
            controls_frame, 
            text=theme_text,
            width=100,
            command=self.toggle_theme,
            fg_color=self.accent_color,
            hover_color="#3a7a7a"
        )
        self.theme_btn.pack(side="right", padx=(10, 0))
        
        help_btn = ctk.CTkButton(
            controls_frame, 
            text="?", 
            width=40,
            command=self.show_help,
            fg_color=self.bg_tertiary,
            hover_color=self.border_color
        )
        help_btn.pack(side="right")
        
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Sidebar navigation
        self.sidebar = ctk.CTkFrame(main_container, width=220, corner_radius=0, fg_color=self.bg_secondary)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)
        
        # Sidebar padding
        sidebar_content = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_content.pack(fill="both", expand=True, padx=15, pady=20)
        
        nav_label = ctk.CTkLabel(
            sidebar_content, 
            text="Navigation", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.text_secondary
        )
        nav_label.pack(anchor="w", pady=(0, 12))
        
        self.nav_buttons = {}
        nav_items = [
            ("Organize", "organize"),
            ("Search", "search"),
            ("Statistics", "stats"),
            ("Tools", "tools"),
            ("Settings", "settings")
        ]
        
        for display_name, view_name in nav_items:
            btn = ctk.CTkButton(
                sidebar_content,
                text=display_name,
                command=lambda v=view_name: self.show_view(v),
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color="transparent",
                hover_color=self.bg_tertiary,
                font=ctk.CTkFont(size=14)
            )
            btn.pack(fill="x", pady=4)
            self.nav_buttons[view_name] = btn
        
        # Main content area with padding
        self.main_frame = ctk.CTkScrollableFrame(main_container, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True, padx=30, pady=25)
        
        # Bottom status bar
        self.status_bar = ctk.CTkFrame(self, height=45, corner_radius=0, fg_color=self.bg_secondary)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar.pack_propagate(False)
        
        status_content = ctk.CTkFrame(self.status_bar, fg_color="transparent")
        status_content.pack(fill="both", expand=True, padx=25, pady=10)
        
        self.status_label = ctk.CTkLabel(
            status_content, 
            text="Ready", 
            anchor="w",
            font=ctk.CTkFont(size=12),
            text_color=self.text_secondary
        )
        self.status_label.pack(side="left", fill="x", expand=True)
        
        self.file_count_label = ctk.CTkLabel(
            status_content, 
            text="Files: 0", 
            font=ctk.CTkFont(size=12),
            text_color=self.text_secondary
        )
        self.file_count_label.pack(side="right")
        
        # Initialize common widgets
        self.path_entry = None
        self.search_entry = None
        self.search_results = None
        self.progress = None
    
    def toggle_theme(self):
        """Switch between light and dark mode"""
        current = ctk.get_appearance_mode()
        new_mode = "Light" if current == "Dark" else "Dark"
        ctk.set_appearance_mode(new_mode)
        config['mode'] = new_mode
        save_config(config)
        self.update_colors()
        
        # Update top bar and sidebar colors
        if hasattr(self, 'top_bar'):
            self.top_bar.configure(fg_color=self.bg_secondary)
        if hasattr(self, 'sidebar'):
            self.sidebar.configure(fg_color=self.bg_secondary)
        if hasattr(self, 'status_bar'):
            self.status_bar.configure(fg_color=self.bg_secondary)
        
        # Update theme button text
        theme_text = "☀️ Light" if new_mode == "Dark" else "🌙 Dark"
        if hasattr(self, 'theme_btn'):
            self.theme_btn.configure(text=theme_text)
        
        # Refresh current view to apply new colors
        self.show_view(self.current_view)

    def show_view(self, view):
        # Clear main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.current_view = view
        self.update_colors()
        
        # Update nav button states
        for key, btn in self.nav_buttons.items():
            if key == view:
                btn.configure(fg_color=self.accent_color, hover_color="#3a7a7a")
            else:
                btn.configure(fg_color="transparent", hover_color=self.bg_tertiary)

        if view == "organize":
            self.show_organize_view()
        elif view == "search":
            self.show_search_view()
        elif view == "stats":
            self.show_stats_view()
        elif view == "tools":
            self.show_tools_view()
        elif view == "settings":
            self.show_settings_view()

    def show_organize_view(self):
        # Page title
        title = ctk.CTkLabel(
            self.main_frame,
            text="Organize Files",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 8))
        
        subtitle = ctk.CTkLabel(
            self.main_frame,
            text="Select a folder to automatically organize files by type",
            font=ctk.CTkFont(size=13),
            text_color=self.text_secondary
        )
        subtitle.pack(anchor="w", pady=(0, 30))
        
        # Folder selection card
        folder_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
        folder_card.pack(fill="x", pady=(0, 20))
        
        card_content = ctk.CTkFrame(folder_card, fg_color="transparent")
        card_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        folder_label = ctk.CTkLabel(
            card_content,
            text="Target Folder",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        folder_label.pack(anchor="w", pady=(0, 12))
        
        path_row = ctk.CTkFrame(card_content, fg_color="transparent")
        path_row.pack(fill="x", pady=(0, 15))
        
        self.path_entry = ctk.CTkEntry(
            path_row,
            placeholder_text="No folder selected...",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        
        browse_btn = ctk.CTkButton(
            path_row,
            text="Browse",
            width=110,
            height=40,
            command=self.select_folder,
            fg_color=self.accent_color,
            hover_color="#3a7a7a"
        )
        browse_btn.pack(side="left", padx=(0, 8))
        
        if self.target_path:
            open_btn = ctk.CTkButton(
                path_row,
                text="📂 Open",
                width=90,
                height=40,
                command=self.open_folder,
                fg_color=self.bg_tertiary,
                hover_color=self.border_color
            )
            open_btn.pack(side="left")
        
        # Recent folders section
        if self.recent_folders:
            recent_label = ctk.CTkLabel(
                card_content,
                text="Recent Folders",
                font=ctk.CTkFont(size=12),
                text_color=self.text_secondary
            )
            recent_label.pack(anchor="w", pady=(0, 8))
            
            recent_grid = ctk.CTkFrame(card_content, fg_color="transparent")
            recent_grid.pack(fill="x")
            
            for folder in self.recent_folders[-3:]:
                folder_btn = ctk.CTkButton(
                    recent_grid,
                    text=f"📁 {os.path.basename(folder)}",
                    anchor="w",
                    height=36,
                    command=lambda f=folder: self.load_folder(f),
                    fg_color=self.bg_tertiary,
                    hover_color=self.border_color,
                    font=ctk.CTkFont(size=12)
                )
                folder_btn.pack(fill="x", pady=3)
        
        # Quick stats preview
        if self.target_path:
            try:
                files, size = get_folder_stats(self.target_path)
                quick_stats_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
                quick_stats_card.pack(fill="x", pady=(0, 20))
                
                quick_stats_content = ctk.CTkFrame(quick_stats_card, fg_color="transparent")
                quick_stats_content.pack(fill="both", expand=True, padx=25, pady=20)
                
                quick_stats_title = ctk.CTkLabel(
                    quick_stats_content,
                    text="Folder Overview",
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                quick_stats_title.pack(anchor="w", pady=(0, 12))
                
                quick_stats_row = ctk.CTkFrame(quick_stats_content, fg_color="transparent")
                quick_stats_row.pack(fill="x")
                
                files_quick = ctk.CTkFrame(quick_stats_row, fg_color=self.bg_tertiary, corner_radius=6)
                files_quick.pack(side="left", fill="both", expand=True, padx=(0, 8))
                
                files_quick_content = ctk.CTkFrame(files_quick, fg_color="transparent")
                files_quick_content.pack(fill="both", expand=True, padx=12, pady=10)
                
                files_quick_label = ctk.CTkLabel(
                    files_quick_content,
                    text=f"{files} files",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=self.accent_color
                )
                files_quick_label.pack()
                
                size_quick = ctk.CTkFrame(quick_stats_row, fg_color=self.bg_tertiary, corner_radius=6)
                size_quick.pack(side="left", fill="both", expand=True, padx=(8, 0))
                
                size_quick_content = ctk.CTkFrame(size_quick, fg_color="transparent")
                size_quick_content.pack(fill="both", expand=True, padx=12, pady=10)
                
                size_quick_label = ctk.CTkLabel(
                    size_quick_content,
                    text=format_file_size(size),
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=self.accent_color
                )
                size_quick_label.pack()
            except:
                pass
        
        # File breakdown preview
        if self.target_path:
            breakdown = get_file_breakdown(self.target_path)
            total_preview = sum(breakdown.values())
            
            if total_preview > 0:
                preview_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
                preview_card.pack(fill="x", pady=(0, 20))
                
                preview_content = ctk.CTkFrame(preview_card, fg_color="transparent")
                preview_content.pack(fill="both", expand=True, padx=25, pady=25)
                
                preview_title = ctk.CTkLabel(
                    preview_content,
                    text="Preview Organization",
                    font=ctk.CTkFont(size=14, weight="bold")
                )
                preview_title.pack(anchor="w", pady=(0, 15))
                
                preview_info = ctk.CTkLabel(
                    preview_content,
                    text=f"{total_preview} files will be organized into categories:",
                    font=ctk.CTkFont(size=12),
                    text_color=self.text_secondary
                )
                preview_info.pack(anchor="w", pady=(0, 12))
                
                # Category icons mapping
                category_icons = {
                    'Images': '🖼️',
                    'Documents': '📄',
                    'Videos': '🎬',
                    'Music': '🎵',
                    'Archives': '📦',
                    'Programs': '⚙️',
                    'Others': '📁'
                }
                
                self.breakdown_frame = ctk.CTkFrame(preview_content, fg_color="transparent")
                self.breakdown_frame.pack(fill="x")
                
                # Show categories with files
                categories_with_files = [(cat, count) for cat, count in breakdown.items() if count > 0]
                
                if categories_with_files:
                    for i, (category, count) in enumerate(categories_with_files):
                        if i % 2 == 0:
                            row = ctk.CTkFrame(self.breakdown_frame, fg_color="transparent")
                            row.pack(fill="x", pady=4)
                        
                        category_frame = ctk.CTkFrame(
                            row if i % 2 == 0 else self.breakdown_frame,
                            fg_color=self.bg_tertiary,
                            corner_radius=6
                        )
                        category_frame.pack(
                            side="left" if i % 2 == 0 else "right",
                            fill="x",
                            expand=True,
                            padx=(0 if i % 2 == 0 else 8, 8 if i % 2 == 0 else 0)
                        )
                        
                        cat_content = ctk.CTkFrame(category_frame, fg_color="transparent")
                        cat_content.pack(fill="both", expand=True, padx=12, pady=8)
                        
                        icon_label = ctk.CTkLabel(
                            cat_content,
                            text=category_icons.get(category, '📁'),
                            font=ctk.CTkFont(size=16)
                        )
                        icon_label.pack(side="left", padx=(0, 10))
                        
                        text_frame = ctk.CTkFrame(cat_content, fg_color="transparent")
                        text_frame.pack(side="left", fill="x", expand=True)
                        
                        cat_name = ctk.CTkLabel(
                            text_frame,
                            text=category,
                            font=ctk.CTkFont(size=12, weight="bold"),
                            anchor="w"
                        )
                        cat_name.pack(anchor="w")
                        
                        cat_count = ctk.CTkLabel(
                            text_frame,
                            text=f"{count} file{'s' if count != 1 else ''}",
                            font=ctk.CTkFont(size=11),
                            text_color=self.text_secondary,
                            anchor="w"
                        )
                        cat_count.pack(anchor="w")
        
        # Actions card
        actions_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
        actions_card.pack(fill="x", pady=(0, 20))
        
        actions_content = ctk.CTkFrame(actions_card, fg_color="transparent")
        actions_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        actions_label = ctk.CTkLabel(
            actions_content,
            text="Actions",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        actions_label.pack(anchor="w", pady=(0, 15))
        
        button_row = ctk.CTkFrame(actions_content, fg_color="transparent")
        button_row.pack(fill="x")
        
        organize_btn = ctk.CTkButton(
            button_row,
            text="Start Organizing",
            height=42,
            command=self.run_organizer,
            fg_color=self.accent_color,
            hover_color="#3a7a7a",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        organize_btn.pack(side="left", padx=(0, 10))
        
        undo_btn = ctk.CTkButton(
            button_row,
            text="Undo Last",
            height=42,
            command=self.undo_last_operation,
            fg_color=self.bg_tertiary,
            hover_color=self.border_color
        )
        undo_btn.pack(side="left", padx=(0, 10))
        
        clear_btn = ctk.CTkButton(
            button_row,
            text="Clear",
            height=42,
            command=self.clear_path,
            fg_color=self.bg_tertiary,
            hover_color=self.border_color
        )
        clear_btn.pack(side="left")
        
        # Progress section
        progress_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
        progress_card.pack(fill="x")
        
        progress_content = ctk.CTkFrame(progress_card, fg_color="transparent")
        progress_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        progress_label = ctk.CTkLabel(
            progress_content,
            text="Progress",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        progress_label.pack(anchor="w", pady=(0, 12))
        
        self.progress = ctk.CTkProgressBar(progress_content, height=8, corner_radius=4)
        self.progress.pack(fill="x")
        self.progress.set(0)

    def show_search_view(self):
        title = ctk.CTkLabel(
            self.main_frame,
            text="Search Files",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 8))
        
        subtitle = ctk.CTkLabel(
            self.main_frame,
            text="Find files by name in your selected folder",
            font=ctk.CTkFont(size=13),
            text_color=self.text_secondary
        )
        subtitle.pack(anchor="w", pady=(0, 30))
        
        # Search card
        search_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
        search_card.pack(fill="x", pady=(0, 20))
        
        search_content = ctk.CTkFrame(search_card, fg_color="transparent")
        search_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        search_label = ctk.CTkLabel(
            search_content,
            text="Search Query",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        search_label.pack(anchor="w", pady=(0, 12))
        
        search_row = ctk.CTkFrame(search_content, fg_color="transparent")
        search_row.pack(fill="x", pady=(0, 20))
        
        self.search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="Enter file name to search...",
            height=42,
            font=ctk.CTkFont(size=13)
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        
        search_btn = ctk.CTkButton(
            search_row,
            text="Search",
            width=110,
            height=42,
            command=self.perform_search,
            fg_color=self.accent_color,
            hover_color="#3a7a7a"
        )
        search_btn.pack(side="left")
        
        # Filter options
        filter_row = ctk.CTkFrame(search_content, fg_color="transparent")
        filter_row.pack(fill="x", pady=(0, 0))
        
        filter_label = ctk.CTkLabel(
            filter_row,
            text="Filter by type:",
            font=ctk.CTkFont(size=11),
            text_color=self.text_secondary
        )
        filter_label.pack(side="left", padx=(0, 10))
        
        self.search_filter = ctk.CTkOptionMenu(
            filter_row,
            values=["All Types", "Images", "Documents", "Videos", "Music", "Archives", "Programs"],
            width=150,
            height=32
        )
        self.search_filter.pack(side="left")
        self.search_filter.set("All Types")
        
        # Results card
        results_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
        results_card.pack(fill="both", expand=True)
        
        results_content = ctk.CTkFrame(results_card, fg_color="transparent")
        results_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        results_label = ctk.CTkLabel(
            results_content,
            text="Search Results",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        results_label.pack(anchor="w", pady=(0, 12))
        
        self.search_results = ctk.CTkTextbox(
            results_content,
            wrap="word",
            font=ctk.CTkFont(size=12),
            corner_radius=8
        )
        self.search_results.pack(fill="both", expand=True)

    def show_stats_view(self):
        title = ctk.CTkLabel(
            self.main_frame,
            text="Statistics",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 8))
        
        subtitle = ctk.CTkLabel(
            self.main_frame,
            text="View detailed statistics about your folder",
            font=ctk.CTkFont(size=13),
            text_color=self.text_secondary
        )
        subtitle.pack(anchor="w", pady=(0, 30))
        
        if self.target_path:
            files, size = get_folder_stats(self.target_path)
            
            # Stats cards in a grid
            stats_grid = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            stats_grid.pack(fill="x", pady=(0, 20))
            
            # Folder path card
            path_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
            path_card.pack(fill="x", pady=(0, 15))
            
            path_content = ctk.CTkFrame(path_card, fg_color="transparent")
            path_content.pack(fill="both", expand=True, padx=25, pady=20)
            
            path_label = ctk.CTkLabel(
                path_content,
                text="Current Folder",
                font=ctk.CTkFont(size=12),
                text_color=self.text_secondary
            )
            path_label.pack(anchor="w", pady=(0, 5))
            
            path_text = ctk.CTkLabel(
                path_content,
                text=self.target_path,
                font=ctk.CTkFont(size=13),
                anchor="w",
                justify="left"
            )
            path_text.pack(anchor="w", fill="x")
            
            # Stats cards row
            stats_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            stats_row.pack(fill="x", pady=(0, 20))
            
            # Files count card
            files_card = ctk.CTkFrame(stats_row, corner_radius=12, fg_color=self.bg_secondary)
            files_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
            
            files_content = ctk.CTkFrame(files_card, fg_color="transparent")
            files_content.pack(fill="both", expand=True, padx=25, pady=25)
            
            files_value = ctk.CTkLabel(
                files_content,
                text=str(files),
                font=ctk.CTkFont(size=36, weight="bold"),
                text_color=self.accent_color
            )
            files_value.pack(anchor="w", pady=(0, 5))
            
            files_label = ctk.CTkLabel(
                files_content,
                text="Total Files",
                font=ctk.CTkFont(size=13),
                text_color=self.text_secondary
            )
            files_label.pack(anchor="w")
            
            # Size card
            size_card = ctk.CTkFrame(stats_row, corner_radius=12, fg_color=self.bg_secondary)
            size_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
            
            size_content = ctk.CTkFrame(size_card, fg_color="transparent")
            size_content.pack(fill="both", expand=True, padx=25, pady=25)
            
            size_value = ctk.CTkLabel(
                size_content,
                text=format_file_size(size),
                font=ctk.CTkFont(size=36, weight="bold"),
                text_color=self.accent_color
            )
            size_value.pack(anchor="w", pady=(0, 5))
            
            size_label = ctk.CTkLabel(
                size_content,
                text="Total Size",
                font=ctk.CTkFont(size=13),
                text_color=self.text_secondary
            )
            size_label.pack(anchor="w")
            
            # Chart button
            chart_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
            chart_card.pack(fill="x")
            
            chart_content = ctk.CTkFrame(chart_card, fg_color="transparent")
            chart_content.pack(fill="both", expand=True, padx=25, pady=25)
            
            chart_btn = ctk.CTkButton(
                chart_content,
                text="Show File Type Chart",
                height=42,
                command=self.show_chart,
                fg_color=self.accent_color,
                hover_color="#3a7a7a"
            )
            chart_btn.pack()
        else:
            empty_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
            empty_card.pack(fill="x")
            
            empty_content = ctk.CTkFrame(empty_card, fg_color="transparent")
            empty_content.pack(fill="both", expand=True, padx=25, pady=40)
            
            empty_label = ctk.CTkLabel(
                empty_content,
                text="Select a folder first to view statistics",
                font=ctk.CTkFont(size=14),
                text_color=self.text_secondary
            )
            empty_label.pack()

    def show_tools_view(self):
        title = ctk.CTkLabel(
            self.main_frame,
            text="Tools",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 8))
        
        subtitle = ctk.CTkLabel(
            self.main_frame,
            text="Additional utilities for managing your files",
            font=ctk.CTkFont(size=13),
            text_color=self.text_secondary
        )
        subtitle.pack(anchor="w", pady=(0, 30))
        
        # Batch rename card
        rename_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
        rename_card.pack(fill="x", pady=(0, 15))
        
        rename_content = ctk.CTkFrame(rename_card, fg_color="transparent")
        rename_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        rename_title = ctk.CTkLabel(
            rename_content,
            text="Batch Rename Files",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        rename_title.pack(anchor="w", pady=(0, 8))
        
        rename_desc = ctk.CTkLabel(
            rename_content,
            text="Rename multiple files using a pattern (use # for numbers)",
            font=ctk.CTkFont(size=12),
            text_color=self.text_secondary
        )
        rename_desc.pack(anchor="w", pady=(0, 15))
        
        self.rename_pattern = ctk.CTkEntry(
            rename_content,
            placeholder_text="Pattern: file_### (becomes file_001, file_002, ...)",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.rename_pattern.pack(fill="x", pady=(0, 12))
        
        rename_btn = ctk.CTkButton(
            rename_content,
            text="Rename Files",
            height=40,
            command=self.batch_rename,
            fg_color=self.accent_color,
            hover_color="#3a7a7a"
        )
        rename_btn.pack(anchor="w")
        
        # Duplicates card
        dup_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
        dup_card.pack(fill="x", pady=(0, 15))
        
        dup_content = ctk.CTkFrame(dup_card, fg_color="transparent")
        dup_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        dup_title = ctk.CTkLabel(
            dup_content,
            text="Find Duplicate Files",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        dup_title.pack(anchor="w", pady=(0, 8))
        
        dup_desc = ctk.CTkLabel(
            dup_content,
            text="Scan for and remove duplicate files based on content",
            font=ctk.CTkFont(size=12),
            text_color=self.text_secondary
        )
        dup_desc.pack(anchor="w", pady=(0, 15))
        
        dup_btn = ctk.CTkButton(
            dup_content,
            text="Find & Delete Duplicates",
            height=40,
            command=self.delete_duplicates,
            fg_color=self.accent_color,
            hover_color="#3a7a7a"
        )
        dup_btn.pack(anchor="w")
        
        # Large files card
        size_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
        size_card.pack(fill="x")
        
        size_content = ctk.CTkFrame(size_card, fg_color="transparent")
        size_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        size_title = ctk.CTkLabel(
            size_content,
            text="Find Large Files",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        size_title.pack(anchor="w", pady=(0, 8))
        
        size_desc = ctk.CTkLabel(
            size_content,
            text="Identify files larger than a specified size",
            font=ctk.CTkFont(size=12),
            text_color=self.text_secondary
        )
        size_desc.pack(anchor="w", pady=(0, 15))
        
        self.size_threshold = ctk.CTkEntry(
            size_content,
            placeholder_text="Minimum size in MB (e.g., 100)",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.size_threshold.pack(fill="x", pady=(0, 12))
        
        size_btn = ctk.CTkButton(
            size_content,
            text="Find Large Files",
            height=40,
            command=self.find_large_files,
            fg_color=self.accent_color,
            hover_color="#3a7a7a"
        )
        size_btn.pack(anchor="w")
        
        # Empty folders cleaner
        empty_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
        empty_card.pack(fill="x", pady=(15, 0))
        
        empty_content = ctk.CTkFrame(empty_card, fg_color="transparent")
        empty_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        empty_title = ctk.CTkLabel(
            empty_content,
            text="Clean Empty Folders",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        empty_title.pack(anchor="w", pady=(0, 8))
        
        empty_desc = ctk.CTkLabel(
            empty_content,
            text="Remove all empty folders from the selected directory",
            font=ctk.CTkFont(size=12),
            text_color=self.text_secondary
        )
        empty_desc.pack(anchor="w", pady=(0, 15))
        
        empty_btn = ctk.CTkButton(
            empty_content,
            text="Find & Remove Empty Folders",
            height=40,
            command=self.clean_empty_folders,
            fg_color=self.accent_color,
            hover_color="#3a7a7a"
        )
        empty_btn.pack(anchor="w")

    def show_settings_view(self):
        title = ctk.CTkLabel(
            self.main_frame,
            text="Settings",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 8))
        
        subtitle = ctk.CTkLabel(
            self.main_frame,
            text="Configure application preferences",
            font=ctk.CTkFont(size=13),
            text_color=self.text_secondary
        )
        subtitle.pack(anchor="w", pady=(0, 30))
        
        # Appearance card
        appearance_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
        appearance_card.pack(fill="x", pady=(0, 15))
        
        appearance_content = ctk.CTkFrame(appearance_card, fg_color="transparent")
        appearance_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        appearance_title = ctk.CTkLabel(
            appearance_content,
            text="Appearance",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        appearance_title.pack(anchor="w", pady=(0, 15))
        
        theme_info = ctk.CTkLabel(
            appearance_content,
            text="Theme mode can be changed using the toggle in the top bar",
            font=ctk.CTkFont(size=12),
            text_color=self.text_secondary
        )
        theme_info.pack(anchor="w", pady=(0, 20))
        
        current_mode = ctk.get_appearance_mode()
        mode_display = ctk.CTkLabel(
            appearance_content,
            text=f"Current mode: {current_mode}",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        mode_display.pack(anchor="w")
        
        # Other settings card
        other_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
        other_card.pack(fill="x", pady=(0, 15))
        
        other_content = ctk.CTkFrame(other_card, fg_color="transparent")
        other_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        other_title = ctk.CTkLabel(
            other_content,
            text="Other",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        other_title.pack(anchor="w", pady=(0, 15))
        
        log_btn = ctk.CTkButton(
            other_content,
            text="View Application Logs",
            height=40,
            command=self.view_logs,
            fg_color=self.accent_color,
            hover_color="#3a7a7a"
        )
        log_btn.pack(anchor="w", pady=(0, 10))
        
        clear_history_btn = ctk.CTkButton(
            other_content,
            text="Clear Activity History",
            height=40,
            command=self.clear_activity_history,
            fg_color=self.bg_tertiary,
            hover_color=self.border_color
        )
        clear_history_btn.pack(anchor="w", pady=(0, 15))
        
        about_text = ctk.CTkLabel(
            other_content,
            text="File Organizer v1.0\nA simple tool for organizing files by type",
            font=ctk.CTkFont(size=12),
            text_color=self.text_secondary,
            justify="left"
        )
        about_text.pack(anchor="w")
        
        # Export/Import rules card
        rules_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
        rules_card.pack(fill="x", pady=(0, 15))
        
        rules_content = ctk.CTkFrame(rules_card, fg_color="transparent")
        rules_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        rules_title = ctk.CTkLabel(
            rules_content,
            text="Organization Rules",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        rules_title.pack(anchor="w", pady=(0, 8))
        
        rules_desc = ctk.CTkLabel(
            rules_content,
            text="Export or import custom file organization rules",
            font=ctk.CTkFont(size=12),
            text_color=self.text_secondary
        )
        rules_desc.pack(anchor="w", pady=(0, 15))
        
        rules_buttons = ctk.CTkFrame(rules_content, fg_color="transparent")
        rules_buttons.pack(fill="x")
        
        export_btn = ctk.CTkButton(
            rules_buttons,
            text="Export Rules",
            height=40,
            command=self.export_rules,
            fg_color=self.accent_color,
            hover_color="#3a7a7a"
        )
        export_btn.pack(side="left", padx=(0, 10))
        
        import_btn = ctk.CTkButton(
            rules_buttons,
            text="Import Rules",
            height=40,
            command=self.import_rules,
            fg_color=self.bg_tertiary,
            hover_color=self.border_color
        )
        import_btn.pack(side="left")
        
        # Quick stats card
        stats_card = ctk.CTkFrame(self.main_frame, corner_radius=12, fg_color=self.bg_secondary)
        stats_card.pack(fill="x")
        
        stats_content = ctk.CTkFrame(stats_card, fg_color="transparent")
        stats_content.pack(fill="both", expand=True, padx=25, pady=25)
        
        stats_title = ctk.CTkLabel(
            stats_content,
            text="Quick Stats",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        stats_title.pack(anchor="w", pady=(0, 15))
        
        total_organized = sum(act.get('files_moved', 0) for act in self.activity_history if act.get('type') == 'organize')
        total_operations = len([act for act in self.activity_history if act.get('type') == 'organize'])
        
        stats_row = ctk.CTkFrame(stats_content, fg_color="transparent")
        stats_row.pack(fill="x")
        
        files_stat = ctk.CTkFrame(stats_row, fg_color=self.bg_tertiary, corner_radius=6)
        files_stat.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        files_stat_content = ctk.CTkFrame(files_stat, fg_color="transparent")
        files_stat_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        files_value = ctk.CTkLabel(
            files_stat_content,
            text=str(total_organized),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.accent_color
        )
        files_value.pack(anchor="w", pady=(0, 5))
        
        files_label = ctk.CTkLabel(
            files_stat_content,
            text="Total Files Organized",
            font=ctk.CTkFont(size=11),
            text_color=self.text_secondary
        )
        files_label.pack(anchor="w")
        
        ops_stat = ctk.CTkFrame(stats_row, fg_color=self.bg_tertiary, corner_radius=6)
        ops_stat.pack(side="left", fill="both", expand=True, padx=(8, 0))
        
        ops_stat_content = ctk.CTkFrame(ops_stat, fg_color="transparent")
        ops_stat_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        ops_value = ctk.CTkLabel(
            ops_stat_content,
            text=str(total_operations),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.accent_color
        )
        ops_value.pack(anchor="w", pady=(0, 5))
        
        ops_label = ctk.CTkLabel(
            ops_stat_content,
            text="Total Operations",
            font=ctk.CTkFont(size=11),
            text_color=self.text_secondary
        )
        ops_label.pack(anchor="w")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            if self.path_entry:
                self.path_entry.delete(0, tk.END)
                self.path_entry.insert(0, folder)
            self.target_path = folder
            if folder not in self.recent_folders:
                self.recent_folders.append(folder)
                if len(self.recent_folders) > 5:
                    self.recent_folders.pop(0)
            config['recent_folders'] = self.recent_folders
            save_config(config)
            self.update_status()

    def load_folder(self, folder):
        self.target_path = folder
        if self.path_entry:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)
        self.update_status()
        # Refresh view to show breakdown
        if self.current_view == "organize":
            self.show_view("organize")
    
    def open_folder(self):
        """Open the selected folder in file explorer"""
        if not self.target_path:
            messagebox.showwarning("Warning", "No folder selected!")
            return
        try:
            os.startfile(self.target_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {e}")

    def run_organizer(self):
        if not self.target_path:
            messagebox.showwarning("Warning", "Please select a folder first!")
            return
        moved, moved_files = organize_files(self.target_path, self.update_progress)
        if moved > 0:
            self.undo_stack.append(("organize", moved_files))
        messagebox.showinfo("Success", f"Organized {moved} files.")
        self.update_status()

    def clear_path(self):
        if self.path_entry:
            self.path_entry.delete(0, tk.END)
        self.target_path = None
        self.update_status()

    def perform_search(self):
        query = self.search_entry.get() if self.search_entry else ""
        if not query or not self.target_path:
            messagebox.showwarning("Warning", "Enter a query and select a folder first!")
            return
        
        filter_type = self.search_filter.get() if hasattr(self, 'search_filter') else "All Types"
        results = search_files(self.target_path, query)
        
        # Apply filter if not "All Types"
        if filter_type != "All Types" and filter_type in extensions_map:
            filtered_results = []
            allowed_exts = extensions_map[filter_type]
            for result in results:
                _, ext = os.path.splitext(result)
                if ext.lower() in allowed_exts:
                    filtered_results.append(result)
            results = filtered_results
        
        if self.search_results:
            self.search_results.delete("0.0", "end")
            if not results:
                self.search_results.insert("0.0", f"No files found matching '{query}'" + 
                                         (f" in {filter_type}" if filter_type != "All Types" else ""))
            else:
                header = f"Found {len(results)} file{'s' if len(results) != 1 else ''} matching '{query}'"
                if filter_type != "All Types":
                    header += f" (filtered: {filter_type})"
                header += "\n\n"
                
                result_text = header
                for i, result in enumerate(results, 1):
                    size, modified = get_file_info(result)
                    filename = os.path.basename(result)
                    rel_path = os.path.relpath(result, self.target_path)
                    result_text += f"{i}. {filename}\n"
                    result_text += f"   📁 {rel_path}\n"
                    result_text += f"   📊 {format_file_size(size)}  •  🕒 {modified}\n\n"
                
                self.search_results.insert("0.0", result_text)

    def show_chart(self):
        if not self.target_path:
            messagebox.showwarning("Warning", "Select a folder first!")
            return
        
        try:
            import matplotlib.pyplot as plt
            from collections import Counter
            
            file_types = []
            for root, dirs, files in os.walk(self.target_path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext:
                        file_types.append(ext)
            
            if not file_types:
                messagebox.showinfo("No Files", "No files found in the selected folder.")
                return
            
            type_counts = Counter(file_types)
            labels = list(type_counts.keys())
            sizes = list(type_counts.values())
            
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            ax.set_title('File Type Distribution')
            
            plt.show()
            
        except ImportError:
            messagebox.showerror("Error", "Matplotlib not installed. Install with: pip install matplotlib")

    def save_settings(self):
        # Settings are saved automatically when theme is toggled
        pass

    def view_logs(self):
        log_file = "file_organizer.log"
        if not os.path.exists(log_file):
            messagebox.showinfo("Logs", "No log file found.")
            return
        
        try:
            with open(log_file, 'r') as f:
                log_content = f.read()
            
            log_window = ctk.CTkToplevel(self)
            log_window.title("Application Logs")
            log_window.geometry("800x600")
            
            text_box = ctk.CTkTextbox(log_window, wrap="word")
            text_box.pack(fill="both", expand=True, padx=10, pady=10)
            text_box.insert("0.0", log_content)
            text_box.configure(state="disabled")
            
            clear_btn = ctk.CTkButton(log_window, text="Clear Logs", command=lambda: self.clear_logs(log_window, text_box))
            clear_btn.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read logs: {str(e)}")

    def clear_logs(self, window, text_box):
        confirm = messagebox.askyesno("Confirm", "Clear all logs?")
        if confirm:
            try:
                with open("file_organizer.log", 'w') as f:
                    f.write("")
                text_box.delete("0.0", "end")
                messagebox.showinfo("Logs", "Logs cleared.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear logs: {str(e)}")

    def undo_last_operation(self):
        if not self.undo_stack:
            messagebox.showinfo("Undo", "No operations to undo.")
            return
        
        operation, data = self.undo_stack.pop()
        if operation == "organize":
            undone = 0
            for old_path, new_path in reversed(data):
                try:
                    if os.path.exists(new_path):
                        shutil.move(new_path, old_path)
                        undone += 1
                        logging.info(f"Undid move: {new_path} -> {old_path}")
                except Exception as e:
                    logging.error(f"Error undoing move: {e}")
                    messagebox.showerror("Error", f"Failed to undo some moves: {e}")
            
            messagebox.showinfo("Undo", f"Undid {undone} file moves.")
            self.update_status()
        else:
            messagebox.showinfo("Undo", f"Undo for {operation} not implemented.")

    def batch_rename(self):
        if not self.target_path:
            messagebox.showwarning("Warning", "Select a folder first!")
            return
        
        pattern = self.rename_pattern.get().strip()
        if not pattern:
            messagebox.showwarning("Warning", "Enter a rename pattern!")
            return
        
        try:
            import re
            files = [f for f in os.listdir(self.target_path) if os.path.isfile(os.path.join(self.target_path, f))]
            renamed = 0
            
            for i, file in enumerate(files):
                name, ext = os.path.splitext(file)
                new_name = pattern.replace("###", f"{i+1:03d}").replace("##", f"{i+1:02d}").replace("#", str(i+1))
                new_path = os.path.join(self.target_path, new_name + ext)
                
                if not os.path.exists(new_path):
                    os.rename(os.path.join(self.target_path, file), new_path)
                    renamed += 1
            
            messagebox.showinfo("Success", f"Renamed {renamed} files.")
            self.update_status()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename files: {str(e)}")

    def delete_duplicates(self):
        if not self.target_path:
            messagebox.showwarning("Warning", "Select a folder first!")
            return
        
        try:
            import hashlib
            file_hashes = {}
            duplicates = []
            
            for root, dirs, files in os.walk(self.target_path):
                for file in files:
                    path = os.path.join(root, file)
                    with open(path, 'rb') as f:
                        hash_val = hashlib.md5(f.read()).hexdigest()
                    
                    if hash_val in file_hashes:
                        duplicates.append(path)
                    else:
                        file_hashes[hash_val] = path
            
            if not duplicates:
                messagebox.showinfo("No Duplicates", "No duplicate files found.")
                return
            
            confirm = messagebox.askyesno("Confirm", f"Found {len(duplicates)} duplicate files. Delete them?")
            if confirm:
                for dup in duplicates:
                    os.remove(dup)
                messagebox.showinfo("Success", f"Deleted {len(duplicates)} duplicate files.")
                self.update_status()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete duplicates: {str(e)}")

    def find_large_files(self):
        if not self.target_path:
            messagebox.showwarning("Warning", "Select a folder first!")
            return
        
        try:
            threshold_mb = float(self.size_threshold.get().strip())
            threshold_bytes = threshold_mb * 1024 * 1024
        except ValueError:
            messagebox.showwarning("Warning", "Enter a valid number for size threshold!")
            return
        
        large_files = []
        for root, dirs, files in os.walk(self.target_path):
            for file in files:
                path = os.path.join(root, file)
                size = os.path.getsize(path)
                if size > threshold_bytes:
                    large_files.append((path, size))
        
        if not large_files:
            messagebox.showinfo("No Large Files", f"No files larger than {threshold_mb} MB found.")
            return
        
        result = f"Files larger than {threshold_mb} MB:\n\n"
        for path, size in sorted(large_files, key=lambda x: x[1], reverse=True):
            result += f"{os.path.basename(path)}: {size / (1024*1024):.2f} MB\n"
        
        # Show in a scrollable text box
        result_window = ctk.CTkToplevel(self)
        result_window.title("Large Files")
        result_window.geometry("600x400")
        
        text_box = ctk.CTkTextbox(result_window, wrap="word")
        text_box.pack(fill="both", expand=True, padx=10, pady=10)
        text_box.insert("0.0", result)
        text_box.configure(state="disabled")
    
    def clean_empty_folders(self):
        """Find and remove empty folders"""
        if not self.target_path:
            messagebox.showwarning("Warning", "Select a folder first!")
            return
        
        try:
            empty_folders = []
            for root, dirs, files in os.walk(self.target_path, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if not os.listdir(dir_path):  # Empty folder
                            empty_folders.append(dir_path)
                    except:
                        pass
            
            if not empty_folders:
                messagebox.showinfo("No Empty Folders", "No empty folders found.")
                return
            
            confirm = messagebox.askyesno(
                "Confirm", 
                f"Found {len(empty_folders)} empty folder{'s' if len(empty_folders) != 1 else ''}. Delete them?"
            )
            if confirm:
                deleted = 0
                for folder in empty_folders:
                    try:
                        os.rmdir(folder)
                        deleted += 1
                        logging.info(f"Deleted empty folder: {folder}")
                    except Exception as e:
                        logging.error(f"Error deleting folder {folder}: {e}")
                
                messagebox.showinfo("Success", f"Deleted {deleted} empty folder{'s' if deleted != 1 else ''}.")
                self.update_status()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clean empty folders: {str(e)}")
    
    def export_rules(self):
        """Export organization rules to a JSON file"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Organization Rules"
            )
            if file_path:
                rules_data = {
                    'extensions_map': extensions_map,
                    'exported_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'version': '1.0'
                }
                with open(file_path, 'w') as f:
                    json.dump(rules_data, f, indent=2)
                messagebox.showinfo("Success", f"Rules exported to {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export rules: {str(e)}")
    
    def import_rules(self):
        """Import organization rules from a JSON file"""
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Import Organization Rules"
            )
            if file_path:
                with open(file_path, 'r') as f:
                    rules_data = json.load(f)
                
                if 'extensions_map' in rules_data:
                    global extensions_map
                    extensions_map = rules_data['extensions_map']
                    messagebox.showinfo("Success", "Rules imported successfully. Restart the app to apply changes.")
                    logging.info(f"Imported rules from {file_path}")
                else:
                    messagebox.showerror("Error", "Invalid rules file format.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import rules: {str(e)}")

    def update_progress(self, value):
        if self.progress:
            self.progress.set(value / 100)

    def update_status(self):
        if self.target_path:
            files, size = get_folder_stats(self.target_path)
            folder_name = os.path.basename(self.target_path) or self.target_path
            self.status_label.configure(text=f"Current folder: {folder_name}")
            self.file_count_label.configure(text=f"Files: {files}")
        else:
            self.status_label.configure(text="No folder selected")
            self.file_count_label.configure(text="Files: 0")

    def clear_activity_history(self):
        """Clear the activity history"""
        confirm = messagebox.askyesno("Confirm", "Clear all activity history?")
        if confirm:
            self.activity_history = []
            config['activity_history'] = []
            save_config(config)
            messagebox.showinfo("Success", "Activity history cleared.")
            if self.current_view == "settings":
                self.show_view("settings")
    
    def show_help(self):
        help_text = """File Organizer Help

Organize: Select a folder and click "Start Organizing" to automatically sort files into category folders (Images, Documents, Videos, etc.)

Search: Enter a file name to search (press Enter or click Search). Use the filter dropdown to search by file type.

Statistics: View file count, total size, generate charts, and see recent activity history

Tools: 
  • Batch Rename: Rename files with patterns (e.g., file_###)
  • Find Duplicates: Remove duplicate files based on content
  • Find Large Files: Locate files above a size threshold
  • Clean Empty Folders: Remove all empty directories

Settings: 
  • Change between light and dark mode using the theme toggle
  • Export/Import organization rules for customization
  • View application logs and clear activity history

Keyboard Shortcuts:
  • Enter: Execute search (when in search view)
  • Click "Open" button to open selected folder in file explorer

Tips: 
  • Your recently used folders appear for quick access
  • The preview shows how files will be organized before running
  • All operations can be undone using the "Undo Last" button
        """
        messagebox.showinfo("Help", help_text)

# ==========================================
# MAIN EXECUTION 
# ==========================================

if __name__ == "__main__":
    app = FileOrganizerApp()
    app.mainloop()