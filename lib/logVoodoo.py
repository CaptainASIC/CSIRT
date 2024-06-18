import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
from tkinter.font import Font
import configparser

class LogVoodooPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read('cfg/config.ini')

        # Setting up the background
        self.canvas = tk.Canvas(self, width=1280, height=800)
        self.canvas.pack(fill="both", expand=True)
        image_path = "img/lvd.png"  # Placeholder image path
        self.bg_image = ImageTk.PhotoImage(Image.open(image_path).resize((1280, 800), Image.Resampling.LANCZOS))
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

        # Service buttons setup
        self.service_buttons = []
        button_font = Font(family="Helvetica", size=16)  # Adjust font size to fit the button
        service_names = ["Log Clean", "Log Archive", "Log Rotate", "Log Search", "Log Delete"]
        self.create_service_buttons(service_names, button_font)

        # Add legend text
        self.add_legend_text()

        # Placement for "Configure", "Back", and "Exit" buttons
        self.setup_control_buttons(button_font)

    def create_service_buttons(self, service_names, button_font):
        button_dimensions = {'width': 18, 'height': 2}  # Adjusted for text units, not pixels
        x_start, y_start = 230, 300  # Adjust starting position
        for i, name in enumerate(service_names):
            button = tk.Button(self, text=name, font=button_font, bg='steelblue4', fg='white', command=lambda n=name: self.handle_service(n), **button_dimensions)
            self.service_buttons.append(button)  # Keep reference
            self.canvas.create_window(x_start + (i % 3) * 300, y_start + (i // 3) * 100, window=button)

    def handle_service(self, service_name):
        # Placeholder for service handling logic
        messagebox.showinfo("Service", f"Service {service_name} is selected.")

    def add_legend_text(self):
        # Placeholder for adding legend text
        legend_text = "Select a log service to proceed."
        self.canvas.create_text(640, 100, text=legend_text, font=Font(family="Helvetica", size=24), fill="white")

    def setup_control_buttons(self, button_font):
        # Placeholder for control buttons
        control_button_config = {
            'Configure': (150, 700),
            'Back': (590, 700),
            'Exit': (1030, 700)
        }
        for name, (x, y) in control_button_config.items():
            button = tk.Button(self, text=name, font=button_font, bg='gray', fg='black', command=lambda n=name: self.handle_control(n))
            self.canvas.create_window(x, y, window=button)

    def handle_control(self, control_name):
        # Placeholder for control handling logic
        if control_name == 'Exit':
            self.controller.quit()
        else:
            messagebox.showinfo("Control", f"Control {control_name} is selected.")

# Main application setup for testing purposes
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Log Voodoo")
    LogVoodooPage(root, None).pack(fill="both", expand=True)
    root.mainloop()
