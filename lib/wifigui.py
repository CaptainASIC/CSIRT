import subprocess
import os
import tkinter as tk
from tkinter import Frame, Label, Button, messagebox, ttk
from tkinter.font import Font
from PIL import Image, ImageTk
import configparser

class WifiSharkPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read('cfg/config.ini')

        # Setting up the background
        self.canvas = tk.Canvas(self, width=1280, height=800)
        self.canvas.pack(fill="both", expand=True)
        image_path = "img/shark.png"
        self.bg_image = ImageTk.PhotoImage(Image.open(image_path).resize((1280, 800), Image.Resampling.LANCZOS))
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

        # Service buttons setup
        self.service_buttons = []
        button_font = Font(family="Helvetica", size=16)  # Adjust font size to fit the button
        service_names = ["Scan for SSIDs", "De-Auth SSIDs", "WEP Crack"]
        self.create_service_buttons(service_names, button_font)

        # Dropdown for SSID selection
        self.ssid_var = tk.StringVar()
        self.ssid_dropdown = ttk.Combobox(self, textvariable=self.ssid_var, values=["Scan SSIDs first"], state="readonly")
        self.ssid_dropdown.set("Scan SSIDs first")
        self.canvas.create_window(640, 450, window=self.ssid_dropdown, anchor="nw")

        # Label for the dropdown
        self.ssid_label = Label(self, text="SSID to Attack:", font=button_font, bg='steelblue4', fg='white')
        self.canvas.create_window(430, 450, window=self.ssid_label, anchor="nw")

        # Placement for "Back" and "Exit" buttons
        self.setup_control_buttons(button_font)

    def create_service_buttons(self, service_names, button_font):
        button_dimensions = {'width': 18, 'height': 2}  # Adjusted for text units, not pixels
        x_start, y_start = 230, 300  # Adjust starting position
        for i, name in enumerate(service_names):
            button = tk.Button(self, text=name, font=button_font, bg='steelblue4', fg='white', command=lambda n=name: self.handle_service(n), **button_dimensions)
            self.service_buttons.append(button)  # Keep reference
            self.canvas.create_window(x_start + (i % 3) * 300, y_start + (i // 3) * 120, window=button, anchor="nw")  # Adjusted spacing

    def setup_control_buttons(self, button_font):
        text_font = Font(family="Helvetica", size=16)
        # "Back" button
        back_btn = tk.Button(self, text="← Back", font=text_font, bg='steelblue4', fg='white', command=lambda: self.controller.show_frame("StartPage"))
        self.canvas.create_window(120, 760, window=back_btn)

        # "Exit" button
        exit_btn = tk.Button(self, text="Exit", font=text_font, bg='steelblue4', fg='white', command=self.controller.quit)
        self.canvas.create_window(1160, 760, window=exit_btn)

        # "Configure" button
        configure_btn = tk.Button(self, text="Configure", font=text_font, bg='steelblue4', fg='white', command=self.configure_service)
        self.canvas.create_window(640, 700, window=configure_btn)  # Adjusted position

    def handle_service(self, name):
        if name == "Scan for SSIDs":
            self.scan_for_ssids()
        elif name == "De-Auth SSIDs":
            messagebox.showinfo("Info", "De-authenticating SSIDs... (functionality to be implemented)")
        elif name == "WEP Crack":
            messagebox.showinfo("Info", "WEP Cracking... (functionality to be implemented)")
        elif name == "Configure":
            self.configure_service()

    def scan_for_ssids(self):
        messagebox.showinfo("Info", "Scanning for SSIDs... (functionality to be implemented)")  

    def configure_service(self):
        self.controller.show_frame("WifiConfigPage")
