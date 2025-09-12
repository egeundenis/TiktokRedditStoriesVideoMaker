"""
Modern dark theme configuration for TikTok Video Maker
"""

import tkinter as tk
from tkinter import ttk

class ModernTheme:
    """Modern dark theme with professional styling"""
    
    # Color palette
    COLORS = {
        'bg_primary': '#1e1e1e',      # Main background
        'bg_secondary': '#2d2d2d',    # Card backgrounds
        'bg_tertiary': '#3d3d3d',     # Input backgrounds
        'accent_primary': '#007acc',   # Primary accent (blue)
        'accent_hover': '#005a9e',     # Hover state
        'success': '#4caf50',          # Success green
        'warning': '#ff9800',          # Warning orange
        'error': '#f44336',            # Error red
        'text_primary': '#ffffff',     # Primary text
        'text_secondary': '#b0b0b0',   # Secondary text
        'border': '#404040',           # Borders
        'shadow': '#000000'            # Shadows
    }
    
    # Typography
    FONTS = {
        'title': ('Segoe UI', 24, 'bold'),
        'subtitle': ('Segoe UI', 16, 'bold'),
        'heading': ('Segoe UI', 12, 'bold'),
        'body': ('Segoe UI', 10),
        'small': ('Segoe UI', 9),
        'mono': ('Consolas', 9)
    }
    
    # Spacing
    SPACING = {
        'xs': 5,
        'sm': 10,
        'md': 15,
        'lg': 20,
        'xl': 30
    }

def apply_modern_theme(root):
    """Apply modern theme to the application"""
    style = ttk.Style()
    
    # Use clam theme as base
    style.theme_use('clam')
    
    # Configure root window
    root.configure(bg=ModernTheme.COLORS['bg_primary'])
    
    # Configure notebook styles
    style.configure("Modern.TNotebook",
                   background=ModernTheme.COLORS['bg_primary'],
                   borderwidth=0,
                   tabmargins=[2, 5, 2, 0])
    
    style.configure("Modern.TNotebook.Tab",
                   background=ModernTheme.COLORS['bg_secondary'],
                   foreground=ModernTheme.COLORS['text_secondary'],
                   padding=[ModernTheme.SPACING['lg'], ModernTheme.SPACING['sm']],
                   borderwidth=0,
                   focuscolor='none')
    
    style.map("Modern.TNotebook.Tab",
             background=[('selected', ModernTheme.COLORS['accent_primary']),
                        ('active', ModernTheme.COLORS['bg_tertiary'])],
             foreground=[('selected', ModernTheme.COLORS['text_primary']),
                        ('active', ModernTheme.COLORS['text_primary'])])
    
    # Configure frame styles
    style.configure("Modern.TFrame", 
                   background=ModernTheme.COLORS['bg_primary'])
    
    style.configure("Card.TFrame",
                   background=ModernTheme.COLORS['bg_secondary'],
                   relief="flat",
                   borderwidth=1)
    
    # Configure label styles
    style.configure("Modern.TLabel",
                   background=ModernTheme.COLORS['bg_primary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   font=ModernTheme.FONTS['body'])
    
    style.configure("Header.TLabel",
                   background=ModernTheme.COLORS['bg_primary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   font=ModernTheme.FONTS['subtitle'])
    
    style.configure("Subheader.TLabel",
                   background=ModernTheme.COLORS['bg_secondary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   font=ModernTheme.FONTS['heading'])
    
    # Configure button styles
    style.configure("Modern.TButton",
                   background=ModernTheme.COLORS['accent_primary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   borderwidth=0,
                   focuscolor='none',
                   padding=[ModernTheme.SPACING['lg'], ModernTheme.SPACING['sm']],
                   font=ModernTheme.FONTS['heading'])
    
    style.map("Modern.TButton",
             background=[('active', ModernTheme.COLORS['accent_hover']),
                        ('pressed', ModernTheme.COLORS['accent_hover'])])
    
    # Configure entry styles
    style.configure("Modern.TEntry",
                   fieldbackground=ModernTheme.COLORS['bg_tertiary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   borderwidth=1,
                   insertcolor=ModernTheme.COLORS['text_primary'])
    
    # Configure labelframe styles
    style.configure("Modern.TLabelframe",
                   background=ModernTheme.COLORS['bg_secondary'],
                   foreground=ModernTheme.COLORS['text_primary'],
                   borderwidth=1,
                   relief="flat")
    
    style.configure("Modern.TLabelframe.Label",
                   background=ModernTheme.COLORS['bg_secondary'],
                   foreground=ModernTheme.COLORS['accent_primary'],
                   font=ModernTheme.FONTS['heading'])
    
    # Configure progressbar
    style.configure("Modern.Horizontal.TProgressbar",
                   background=ModernTheme.COLORS['accent_primary'],
                   troughcolor=ModernTheme.COLORS['bg_tertiary'],
                   borderwidth=0,
                   lightcolor=ModernTheme.COLORS['accent_primary'],
                   darkcolor=ModernTheme.COLORS['accent_primary'])

def create_gradient_frame(parent, color1, color2, height=100):
    """Create a gradient background frame (simplified version)"""
    frame = tk.Frame(parent, bg=color1, height=height)
    return frame

def add_hover_effect(widget, hover_color, normal_color):
    """Add hover effect to a widget"""
    def on_enter(event):
        widget.configure(bg=hover_color)
    
    def on_leave(event):
        widget.configure(bg=normal_color)
    
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

def create_modern_button(parent, text, command, style="primary"):
    """Create a modern styled button"""
    colors = ModernTheme.COLORS
    
    if style == "primary":
        bg_color = colors['accent_primary']
        hover_color = colors['accent_hover']
    elif style == "success":
        bg_color = colors['success']
        hover_color = colors['success']
    elif style == "warning":
        bg_color = colors['warning']
        hover_color = colors['warning']
    else:
        bg_color = colors['bg_tertiary']
        hover_color = colors['border']
    
    button = tk.Button(parent, text=text, command=command,
                      bg=bg_color, fg=colors['text_primary'],
                      font=ModernTheme.FONTS['heading'],
                      relief="flat", bd=0,
                      padx=ModernTheme.SPACING['lg'],
                      pady=ModernTheme.SPACING['sm'])
    
    add_hover_effect(button, hover_color, bg_color)
    return button

def create_modern_text_widget(parent, **kwargs):
    """Create a modern styled text widget"""
    colors = ModernTheme.COLORS
    
    default_config = {
        'bg': colors['bg_tertiary'],
        'fg': colors['text_primary'],
        'font': ModernTheme.FONTS['mono'],
        'relief': 'flat',
        'bd': 0,
        'wrap': 'word',
        'insertbackground': colors['text_primary']
    }
    
    # Update with user provided kwargs
    default_config.update(kwargs)
    
    text_widget = tk.Text(parent, **default_config)
    
    # Configure tags for colored output
    text_widget.tag_configure("success", foreground=colors['success'])
    text_widget.tag_configure("warning", foreground=colors['warning'])
    text_widget.tag_configure("error", foreground=colors['error'])
    text_widget.tag_configure("info", foreground=colors['accent_primary'])
    
    return text_widget