import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
from tkinter.font import Font
from lndcli import bleach_mode, pre_soak, wash_drive, dry
import configparser
from functions import compress_with_7zip, finish_task


class LaundryServicePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read('cfg/config.ini') 

        # Setting up the background
        self.canvas = tk.Canvas(self, width=1280, height=800)
        self.canvas.pack(fill="both", expand=True)
        image_path = "img/lnd.png"
        self.bg_image = ImageTk.PhotoImage(Image.open(image_path).resize((1280, 800), Image.Resampling.LANCZOS))
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

        # Service buttons setup
        self.service_buttons = []
        button_font = Font(family="Helvetica", size=16)  # Adjust font size to fit the button
        service_names = ["Bleach", "Pre-soak", "Wash", "Dry", "Fold", "Tidy up"]
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
            self.canvas.create_window(x_start + (i % 3) * 300, y_start + (i // 3) * 120, window=button, anchor="nw")  # Adjusted spacing

    def add_legend_text(self):
        descriptions = [
            "Bleach: Moves data from a dirty drive to a specified destination directory, while also deleting prohibited files and directories.",
            "Pre-soak: Deletes prohibited files before the main wash cycle.",
            "Wash: Scans the drive with antivirus software to clean it.",
            "Dry: Marks the drive as read-only to protect its contents.",
            "Fold: Uploads the cleaned data to Google Drive.",
            "Tidy up: Compresses and organizes the cleaned data."
        ]
        legend_font = Font(family="Helvetica", size=12)
        y_start = 550  # Starting position of the legend text, adjust as needed
        for i, desc in enumerate(descriptions):
            label = tk.Label(self, text=desc, font=legend_font, fg="white", bg="steelblue4", justify="left")
            self.canvas.create_window(160, y_start + i * 20, window=label, anchor="nw", width=960)

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
        if name == "Bleach":
            self.run_bleach_service()
        elif name == "Pre-soak":
            self.run_pre_soak_service()
        elif name == "Wash":
            self.run_wash_service()
        elif name == "Dry":
            self.run_dry_service()
        else:
            print(f"Handling service: {name}")
            # Add cases for other services as needed.

    def run_bleach_service(self):
        destination_name = simpledialog.askstring("Destination Name", "Enter the User's Real Name as Last.First:", parent=self)
        if destination_name:
            confirm = messagebox.askyesno("Confirm", "Are you sure you want to proceed with Bleach mode?", parent=self)
            if confirm:
                # Retrieve directories from the configuration
                source_dir = self.config.get('Directories', 'SourceDirectory', fallback='/dev/null')
                destination_dir = self.config.get('Directories', 'DestinationDirectory', fallback='/dev/null')

                # Call bleach_mode with GUI adjustments
                try:
                    message = bleach_mode(destination_name, source_dir, destination_dir, self.finish_task_gui)
                except Exception as e:
                    messagebox.showerror("Error", str(e), parent=self)
        else:
            messagebox.showwarning("Cancelled", "Bleach mode cancelled.", parent=self)

    def run_pre_soak_service(self):
        config = self.config  
        destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/dev/null')
        try:
            pre_soak_message = pre_soak(self.config, self.finish_task_gui)  # Adjusted call for GUI
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def run_wash_service(self):
        try:
            wash_result = wash_drive(self.config, self.finish_task_gui)
            messagebox.showinfo("Wash Complete", wash_result)
        except Exception as e:
            messagebox.showerror("Wash Error", str(e))

    def run_dry_service(self):
        try:
            dry_result = dry(self.config, self.finish_task_gui)
            messagebox.showinfo("Dry Complete", dry_result)
        except Exception as e:
            messagebox.showerror("Dry Error", str(e))


    @staticmethod
    def finish_task_gui(message):
        # This method might play a sound and show a message box similar to the CLI's finish_task
        messagebox.showinfo("Task Completed", message)
        
    def configure_service(self):
        self.controller.show_frame("ConfigPage")
