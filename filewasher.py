import os
import shutil
import subprocess
from pathlib import Path
import time
import pygame
import configparser

# Get the directory where the script is located
script_dir = Path(__file__).resolve().parent

# Initialize pygame audio mixer
pygame.mixer.init()

# Function to play start sound
def play_start_sound():
    sound_file = script_dir / "snd/start.mp3"
    pygame.mixer.music.load(str(sound_file))
    pygame.mixer.music.play()

# Function to wash the drive
def bleach_mode():
    # Construct the full destination directory path
    destination_name = input("Enter the User's Real Name as Last.First: ")
    if not destination_name:
        print("Error: Destination directory name is required.")
        return

    destination_dir = f'/media/cleaner/Passport/{destination_name}'
    print("Destination directory:", destination_dir)

    # Record start time
    start_time = time.time()
    print("Starting file copy...")

    # Read extensions from the reference file
    extensions_file = script_dir / "extensions.bsd"
    with open(extensions_file) as f:
        extensions = [f"--include '={line.strip()}'" for line in f]

    # Perform the file copy using rsync
    source_dir = "/media/cleaner/Windows/Users"
    rsync_command = f"rsync -av --stats {' '.join(extensions)} --exclude='*.*' --exclude='desktop.ini' --exclude='/administrator/' --exclude='/Default/' --excluded='/Public/' {source_dir}/ {destination_dir}"
    print("Rsync command:", rsync_command)
    rsync_result = subprocess.run(rsync_command, shell=True, capture_output=True, text=True)
    print("Rsync output:", rsync_result.stdout)

    print("File copy completed.")

    # Extract the number of files copied and total file size
    rsync_output = subprocess.run(f"rsync --stats {source_dir}/ {destination_dir}", shell=True, capture_output=True, text=True)
    print("Second rsync output:", rsync_output.stdout)
    stats = rsync_output.stdout.splitlines()
    copied_files = int([line.split()[5] for line in stats if 'Number of regular files transferred' in line][0])
    total_size = int([line.split()[5] for line in stats if 'Total transferred file size' in line][0])

    print(f"Number of files copied: {copied_files}")
    print("Total file size:", convert_bytes(total_size))

    # Delete prohibited files
    print("Deleting prohibited files...")
    prohibited_file = script_dir / "prohibited.bsd"
    delete_prohibited_files(destination_dir, prohibited_file)

    # Clean up empty directories in the destination directory
    print(f"Cleaning up empty directories in {destination_dir}...")
    clean_empty_directories(destination_dir)

    # Calculate elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Output the elapsed time
    print("Total time taken:", convert_seconds(int(elapsed_time)))

    # Finish
    midi_file = script_dir / "snd/ffvii.mp3"
    pygame.mixer.music.load(str(midi_file))
    pygame.mixer.music.play()
    input("Press Enter to return to the main menu...")  # Wait for user input

# Function to clean the drive
def wash_drive():
    # Stop clamav-freshclam service
    subprocess.run(["sudo", "service", "clamav-freshclam", "stop"])

    # Update ClamAV signatures
    subprocess.run(["sudo", "freshclam"])

    # Start clamav-freshclam service
    subprocess.run(["sudo", "service", "clamav-freshclam", "start"])

    # Run ClamAV scan on the specified folder and its subfolders
    folder_path = "/media/cleaner/Passport"
    print("Running ClamAV scan on the folder and its subfolders...")
    subprocess.run(["clamscan", "-r", folder_path])
    
    # Finish
    midi_file = script_dir / "snd/ffvii.mp3"
    pygame.mixer.music.load(str(midi_file))
    pygame.mixer.music.play()
    print("Scan Complete")
    input("Press Enter to return to the main menu...")  # Wait for user input

# Function to install prerequisites
def install_prerequisites():
    print("Installing prerequisites...")
    subprocess.run(["sudo", "apt", "update"])
    result = subprocess.run(["sudo", "apt", "install", "-y", "clamav"], capture_output=True, text=True)
    if result.returncode == 0:
        print("Prerequisites Installed")
    else:
        print("Error installing prerequisites.")

    # Wait for user input before returning to the main menu
    input("Press Enter to return to the main menu...")

def configure_directories():
    # Read current configuration
    config = configparser.ConfigParser()
    config.read(script_dir / 'config.ini')

    source_dir = config.get('Directories', 'SourceDirectory', fallback='/media/cleaner/Windows/Users')
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/media/cleaner/Passport')

    print(f"Current source directory: {source_dir}")
    change_source_dir = input("Do you want to change the source directory? (y/n): ").lower()

    if change_source_dir == 'y':
        new_source_dir = input("Enter the new source directory: ")
        config.set('Directories', 'SourceDirectory', new_source_dir)
        with open(script_dir / 'config.ini', 'w') as configfile:
            config.write(configfile)
        print("Source directory updated successfully.")
    else:
        print("Keeping the current source directory.")

    print(f"Current destination directory: {destination_dir}")
    change_dest_dir = input("Do you want to change the destination directory? (y/n): ").lower()

    if change_dest_dir == 'y':
        new_dest_dir = input("Enter the new destination directory: ")
        config.set('Directories', 'DestinationDirectory', new_dest_dir)
        with open(script_dir / 'config.ini', 'w') as configfile:
            config.write(configfile)
        print("Destination directory updated successfully.")
    else:
        print("Keeping the current destination directory.")

    input("Press Enter to return to the main menu...")  # Wait for user input

def display_menu():
    print("Menu:")
    print("1. Bleach Mode: Move data from a dirty drive.")
    print("2. Wash: Scan Bleached Drive with ClamAV")
    print("C. Configure Directories")
    print("I. Install Prerequisites")
    print("Q. Quit Script")

def convert_bytes(bytes):
    if bytes < 1024:
        return f"{bytes} bytes"
    elif bytes < 1024**2:
        return f"{bytes / 1024} KB"
    elif bytes < 1024**3:
        return f"{bytes / 1024**2} MB"
    else:
        return f"{bytes / 1024**3} GB"

def convert_seconds(sec):
    days = sec // 86400
    hours = (sec // 3600) % 24
    minutes = (sec // 60) % 60
    seconds = sec % 60
    return f"{days} days, {hours:02}:{minutes:02}:{seconds:02}"

def main():
    # Play start sound
    play_start_sound()

    # Load configuration
    if not os.path.exists(script_dir / 'config.ini'):
        # Create default configuration
        config = configparser.ConfigParser()
        config['Directories'] = {'SourceDirectory': '/media/cleaner/Windows/Users', 'DestinationDirectory': '/media/cleaner/Passport'}
        with open(script_dir / 'config.ini', 'w') as configfile:
            config.write(configfile)

    while True:
        # Clear the screen
        subprocess.run("clear", shell=True)

        # Dark orange color code
        dark_orange = "\033[38;5;202m"
        reset_color = "\033[0m"

        # Banner with ASCII art centered and bordered
        banner_text = f"""\
    {dark_orange}+{'-' * 84}+{reset_color}
    {dark_orange}|{reset_color}{' ' * 84}{dark_orange}|{reset_color}
    {dark_orange}|{reset_color}{' ' * 84}{dark_orange}|{reset_color}
    {dark_orange}|{'██╗     ██╗██╗  ██╗██╗██╗     '.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{'██║     ██║╚██╗██╔╝██║██║     '.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{'██║     ██║ ╚███╔╝ ██║██║     '.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{'██║     ██║ ██╔██╗ ██║██║     '.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{'███████╗██║██╔╝ ██╗██║███████╗'.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{'╚══════╝╚═╝╚═╝  ╚═╝╚═╝╚══════╝'.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{reset_color}{'Drive Sanitizer Script'.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{reset_color}{'Created by Samuel Presgraves, Security Engineer'.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{reset_color}{'LIXIL HQ, Digital Group, Security & IAM Team'.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{reset_color}{'Version 1.1, Feb 2024'.center(84)}{dark_orange}|{reset_color}
    {dark_orange}+{'-' * 84}+{reset_color}
        """

        # Print centered banner
        print(banner_text)

        # Display menu
        display_menu()

        choice = input("Enter your choice (1/2/C/I/Q): ").upper()
        if choice == '1':
            bleach_mode()
        elif choice == '2':
            wash_drive()
        elif choice == 'C':
            configure_directories()
        elif choice == 'I':
            install_prerequisites()
        elif choice == 'Q':
            print("Quitting script...")
            exit()
        else:
            print("Invalid choice. Please enter 1, 2, C, I, or Q.")

if __name__ == "__main__":
    main()
