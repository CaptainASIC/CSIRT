import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from tkinter.font import Font
import configparser

class ConfigPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config = configparser.ConfigParser()
        self.config.read('cfg/config.ini')
        
        self.canvas = tk.Canvas(self, width=1280, height=800)
        self.canvas.pack(fill="both", expand=True)
        
        image_path = "img/csirt.png"
        img = Image.open(image_path).resize((1280, 800), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)
        
        self.create_widgets_on_canvas()

    def create_widgets_on_canvas(self):
        text_font = Font(family="Helvetica", size=16)
        
        config_fields = [
            ("Source Directory", "Directories", "sourcedirectory", "red4", self.browse_directory),
            ("Destination Directory", "Directories", "destinationdirectory", "dark green", self.browse_directory),
            ("Cloud Storage Name", "RemoteDrive", "RemoteName", None, None),  # No special color or browse button
            ("Cloud Storage Folder", "RemoteDrive", "BasePath", None, None),  # No special color or browse button
            ("Patterns File", "Settings", "patterns_file", None, self.browse_file),  # New field for patterns file
            ("Log Search Directory", "Settings", "log_directory", None, self.browse_directory)  # New field for log search directory
        ]
        
        self.entries = {}  # Dictionary to store entry widgets
        
        for i, (label_text, section, option, bg_color, browse_command) in enumerate(config_fields, start=1):
            label = tk.Label(self, text=label_text, font=text_font, bg='steelblue4', fg='white')
            entry_var = tk.StringVar(value=self.config.get(section, option, fallback=""))
            entry = tk.Entry(self, textvariable=entry_var, font=text_font, width=40, bg=bg_color if bg_color else 'white')
            
            self.canvas.create_window(640, 160 + i*60, window=label)
            self.canvas.create_window(640, 190 + i*60, window=entry)
            
            if browse_command:
                browse_button = tk.Button(self, text="Browse", command=lambda e=entry_var, c=browse_command: c(e))
                self.canvas.create_window(920, 190 + i*60, window=browse_button)
            
            self.entries[(section, option)] = entry_var  # Store the entry variable for saving

        save_btn = tk.Button(self, text="Save Config", font=text_font, bg='steelblue4', fg='white', command=self.save_config)
        self.canvas.create_window(640, 600, window=save_btn)

        back_btn = tk.Button(self, text="← Back", font=text_font, bg='steelblue4', fg='white', command=lambda: self.controller.show_frame("StartPage"))
        exit_btn = tk.Button(self, text="Exit", font=text_font, bg='steelblue4', fg='white', command=self.quit_app)
        self.canvas.create_window(120, 760, window=back_btn)
        self.canvas.create_window(1160, 760, window=exit_btn)

    def browse_directory(self, entry_var):
        directory = filedialog.askdirectory()
        if directory:
            entry_var.set(directory)

    def browse_file(self, entry_var):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            entry_var.set(filename)

    def save_config(self):
        for (section, option), entry_var in self.entries.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            self.config.set(section, option, entry_var.get())
        
        with open('cfg/config.ini', 'w') as configfile:
            self.config.write(configfile)
        
        messagebox.showinfo("Configuration Saved", "Your configuration has been successfully saved.", parent=self)

    def quit_app(self):
        self.controller.quit()
