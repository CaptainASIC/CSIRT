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
        # Indicate the start of the installation process
        messagebox.showinfo("Starting Installation", "Beginning Aircrack-ng installation. This may take some time.", parent=self)

        try:
            # Define the commands to download, extract, build, and install Aircrack-ng from source
            commands = [
                ["wget", "https://download.aircrack-ng.org/aircrack-ng-1.7.tar.gz", "-O", "/tmp/aircrack-ng-1.7.tar.gz"],
                ["tar", "-zxvf", "/tmp/aircrack-ng-1.7.tar.gz", "-C", "/tmp"],
                ["autoreconf", "-i"],
                ["./configure", "--with-experimental"],
                ["make"],
                ["sudo", "make", "install"],
                ["sudo", "ldconfig"]
            ]

            # Change directory to the extracted source code directory
            os.chdir("/tmp/aircrack-ng-1.7")

            # Execute each command in the list
            for command in commands:
                subprocess.run(command, check=True)

            # Inform the user of successful installation
            messagebox.showinfo("Installation Success", "Aircrack-ng was successfully installed.", parent=self)

        except subprocess.CalledProcessError as e:
            # In case of an error, display an error message
            messagebox.showerror("Installation Failed", f"Aircrack-ng installation failed. Error: {str(e)}", parent=self)


