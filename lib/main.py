import tkinter as tk
from PIL import Image, ImageTk
from tkinter.font import Font
from lndgui import LaundryServicePage 
from cfggui import ConfigPage
from wifigui import WifiSharkPage
from wificfg import WifiConfigPage
from logVoodoo import LogVoodooPage
from functions import APP_VERSION

class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title(f"Captain ASIC's CSIRT Toolbox - Version {APP_VERSION}")
        self.geometry("1280x800")
        self.resizable(False, False)
        self.configure(bg='gray5')

        # Container frame
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, LaundryServicePage, LogVoodooPage, ConfigPage, WifiSharkPage, WifiConfigPage):
            frame = F(parent=container, controller=self)
            self.frames[F.__name__] = frame  # Use class name as string identifier
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg='gray5')
        self.controller = controller

        # Initialize a Canvas
        self.canvas = tk.Canvas(self, width=1280, height=800)
        self.canvas.pack(fill="both", expand=True)

        # Load and scale wallpaper
        wallpaper_path = "img/asic-csirt.png"  
        wallpaper = Image.open(wallpaper_path)
        wallpaper = wallpaper.resize((1280, 800), Image.Resampling.LANCZOS)
        wallpaper_tk = ImageTk.PhotoImage(wallpaper)

        # Set wallpaper on the canvas
        self.canvas.create_image(0, 0, anchor='nw', image=wallpaper_tk)
        self.canvas.image = wallpaper_tk  # Keep a reference!

        # Stylized banner text for 'CSIRT Toolbox'
        self.banner_font = Font(family="Helvetica", size=60, weight="bold")  # Customize as needed
        text_bg = self.canvas.create_rectangle(100, 60, 1180, 150, fill='black', outline='black')
        self.canvas.create_text(640, 60, text="CSIRT Toolbox", font=self.banner_font, fill="orange", anchor="n")

        # Font configuration for buttons
        button_font = Font(family="Helvetica", size=10, weight="bold")

        # Create a Laundry Service button
        laundry_service_button = tk.Button(self, text="Laundry Service", font=button_font, command=lambda: controller.show_frame("LaundryServicePage"))
        self.canvas.create_window(540, 700, window=laundry_service_button)
        
        # Create a Log Voodoo button
        log_voodoo_button = tk.Button(self, text="Log Voodoo", font=button_font, command=lambda: controller.show_frame("LogVoodooPage"))
        self.canvas.create_window(640, 700, window=log_voodoo_button)

        # Create a Wifi Shark button
        wifi_shark_button = tk.Button(self, text="WiFi Shark", font=button_font, command=lambda: controller.show_frame("WifiSharkPage"))
        self.canvas.create_window(740, 700, window=wifi_shark_button)


        # Create a Quit button with bold text
        quit_button = tk.Button(self, text="Quit", font=button_font, command=controller.quit)
        self.canvas.create_window(1260, 760, anchor="se", window=quit_button)
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
