import tkinter as tk
from PIL import Image, ImageTk
from tkinter.font import Font
from lndgui import LaundryServicePage 
from cfggui import ConfigPage
class MainApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("ASIC's CSIRT Services - Version 2.0.3")
        self.geometry("1280x800")
        self.resizable(False, False)
        self.configure(bg='gray5')

        # Container frame
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, LaundryServicePage, ConfigPage):
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

        # Load and display 'ASIC.png' with a specified width
        image_path = "img/ASIC.png"  # Adjust the path to your actual image location
        img = Image.open(image_path)
        aspect_ratio = img.height / img.width
        new_width = 500
        new_height = int(new_width * aspect_ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        label_image = tk.Label(self, image=img_tk, bg='gray5')
        label_image.image = img_tk  # Keep a reference to avoid garbage collection
        label_image.pack(pady=20)

        # Font configuration for buttons
        button_font = Font(family="Helvetica", size=10, weight="bold")

        # Create a Laundry Service button
        laundry_service_button = tk.Button(self, text="Laundry Service", font=button_font, command=lambda: controller.show_frame("LaundryServicePage"))
        laundry_service_button.pack(pady=10)

        # Create a Quit button with bold text
        quit_button = tk.Button(self, text="Quit", font=button_font, command=controller.quit)
        quit_button.pack(side=tk.BOTTOM, anchor='se', padx=20, pady=20)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
