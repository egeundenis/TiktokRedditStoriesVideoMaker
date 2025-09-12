import tkinter as tk
from tkinter import ttk, messagebox, font
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
from utils import text_to_speech, speed_up_audio
from video_processor import prepare_video, transcribe_and_chunk, burn_subtitles
from theme import ModernTheme, apply_modern_theme, create_modern_text_widget
import random
import glob

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎬 TikTok Video Maker")
        self.geometry("900x800")
        self.minsize(800, 700)
        
        # Apply modern theme
        apply_modern_theme(self)

        # Create main container with padding
        main_container = tk.Frame(self, bg=ModernTheme.COLORS['bg_primary'])
        main_container.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Create header
        self.create_header(main_container)
        
        # Create modern notebook
        self.notebook = ttk.Notebook(main_container, style="Modern.TNotebook")
        self.notebook.pack(expand=True, fill="both", pady=(20, 0))

        # ---------------- Simple Mode ----------------
        self.simple_frame = ttk.Frame(self.notebook, style="Modern.TFrame")
        self.notebook.add(self.simple_frame, text="  🚀 Simple Mode  ")
        self.build_simple_ui()

        # ---------------- Advanced Mode ----------------
        self.advanced_frame = ttk.Frame(self.notebook, style="Modern.TFrame")
        self.notebook.add(self.advanced_frame, text="  ⚙️ Advanced Mode  ")
        self.build_advanced_ui()

        # ---------------- Bulk Production Mode ----------------
        self.bulk_frame = ttk.Frame(self.notebook, style="Modern.TFrame")
        self.notebook.add(self.bulk_frame, text="  📦 Bulk Production  ")
        self.build_bulk_ui()
    

    
    def create_header(self, parent):
        """Create modern header with app title and description"""
        header_frame = tk.Frame(parent, bg=ModernTheme.COLORS['bg_primary'])
        header_frame.pack(fill="x", pady=(0, 10))
        
        # App title
        title_label = tk.Label(header_frame, 
                              text="🎬 TikTok Video Maker",
                              font=ModernTheme.FONTS['title'],
                              fg=ModernTheme.COLORS['text_primary'],
                              bg=ModernTheme.COLORS['bg_primary'])
        title_label.pack(anchor="w")
        
        # Subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Create engaging TikTok videos with AI-powered speech synthesis and automated editing",
                                 font=ModernTheme.FONTS['body'],
                                 fg=ModernTheme.COLORS['text_secondary'],
                                 bg=ModernTheme.COLORS['bg_primary'])
        subtitle_label.pack(anchor="w", pady=(5, 0))

    # ---------------- Simple Mode UI ----------------
    def build_simple_ui(self):
        self.text_file = None
        self.video_file = None
        self.bg_music_file = None
        self.youtube_mode = tk.BooleanVar(value=False)

        # Create scrollable container
        canvas = tk.Canvas(self.simple_frame, bg=ModernTheme.COLORS['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.simple_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernTheme.COLORS['bg_primary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=20)
        scrollbar.pack(side="right", fill="y", pady=20)

        # File input section
        file_section = ttk.LabelFrame(scrollable_frame, text="📁 File Inputs", style="Modern.TLabelframe")
        file_section.pack(fill="x", pady=(0, 20), padx=20)
        
        # Text file input
        self.create_file_input(file_section, "📄 Text File (.txt)", "text_file", self.set_text, 0)
        
        # Video file input  
        self.create_file_input(file_section, "🎬 Background Video", "video_file", self.set_video, 1)
        
        # Music file input
        self.create_file_input(file_section, "🎼 Background Music (optional)", "bg_music_file", self.set_music, 2)

        # Format options section
        format_section = ttk.LabelFrame(scrollable_frame, text="📺 Output Format", style="Modern.TLabelframe")
        format_section.pack(fill="x", pady=(0, 20), padx=20)
        
        youtube_checkbox = ttk.Checkbutton(format_section, text="📺 YouTube Mode (preserves original format for videos >3min)", 
                                         variable=self.youtube_mode, style="Modern.TCheckbutton")
        youtube_checkbox.pack(anchor="w", padx=15, pady=10)

        # Action section
        action_section = tk.Frame(scrollable_frame, bg=ModernTheme.COLORS['bg_primary'])
        action_section.pack(fill="x", pady=(0, 20), padx=20)
        
        self.start_btn = ttk.Button(action_section, text="🚀 Create Video", 
                                   command=self.start_process, style="Modern.TButton")
        self.start_btn.pack(pady=20)

        # Progress section
        progress_section = ttk.LabelFrame(scrollable_frame, text="📊 Progress", style="Modern.TLabelframe")
        progress_section.pack(fill="both", expand=True, padx=20)
        
        self.log_box = self.create_modern_log_box(progress_section)
    
    def create_file_input(self, parent, label_text, attr_name, callback, row):
        """Create a modern file input with drag & drop"""
        # Label
        label = ttk.Label(parent, text=label_text, style="Modern.TLabel")
        label.grid(row=row, column=0, sticky="w", padx=15, pady=10)
        
        # Drop zone frame
        drop_frame = tk.Frame(parent, bg=ModernTheme.COLORS['bg_tertiary'], relief="flat", bd=1)
        drop_frame.grid(row=row, column=1, sticky="ew", padx=(10, 15), pady=10)
        parent.grid_columnconfigure(1, weight=1)
        
        # Drop zone
        drop_zone = tk.Text(drop_frame, height=2, 
                           bg=ModernTheme.COLORS['bg_tertiary'], 
                           fg=ModernTheme.COLORS['text_secondary'],
                           font=ModernTheme.FONTS['small'],
                           relief="flat", bd=0,
                           wrap="word")
        drop_zone.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Placeholder text
        placeholder = "Drag & drop file here or click to browse..."
        drop_zone.insert("1.0", placeholder)
        drop_zone.config(state="disabled")
        
        # Drag & drop functionality
        drop_zone.drop_target_register(DND_FILES)
        drop_zone.dnd_bind("<<Drop>>", callback)
        
        # Store reference
        setattr(self, f"{attr_name}_drop", drop_zone)
        
        # Click to browse functionality
        def on_click(event):
            from tkinter import filedialog
            if attr_name == "text_file":
                file_path = filedialog.askopenfilename(
                    title="Select Text File",
                    filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
                )
            elif attr_name == "video_file":
                file_path = filedialog.askopenfilename(
                    title="Select Video File",
                    filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
                )
            else:  # music file
                file_path = filedialog.askopenfilename(
                    title="Select Music File",
                    filetypes=[("Audio files", "*.mp3 *.wav *.m4a"), ("All files", "*.*")]
                )
            
            if file_path:
                # Create mock event for callback
                class MockEvent:
                    def __init__(self, data):
                        self.data = data
                callback(MockEvent(file_path))
        
        drop_zone.bind("<Button-1>", on_click)
        
        return drop_zone
    
    def create_modern_log_box(self, parent):
        """Create a modern styled log box"""
        log_frame = tk.Frame(parent, bg=ModernTheme.COLORS['bg_secondary'])
        log_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Use the theme's text widget creator
        log_box = create_modern_text_widget(log_frame, state="disabled")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=log_box.yview)
        log_box.configure(yscrollcommand=scrollbar.set)
        
        log_box.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        return log_box

    # ---------------- Advanced Mode UI ----------------
    def build_advanced_ui(self):
        self.adv_text_file = None
        self.adv_video_file = None
        self.adv_music_file = None
        self.adv_narration_file = None
        self.adv_youtube_mode = tk.BooleanVar(value=False)

        # Create scrollable container
        canvas = tk.Canvas(self.advanced_frame, bg=ModernTheme.COLORS['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.advanced_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernTheme.COLORS['bg_primary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=20)
        scrollbar.pack(side="right", fill="y", pady=20)

        # File inputs section
        file_frame = ttk.LabelFrame(scrollable_frame, text="📁 File Inputs", style="Modern.TLabelframe")
        file_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        self.create_file_input(file_frame, "📄 Text File / Narration MP3", "adv_text_file", self.set_adv_text_or_audio, 0)
        self.create_file_input(file_frame, "🎬 Background Video", "adv_video_file", self.set_adv_video, 1)
        self.create_file_input(file_frame, "🎼 Background Music (optional)", "adv_music_file", self.set_adv_music, 2)

        # Speed options section
        speed_frame = ttk.LabelFrame(scrollable_frame, text="⚡ Speed Controls", style="Modern.TLabelframe")
        speed_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        # Narration speed
        self.narration_speed = tk.DoubleVar(value=1.5)
        self.create_slider_input(speed_frame, "🎤 Narration Speed", self.narration_speed, 0.5, 3.0, 0)
        
        # Music speed
        self.music_speed = tk.DoubleVar(value=1.0)
        self.create_slider_input(speed_frame, "🎵 Music Speed", self.music_speed, 0.5, 2.0, 1)

        # Subtitle options section
        subtitle_frame = ttk.LabelFrame(scrollable_frame, text="📝 Subtitle Customization", style="Modern.TLabelframe")
        subtitle_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        # Create subtitle controls in a grid
        self.subtitle_frequency = tk.IntVar(value=3)
        self.subtitle_font = tk.StringVar(value="Impact")
        self.subtitle_font_size = tk.IntVar(value=72)
        self.subtitle_color = tk.StringVar(value="#00FFFF")
        
        self.create_subtitle_controls(subtitle_frame)

        # Format options section
        format_frame = ttk.LabelFrame(scrollable_frame, text="📺 Output Format", style="Modern.TLabelframe")
        format_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        adv_youtube_checkbox = ttk.Checkbutton(format_frame, text="📺 YouTube Mode (preserves original format for videos >3min)", 
                                             variable=self.adv_youtube_mode, style="Modern.TCheckbutton")
        adv_youtube_checkbox.pack(anchor="w", padx=15, pady=10)

        # Action section
        action_frame = tk.Frame(scrollable_frame, bg=ModernTheme.COLORS['bg_primary'])
        action_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        self.adv_start_btn = ttk.Button(action_frame, text="🚀 Create Advanced Video", 
                                       command=self.start_process_advanced, style="Modern.TButton")
        self.adv_start_btn.pack(pady=20)

        # Progress section
        progress_section = ttk.LabelFrame(scrollable_frame, text="📊 Progress", style="Modern.TLabelframe")
        progress_section.pack(fill="both", expand=True, padx=20)
        
        self.adv_log_box = self.create_modern_log_box(progress_section)
    
    def create_slider_input(self, parent, label_text, variable, min_val, max_val, row):
        """Create a modern slider input with value display"""
        # Label
        label = ttk.Label(parent, text=label_text, style="Modern.TLabel")
        label.grid(row=row, column=0, sticky="w", padx=15, pady=10)
        
        # Slider frame
        slider_frame = tk.Frame(parent, bg=ModernTheme.COLORS['bg_secondary'])
        slider_frame.grid(row=row, column=1, sticky="ew", padx=(10, 15), pady=10)
        parent.grid_columnconfigure(1, weight=1)
        
        # Slider
        slider = tk.Scale(slider_frame, from_=min_val, to=max_val, resolution=0.1,
                         orient="horizontal", variable=variable,
                         bg=ModernTheme.COLORS['bg_secondary'], fg=ModernTheme.COLORS['text_primary'],
                         highlightthickness=0, troughcolor=ModernTheme.COLORS['bg_tertiary'],
                         activebackground=ModernTheme.COLORS['accent_primary'])
        slider.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        
        # Value display
        value_label = tk.Label(slider_frame, textvariable=variable,
                              bg=ModernTheme.COLORS['bg_secondary'], fg=ModernTheme.COLORS['accent_primary'],
                              font=ModernTheme.FONTS['heading'], width=6)
        value_label.pack(side="right", padx=10, pady=5)
    
    def create_subtitle_controls(self, parent):
        """Create subtitle customization controls"""
        # Frequency
        freq_label = ttk.Label(parent, text="📊 Words per chunk:", style="Modern.TLabel")
        freq_label.grid(row=0, column=0, sticky="w", padx=15, pady=8)
        
        freq_spinbox = tk.Spinbox(parent, from_=1, to=10, textvariable=self.subtitle_frequency,
                                 bg=ModernTheme.COLORS['bg_tertiary'], fg=ModernTheme.COLORS['text_primary'],
                                 font=ModernTheme.FONTS['body'], width=10)
        freq_spinbox.grid(row=0, column=1, sticky="w", padx=(10, 15), pady=8)
        
        # Font
        font_label = ttk.Label(parent, text="🔤 Font Name:", style="Modern.TLabel")
        font_label.grid(row=1, column=0, sticky="w", padx=15, pady=8)
        
        font_combo = ttk.Combobox(parent, textvariable=self.subtitle_font, width=15,
                                 values=["Impact", "Arial", "Helvetica", "Times New Roman", "Comic Sans MS"])
        font_combo.grid(row=1, column=1, sticky="w", padx=(10, 15), pady=8)
        
        # Font size
        size_label = ttk.Label(parent, text="📏 Font Size:", style="Modern.TLabel")
        size_label.grid(row=2, column=0, sticky="w", padx=15, pady=8)
        
        size_spinbox = tk.Spinbox(parent, from_=24, to=120, textvariable=self.subtitle_font_size,
                                 bg=ModernTheme.COLORS['bg_tertiary'], fg=ModernTheme.COLORS['text_primary'],
                                 font=ModernTheme.FONTS['body'], width=10)
        size_spinbox.grid(row=2, column=1, sticky="w", padx=(10, 15), pady=8)
        
        # Color
        color_label = ttk.Label(parent, text="🎨 Font Color:", style="Modern.TLabel")
        color_label.grid(row=3, column=0, sticky="w", padx=15, pady=8)
        
        color_frame = tk.Frame(parent, bg=ModernTheme.COLORS['bg_secondary'])
        color_frame.grid(row=3, column=1, sticky="w", padx=(10, 15), pady=8)
        
        color_entry = ttk.Entry(color_frame, textvariable=self.subtitle_color, width=10, style="Modern.TEntry")
        color_entry.pack(side="left", padx=(0, 10))
        
        # Color preview
        color_preview = tk.Label(color_frame, text="  ", width=3,
                                bg=self.subtitle_color.get(), relief="solid", bd=1)
        color_preview.pack(side="left")
        
        # Update color preview when color changes
        def update_color_preview(*args):
            try:
                color_preview.config(bg=self.subtitle_color.get())
            except:
                pass
        
        self.subtitle_color.trace("w", update_color_preview)

    # ---------------- Bulk Production Mode UI ----------------
    def build_bulk_ui(self):
        self.script_dir = None
        self.video_dir = None
        self.music_dir = None
        self.bulk_youtube_mode = tk.BooleanVar(value=False)

        # Create scrollable container
        canvas = tk.Canvas(self.bulk_frame, bg=ModernTheme.COLORS['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.bulk_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernTheme.COLORS['bg_primary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=20)
        scrollbar.pack(side="right", fill="y", pady=20)

        # Directory inputs section
        dir_frame = ttk.LabelFrame(scrollable_frame, text="📂 Directory Inputs", style="Modern.TLabelframe")
        dir_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        self.create_dir_input(dir_frame, "📄 Text Files Directory", "script_dir", self.set_script_dir, 0)
        self.create_dir_input(dir_frame, "🎬 Videos Directory", "video_dir", self.set_video_dir, 1)
        self.create_dir_input(dir_frame, "🎼 Music Directory (optional)", "music_dir", self.set_music_dir, 2)

        # Format options section
        format_frame = ttk.LabelFrame(scrollable_frame, text="📺 Output Format", style="Modern.TLabelframe")
        format_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        bulk_youtube_checkbox = ttk.Checkbutton(format_frame, text="📺 YouTube Mode (preserves original format for videos >3min)", 
                                              variable=self.bulk_youtube_mode, style="Modern.TCheckbutton")
        bulk_youtube_checkbox.pack(anchor="w", padx=15, pady=10)

        # Bulk settings section
        settings_frame = ttk.LabelFrame(scrollable_frame, text="⚙️ Batch Settings", style="Modern.TLabelframe")
        settings_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        # Progress indicator
        self.progress_var = tk.DoubleVar()
        self.progress_label = ttk.Label(settings_frame, text="Ready to process", style="Modern.TLabel")
        self.progress_label.pack(pady=(15, 5))
        
        self.progress_bar = ttk.Progressbar(settings_frame, variable=self.progress_var, 
                                          maximum=100, length=400, mode='determinate')
        self.progress_bar.pack(pady=(0, 15))

        # Action section
        action_frame = tk.Frame(scrollable_frame, bg=ModernTheme.COLORS['bg_primary'])
        action_frame.pack(fill="x", pady=(0, 20), padx=20)
        
        self.bulk_start_btn = ttk.Button(action_frame, text="🚀 Start Bulk Production", 
                                        command=self.start_bulk_process, style="Modern.TButton")
        self.bulk_start_btn.pack(pady=20)

        # Progress section
        progress_section = ttk.LabelFrame(scrollable_frame, text="📊 Progress Log", style="Modern.TLabelframe")
        progress_section.pack(fill="both", expand=True, padx=20)
        
        self.bulk_log_box = self.create_modern_log_box(progress_section)
    
    def create_dir_input(self, parent, label_text, attr_name, callback, row):
        """Create a modern directory input with drag & drop"""
        # Label
        label = ttk.Label(parent, text=label_text, style="Modern.TLabel")
        label.grid(row=row, column=0, sticky="w", padx=15, pady=10)
        
        # Drop zone frame
        drop_frame = tk.Frame(parent, bg=ModernTheme.COLORS['bg_tertiary'], relief="flat", bd=1)
        drop_frame.grid(row=row, column=1, sticky="ew", padx=(10, 15), pady=10)
        parent.grid_columnconfigure(1, weight=1)
        
        # Drop zone
        drop_zone = tk.Text(drop_frame, height=2, 
                           bg=ModernTheme.COLORS['bg_tertiary'], 
                           fg=ModernTheme.COLORS['text_secondary'],
                           font=ModernTheme.FONTS['small'],
                           relief="flat", bd=0,
                           wrap="word")
        drop_zone.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Placeholder text
        placeholder = "Drag & drop directory here or click to browse..."
        drop_zone.insert("1.0", placeholder)
        drop_zone.config(state="disabled")
        
        # Drag & drop functionality
        drop_zone.drop_target_register(DND_FILES)
        drop_zone.dnd_bind("<<Drop>>", callback)
        
        # Store reference
        setattr(self, f"{attr_name}_drop", drop_zone)
        
        # Click to browse functionality
        def on_click(event):
            from tkinter import filedialog
            dir_path = filedialog.askdirectory(title=f"Select {label_text}")
            if dir_path:
                # Create mock event for callback
                class MockEvent:
                    def __init__(self, data):
                        self.data = data
                callback(MockEvent(dir_path))
        
        drop_zone.bind("<Button-1>", on_click)
        
        return drop_zone

    # ---------------- Enhanced Log Helper ----------------
    def log(self, message, advanced=False, bulk=False):
        """Enhanced logging with color coding"""
        if bulk:
            box = self.bulk_log_box
        elif advanced:
            box = self.adv_log_box
        else:
            box = self.log_box
            
        box.config(state="normal")
        
        # Determine message type and apply appropriate tag
        if "✅" in message or "complete" in message.lower():
            tag = "success"
        elif "❌" in message or "error" in message.lower():
            tag = "error"
        elif "⚠️" in message or "warning" in message.lower():
            tag = "warning"
        elif "[" in message and "/" in message and "]" in message:
            tag = "info"
        else:
            tag = None
        
        if tag:
            box.insert(tk.END, message + "\n", tag)
        else:
            box.insert(tk.END, message + "\n")
            
        box.see(tk.END)
        box.config(state="disabled")
        self.update_idletasks()

    # ---------------- Enhanced File Handlers ----------------
    def set_text(self, event):
        self.text_file = event.data.strip("{}").strip()
        self.update_drop_zone(self.text_file_drop, self.text_file, "📄 Text file loaded")

    def set_video(self, event):
        self.video_file = event.data.strip("{}").strip()
        self.update_drop_zone(self.video_file_drop, self.video_file, "🎬 Video file loaded")

    def set_music(self, event):
        self.bg_music_file = event.data.strip("{}").strip()
        self.update_drop_zone(self.bg_music_file_drop, self.bg_music_file, "🎼 Music file loaded")
    
    def update_drop_zone(self, drop_zone, file_path, success_message):
        """Update drop zone with file information"""
        drop_zone.config(state="normal")
        drop_zone.delete("1.0", tk.END)
        
        filename = os.path.basename(file_path)
        drop_zone.insert("1.0", f"{success_message}\n{filename}")
        drop_zone.config(state="disabled", fg=ModernTheme.COLORS['success'])

    def set_adv_text_or_audio(self, event):
        path = event.data.strip("{}").strip()
        if path.lower().endswith(".mp3"):
            self.adv_narration_file = path
            message = "🎤 Narration MP3 loaded"
        else:
            self.adv_text_file = path
            message = "📄 Text file loaded"
        self.update_drop_zone(self.adv_text_file_drop, path, message)

    def set_adv_video(self, event):
        self.adv_video_file = event.data.strip("{}").strip()
        self.update_drop_zone(self.adv_video_file_drop, self.adv_video_file, "🎬 Video file loaded")

    def set_adv_music(self, event):
        self.adv_music_file = event.data.strip("{}").strip()
        self.update_drop_zone(self.adv_music_file_drop, self.adv_music_file, "🎼 Music file loaded")

    # ---------------- Bulk Production File Handlers ----------------
    def set_script_dir(self, event):
        self.script_dir = event.data.strip("{}").strip()
        file_count = len(glob.glob(os.path.join(self.script_dir, "*.txt")))
        self.update_drop_zone(self.script_dir_drop, self.script_dir, f"📄 {file_count} text files found")

    def set_video_dir(self, event):
        self.video_dir = event.data.strip("{}").strip()
        video_extensions = ["*.mp4", "*.avi", "*.mov", "*.mkv", "*.wmv"]
        file_count = sum(len(glob.glob(os.path.join(self.video_dir, ext))) for ext in video_extensions)
        self.update_drop_zone(self.video_dir_drop, self.video_dir, f"🎬 {file_count} video files found")

    def set_music_dir(self, event):
        self.music_dir = event.data.strip("{}").strip()
        audio_extensions = ["*.mp3", "*.wav", "*.m4a", "*.aac"]
        file_count = sum(len(glob.glob(os.path.join(self.music_dir, ext))) for ext in audio_extensions)
        self.update_drop_zone(self.music_dir_drop, self.music_dir, f"🎼 {file_count} music files found")

    # ---------------- Processes ----------------
    def start_process(self):
        if not self.text_file or not self.video_file:
            messagebox.showerror("Error", "You must select a text file and a video file!")
            return

        try:
            self.log("[1/5] Converting text to speech (gTTS)...")
            input_audio = text_to_speech(self.text_file, "intermediate/input_audio.mp3")

            self.log("[2/5] Speeding up audio...")
            fast_audio = speed_up_audio(input_audio, "intermediate/fast_input.mp3", factor=1.5)

            # Check if YouTube mode should be used
            from utils import get_audio_duration
            audio_duration = get_audio_duration(fast_audio)
            use_youtube_format = self.youtube_mode.get() and audio_duration > 180  # 3 minutes

            if use_youtube_format:
                self.log("[3/5] Preparing video (YouTube format - preserving original dimensions)...")
                tiktok_video = prepare_video(self.video_file, fast_audio, "intermediate/youtube_video.mp4", youtube_mode=True)
            else:
                self.log("[3/5] Preparing video (TikTok format)...")
                tiktok_video = prepare_video(self.video_file, fast_audio, "intermediate/tiktok_video.mp4")

            self.log("[4/5] Transcribing audio...")
            ass_file = transcribe_and_chunk(fast_audio, "intermediate/output.ass", chunk_size=3, youtube_mode=use_youtube_format)

            self.log("[5/5] Adding subtitles and background music...")
            output_name = "video/final_youtube.mp4" if use_youtube_format else "video/final_tiktok.mp4"
            final = burn_subtitles(tiktok_video, ass_file, bg_music=self.bg_music_file, output_path=output_name)

            format_type = "YouTube" if use_youtube_format else "TikTok"
            self.log(f"✅ Process complete! {format_type} format video: {os.path.abspath(final)}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log("❌ An error occurred.")

    def start_process_advanced(self):
        if (not self.adv_text_file and not self.adv_narration_file) or not self.adv_video_file:
            messagebox.showerror("Error", "You must select text/mp3 narration and a video file!")
            return

        try:
            self.log("[1/5] Obtaining the narration", advanced=True)
            input_audio = self.adv_narration_file or text_to_speech(self.adv_text_file, "intermediate/input_audio.mp3")

            self.log("[2/5] Adjusting narration speed...", advanced=True)
            fast_audio = speed_up_audio(input_audio, "intermediate/fast_input.mp3", factor=self.narration_speed.get())

            # Check if YouTube mode should be used
            from utils import get_audio_duration
            audio_duration = get_audio_duration(fast_audio)
            use_youtube_format = self.adv_youtube_mode.get() and audio_duration > 180  # 3 minutes

            if use_youtube_format:
                self.log("[3/5] Preparing video (YouTube format - preserving original dimensions)...", advanced=True)
                tiktok_video = prepare_video(self.adv_video_file, fast_audio, "intermediate/youtube_video.mp4", youtube_mode=True)
            else:
                self.log("[3/5] Preparing video (TikTok format)...", advanced=True)
                tiktok_video = prepare_video(self.adv_video_file, fast_audio, "intermediate/tiktok_video.mp4")

            self.log("[4/5] Transcribing audio...", advanced=True)
            ass_file = transcribe_and_chunk(
                fast_audio,
                "intermediate/output.ass",
                chunk_size=self.subtitle_frequency.get(),
                font=self.subtitle_font.get(),
                font_size=self.subtitle_font_size.get(),
                color=self.subtitle_color.get(),
                youtube_mode=use_youtube_format
            )

            self.log("[5/5] Adding subtitles and background music...", advanced=True)
            output_name = "video/final_youtube.mp4" if use_youtube_format else "video/final_tiktok.mp4"
            final = burn_subtitles(tiktok_video, ass_file, bg_music=self.adv_music_file, bg_speed=self.music_speed.get(), output_path=output_name)

            format_type = "YouTube" if use_youtube_format else "TikTok"
            self.log(f"✅ Process complete! {format_type} format video: {os.path.abspath(final)}", advanced=True)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log("❌ An error occurred.", advanced=True)

    # ---------------- Bulk Process ----------------
    def start_bulk_process(self):
        if not self.script_dir or not self.video_dir:
            messagebox.showerror("Error", "You must select directories for scripts and videos!")
            return

        try:
            script_files = glob.glob(os.path.join(self.script_dir, "*.txt"))
            video_files = glob.glob(os.path.join(self.video_dir, "*"))
            music_files = glob.glob(os.path.join(self.music_dir, "*")) if self.music_dir else []

            if not script_files or not video_files:
                messagebox.showerror("Error", "No valid files found in the selected directories!")
                return

            total_files = len(script_files)
            self.log(f"🚀 Starting bulk production: {total_files} files to process", bulk=True)
            
            for idx, script_file in enumerate(script_files, start=1):
                # Update progress
                progress = (idx - 1) / total_files * 100
                self.progress_var.set(progress)
                self.progress_label.config(text=f"Processing {idx}/{total_files}: {os.path.basename(script_file)}")
                
                self.log(f"[{idx}/{total_files}] Processing {os.path.basename(script_file)}...", bulk=True)

                # Select random video and music
                video_file = random.choice(video_files)
                music_file = random.choice(music_files) if music_files else None

                # Process video (simplified logging)
                input_audio = text_to_speech(script_file, f"intermediate/input_audio_{idx}.mp3")
                fast_audio = speed_up_audio(input_audio, f"intermediate/fast_input_{idx}.mp3", factor=1.5)
                
                # Check if YouTube mode should be used
                from utils import get_audio_duration
                audio_duration = get_audio_duration(fast_audio)
                use_youtube_format = self.bulk_youtube_mode.get() and audio_duration > 180  # 3 minutes
                
                if use_youtube_format:
                    tiktok_video = prepare_video(video_file, fast_audio, f"intermediate/youtube_video_{idx}.mp4", youtube_mode=True)
                    output_name = f"video/final_youtube{idx}.mp4"
                else:
                    tiktok_video = prepare_video(video_file, fast_audio, f"intermediate/tiktok_video_{idx}.mp4")
                    output_name = f"video/final_tiktok{idx}.mp4"
                
                ass_file = transcribe_and_chunk(fast_audio, f"intermediate/output_{idx}.ass", chunk_size=3, youtube_mode=use_youtube_format)
                final = burn_subtitles(
                    tiktok_video,
                    ass_file,
                    bg_music=music_file,
                    output_path=output_name
                )

                self.log(f"✅ Created: {os.path.basename(final)}", bulk=True)

            self.log("🎉 Bulk production complete!", bulk=True)
            self.progress_var.set(100)
            self.progress_label.config(text="✅ All videos processed successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log("❌ An error occurred during bulk processing.", bulk=True)
            self.progress_label.config(text="❌ Processing failed")

if __name__ == "__main__":
    app = App()
    app.mainloop()