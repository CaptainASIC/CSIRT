import tkinter as tk
from PIL import Image, ImageTk
from tkinter.font import Font
from tkinter import messagebox
import configparser

class ConfigPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config = configparser.ConfigParser()
        self.config.read('cfg/config.ini')
        
        # Create a Canvas for the background
        self.canvas = tk.Canvas(self, width=1280, height=800)
        self.canvas.pack(fill="both", expand=True)
        
        # Load and set the background image
        image_path = "img/lnd.png"
        img = Image.open(image_path).resize((1280, 800), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)
        
        # Add widgets on the canvas
        self.create_widgets_on_canvas()

    def create_widgets_on_canvas(self):
        # Define fonts
        text_font = Font(family="Helvetica", size=16)
        
        # Configuration fields and labels
        config_fields = [
            ("Source Directory", "Directories", "sourcedirectory"),
            ("Destination Directory", "Directories", "destinationdirectory"),
            ("Google Drive Folder ID", "GoogleDrive", "FolderID")
        ]
        
        for i, (label_text, section, option) in enumerate(config_fields, start=1):
            label = tk.Label(self, text=label_text, font=text_font, bg='steelblue4', fg='white')
            entry_var = tk.StringVar(value=self.config.get(section, option, fallback=""))
            entry = tk.Entry(self, textvariable=entry_var, font=text_font, width=40)
            
            # Positioning widgets on the canvas
            self.canvas.create_window(640, 160 + i*60, window=label)
            self.canvas.create_window(640, 190 + i*60, window=entry)

        # Save Config button
        save_btn = tk.Button(self, text="Save Config", font=text_font, command=self.save_config)
        self.canvas.create_window(640, 500, window=save_btn)

        # Control buttons
        back_btn = tk.Button(self, text="← Back", font=text_font, command=lambda: self.controller.show_frame("LaundryServicePage"))
        exit_btn = tk.Button(self, text="Exit", font=text_font, command=self.quit_app)
        self.canvas.create_window(120, 760, window=back_btn)
        self.canvas.create_window(1160, 760, window=exit_btn)

    def save_config(self):
        # Logic to save the configurations
        with open('cfg/config.ini', 'w') as configfile:
            self.config.write(configfile)
        
        # Display a popup message
        messagebox.showinfo("Configuration Saved", "Your configuration has been successfully saved.", parent=self)


    def quit_app(self):
        self.controller.quit()
