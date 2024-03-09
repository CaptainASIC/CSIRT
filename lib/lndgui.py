import tkinter as tk
from PIL import Image, ImageTk
from tkinter.font import Font

class LaundryServicePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Load and display 'lnd.png'
        image_path = "img/lnd.png"  # Corrected the path
        img = Image.open(image_path)
        img = img.resize((1280, 800), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        # Set the image as a background
        label_image = tk.Label(self, image=img_tk)
        label_image.place(x=0, y=0, relwidth=1, relheight=1)
        label_image.image = img_tk  # Keep a reference

        # Create a container for service buttons without specifying a background color
        buttons_frame = tk.Frame(self, bg='steelblue4')
        buttons_frame.place(relx=0.5, rely=0.5, y=50, anchor='n')

        # Font configuration for larger buttons
        button_font = Font(family="Helvetica", size=18, weight="bold")

        # Define button style with 'steelblue4' background to match the theme
        button_style = {'font': button_font, 'fg': 'white', 'bg': 'steelblue4', 'activebackground': 'steelblue3'}

        # Service buttons setup
        service_names = ["Bleach", "Pre-soak", "Wash", "Dry", "Fold", "Tidy up"]
        button_width = 10  # Adjusted for larger buttons
        button_height = 2  # Adjusted for larger buttons
        for i, name in enumerate(service_names):
            button = tk.Button(buttons_frame, text=name, width=button_width, height=button_height, **button_style, command=lambda n=name: self.handle_service(n))
            button.grid(row=i//3, column=i%3, padx=10, pady=10, sticky='ew')

        # Control buttons at the bottom, following a similar styling approach
        control_frame = tk.Frame(self, bg='steelblue4')
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

        # Back button
        back_button = tk.Button(control_frame, text="← Back", **button_style, command=lambda: controller.show_frame("StartPage"))
        back_button.pack(side=tk.LEFT, padx=20, anchor='s')

        # Configure button
        configure_button = tk.Button(control_frame, text="Configure", **button_style, command=self.configure_service)
        configure_button.pack(side=tk.LEFT, expand=True, anchor='s')

        # Quit button
        quit_button = tk.Button(control_frame, text="Quit", **button_style, command=controller.quit)
        quit_button.pack(side=tk.LEFT, padx=20, anchor='s')

    def handle_service(self, name):
        print(f"Handling service: {name}")
        # Placeholder for handling each service

    def configure_service(self):
        self.controller.show_frame("ConfigPage")


