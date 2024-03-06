import os
import shutil
import subprocess
from pathlib import Path
import time
import pygame
import configparser
import fnmatch
import shlex
import urllib.request
import tarfile
import datetime
import stat

# Define the directory where the script is located
script_dir = Path(__file__).resolve().parent

# Initialize pygame audio mixer
pygame.mixer.init()

# Function to display the banner
def display_banner():
    while True:
        # Clear the screen
        #subprocess.run("clear", shell=True)

        # Color codes
        dark_red = "\033[38;5;160m"
        reset_color = "\033[0m"

        # Banner with ASCII art centered and bordered
        banner_text = f"""\
    {dark_red}+{'-' * 84}+{reset_color}
    {dark_red}|{reset_color}{' ' * 84}{dark_red}|{reset_color}
    {dark_red}|{reset_color}{' ' * 84}{dark_red}|{reset_color}
    {dark_red}|{'██╗    ██╗██╗███████╗██╗'.center(84)}{dark_red}|{reset_color}
    {dark_red}|{'██║    ██║██║██╔════╝██║'.center(84)}{dark_red}|{reset_color}
    {dark_red}|{'██║ █╗ ██║██║█████╗  ██║'.center(84)}{dark_red}|{reset_color}
    {dark_red}|{'██║███╗██║██║██╔══╝  ██║'.center(84)}{dark_red}|{reset_color}
    {dark_red}|{'╚███╔███╔╝██║██║     ██║'.center(84)}{dark_red}|{reset_color}
    {dark_red}|{' ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝'.center(84)}{dark_red}|{reset_color}
    {dark_red}|{reset_color}{' ' * 84}{dark_red}|{reset_color}                    
    {dark_red}|{'███████╗██╗  ██╗ █████╗ ██████╗ ██╗  ██╗'.center(84)}{dark_red}|{reset_color}
    {dark_red}|{'██╔════╝██║  ██║██╔══██╗██╔══██╗██║ ██╔╝'.center(84)}{dark_red}|{reset_color}
    {dark_red}|{'███████╗███████║███████║██████╔╝█████╔╝ '.center(84)}{dark_red}|{reset_color}
    {dark_red}|{'╚════██║██╔══██║██╔══██║██╔══██╗██╔═██╗ '.center(84)}{dark_red}|{reset_color}
    {dark_red}|{'███████║██║  ██║██║  ██║██║  ██║██║  ██╗'.center(84)}{dark_red}|{reset_color}
    {dark_red}|{'╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝'.center(84)}{dark_red}|{reset_color}
    {dark_red}|{reset_color}{' ' * 84}{dark_red}|{reset_color}
    {dark_red}|{reset_color}{' ' * 84}{dark_red}|{reset_color}
    {dark_red}|{reset_color}{'WiFi Control Center'.center(84)}{dark_red}|{reset_color}
    {dark_red}|{reset_color}{'Created by Captain ASIC'.center(84)}{dark_red}|{reset_color}
    {dark_red}|{reset_color}{'Version 1.0, Mar 2024'.center(84)}{dark_red}|{reset_color}
    {dark_red}|{reset_color}{' ' * 84}{dark_red}|{reset_color}
    {dark_red}+{'-' * 84}+{reset_color}
    """

        print(banner_text)
        break

# Function to play start sound
def play_start_sound():
    # Your sound playing code here
    pass

# Function to scan for SSID's
def scan_for_ssids():
    # Your scan for SSID's code here
    pass

# Function to de-auth SSID's
def deauth_ssids():
    # Your de-auth SSID's code here
    pass

# Function to install prerequisites
def install_prerequisites():
    print("Installing prerequisites...")
    download_and_install()
    subprocess.run(["sudo", "apt", "update"])
    result = subprocess.run(["sudo", "apt", "install", "-y", "lsusb lspci libnl-dev build-essential libstdc++-dev"], capture_output=True, text=True)
    if result.returncode == 0:
        print("Prerequisites Installed")
    else:
        print("Error installing prerequisites.")

    # Additional commands for installing aircrack-ng
    print("Installing aircrack-ng...")
    subprocess.run(["wget", "https://download.aircrack-ng.org/aircrack-ng-1.7.tar.gz"])
    subprocess.run(["tar", "-zxvf", "aircrack-ng-1.7.tar.gz"])
    os.chdir("aircrack-ng-1.7")
    subprocess.run(["autoreconf", "-i"])
    subprocess.run(["./configure", "--with-experimental"])
    subprocess.run(["make"])
    subprocess.run(["sudo", "make", "install"])
    subprocess.run(["sudo", "ldconfig"])

    print("Aircrack-ng Installed")

    # Wait for user input before returning to the main menu
    input("Press Enter to return to the main menu...")

# Function to display the menu
def display_menu():
    print("Menu:")
    print("1. Scan for SSID's")
    print("2. De-Auth SSID's")
    print("I. Install Prerequisites")
    print("Q. Quit Script")
    # Add other menu items as needed

# Function to handle user input
def handle_menu_choice(choice):
    if choice == '1':
        scan_for_ssids()
    elif choice == '2':
        deauth_ssids()
    elif choice == 'I':
        install_prerequisites()
    elif choice == 'Q':
        print("Quitting script...")
        exit()
    else:
        print("Invalid choice. Please enter 1, 2, I, or Q.")
    # Add more conditions for other menu items

# Main function
def main():
    # Display banner
    display_banner()

    # Play start sound
    play_start_sound()

    while True:
        # Clear the screen
        subprocess.run("clear", shell=True)

        # Display the menu
        display_menu()

        # Get user input
        choice = input("Enter your choice: ")

        # Handle user choice
        handle_menu_choice(choice)

# Run the main function if the script is executed
if __name__ == "__main__":
    main()
