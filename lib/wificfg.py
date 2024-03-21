import tkinter as tk
from tkinter import messagebox
from tkinter.font import Font
from PIL import Image, ImageTk
import subprocess
import os
import configparser


class WifiConfigPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config = configparser.ConfigParser()
        self.config.read('cfg/config.ini')
        
        self.canvas = tk.Canvas(self, width=1280, height=800)
        self.canvas.pack(fill="both", expand=True)
        
        image_path = "img/shark.png"
        img = Image.open(image_path).resize((1280, 800), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

        self.create_widgets_on_canvas()

    def create_widgets_on_canvas(self):
        text_font = Font(family="Helvetica", size=16)
        
        # Title Label
        label_title = tk.Label(self, text="WiFi Shark Configuration", font=Font(family="Helvetica", size=20, weight="bold"), bg='steelblue4', fg='white')
        self.canvas.create_window(640, 100, window=label_title)
        
        # Install Aircrack-ng Button
        btn_install_aircrack = tk.Button(self, text="Install Aircrack-ng", font=text_font, bg='steelblue4', fg='white', command=self.install_aircrack)
        self.canvas.create_window(640, 250, window=btn_install_aircrack)
        
        # Back Button
        back_btn = tk.Button(self, text="← Back", font=text_font, bg='steelblue4', fg='white', command=lambda: self.controller.show_frame("WifiSharkPage"))
        self.canvas.create_window(120, 760, window=back_btn)

        # Exit Button
        exit_btn = tk.Button(self, text="Exit", font=text_font, bg='steelblue4', fg='white', command=self.controller.quit)
        self.canvas.create_window(1160, 760, window=exit_btn)

    def install_aircrack(self):
        # URL of the Aircrack-ng tar.gz file
        aircrack_url = "https://download.aircrack-ng.org/aircrack-ng-1.7.tar.gz"
        # Path where the tar.gz file will be saved
        download_path = "/tmp/aircrack-ng-1.7.tar.gz"
        # Path for the extracted content
        extract_dir = "/tmp/aircrack-ng-1.7"

        try:
            # Indicate start of download
            messagebox.showinfo("Download", "Starting the download of Aircrack-ng.", parent=self)
            # Downloading the tar.gz file
            response = requests.get(aircrack_url)
            with open(download_path, 'wb') as file:
                file.write(response.content)
            messagebox.showinfo("Download Complete", "Aircrack-ng downloaded successfully.", parent=self)

            # Extracting the tar.gz file
            with tarfile.open(download_path, "r:gz") as tar:
                tar.extractall(path="/tmp")

            # Change directory to the extracted folder
            os.chdir(extract_dir)

            # Compilation and installation process
            subprocess.check_call(["autoreconf", "-i"])
            subprocess.check_call(["./configure", "--with-experimental"])
            subprocess.check_call(["make"])
            subprocess.check_call(["sudo", "make", "install"])
            subprocess.check_call(["sudo", "ldconfig"])
            
            messagebox.showinfo("Installation Complete", "Aircrack-ng has been successfully installed.", parent=self)
        except Exception as e:
            messagebox.showerror("Installation Error", f"Failed to install Aircrack-ng: {e}", parent=self)