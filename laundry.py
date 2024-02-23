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
    # Read configuration
    config = configparser.ConfigParser()
    config.read(script_dir / 'config.ini')
    source_dir = config.get('Directories', 'SourceDirectory', fallback='/media/cleaner/Windows/Users')
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/media/cleaner/Passport')

    # Construct the full destination directory path
    destination_name = input("Enter the User's Real Name as Last.First: ")
    if not destination_name:
        print("Error: Destination directory name is required.")
        return

    destination_dir = f'{destination_dir}/{destination_name}'
    print("Destination directory:", destination_dir)

    # Use destination_name as the log filename
    log_filename = f"bleach_{destination_name.lower().replace(' ', '_')}.log"

    # Create the log file
    log_path = script_dir / "log" / log_filename
    log_file = open(log_path, "w")

    # Record start time
    start_time = time.time()
    print("Starting file copy...")

    # Read extensions from the reference file
    extensions_file = script_dir / "extensions.list"
    with open(extensions_file) as f:
        extensions = [f'"--include={line.strip()}"' for line in f]

    # Perform the file copy using rsync
    rsync_command = f'rsync -av --stats {" ".join(extensions)} --exclude="*.*" --exclude="desktop.ini" --exclude="/administrator/" --exclude="/Default/" --exclude="/Public/" {source_dir}/ {destination_dir}'
    #debug# print("Rsync command:", rsync_command)
    rsync_result = subprocess.run(rsync_command, shell=True, text=True, stdout=log_file, stderr=subprocess.STDOUT)
    #print("Rsync output:", rsync_result.stdout)

    print("File copy completed.")

    # Delete prohibited files
    delete_prohibited_files(destination_dir , "prohibited.list")

    # Clean up empty directories in the destination directory
    #clean_empty_directories(destination_dir)

    # Calculate elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Output the elapsed time
    print("Total time taken:", convert_seconds(int(elapsed_time)))

    # Write total time taken to the log file
    log_file.write(f"\nTotal time taken: {convert_seconds(int(elapsed_time))}")

    # Close the log file
    log_file.close()

    # Finish
    midi_file = script_dir / "snd/ffvii.mp3"
    pygame.mixer.music.load(str(midi_file))
    pygame.mixer.music.play()
    input("Press Enter to return to the main menu...")  # Wait for user input

def pre_soak(config):
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/media/cleaner/Passport')
    # Delete prohibited files
    delete_prohibited_files(destination_dir , "prohibited.list")

    # Clean up empty directories in the destination directory
   # clean_empty_directories(destination_dir)
    # Finish
    midi_file = script_dir / "snd/ffvii.mp3"
    pygame.mixer.music.load(str(midi_file))
    pygame.mixer.music.play()
    print("Pre-soak completed.")
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

def download_and_install_gdrive():
    # Define paths
    download_url = "https://github.com/glotlabs/gdrive/releases/download/3.9.1/gdrive_linux-x64.tar.gz"
    download_path = "/tmp/gdrive.tar.gz"
    extract_dir = "/tmp/gdrive"

    # Check if gdrive already exists in /usr/local/bin
    if os.path.exists("/usr/local/bin/gdrive"):
        print("gdrive is already installed.")
        return

    # Download gdrive
    print("Downloading gdrive...")
    urllib.request.urlretrieve(download_url, download_path)

    # Extract gdrive
    print("Extracting gdrive...")
    with tarfile.open(download_path, "r:gz") as tar:
        tar.extractall(path=extract_dir)

    # Move gdrive to /usr/local/bin using sudo
    print("Moving gdrive to /usr/local/bin...")
    subprocess.run(["sudo", "mv", os.path.join(extract_dir, "gdrive"), "/usr/local/bin"])

    # Change permissions using sudo
    print("Changing permissions...")
    subprocess.run(["sudo", "chmod", "755", "/usr/local/bin/gdrive"])

    # Clean up
    print("Cleaning up...")
    os.remove(download_path)
    shutil.rmtree(extract_dir)

    # Verify installation
    print("Verifying installation...")
    subprocess.run(["gdrive", "account", "add"])

    print("gdrive installed successfully.")

# Function to install prerequisites
def install_prerequisites():
    print("Installing prerequisites...")
    download_and_install_gdrive()
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

def dry(config):
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/media/cleaner/Passport')
    for root, dirs, files in os.walk(destination_dir):
        for d in dirs:
            d_path = os.path.join(root, d)
            os.chmod(d_path, 0o555)  # Make the directory read-only


def upload_to_gdrive():
    # Get the current date and time for the log filename
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/media/cleaner/Passport')
    current_datetime = datetime.datetime.now()
    log_filename = current_datetime.strftime("%Y-%m-%d-%H-%M-%S") + ".log"
    log_path = script_dir / "log" / log_filename

    # Construct the gdrive command
    gdrive_command = f"gdrive files upload --recursive {destination_dir}/TESTING"

    # Run the gdrive command and write the output to the log file
    print("Uploading to Google Drive...")
    with open(log_path, "w") as log_file:
        subprocess.run(shlex.split(gdrive_command), stdout=log_file, stderr=subprocess.STDOUT)

    print("Upload to Google Drive completed.")
    
    # Finish
    midi_file = script_dir / "snd/ffvii.mp3"
    pygame.mixer.music.load(str(midi_file))
    pygame.mixer.music.play()
    input("Press Enter to return to the main menu...")  # Wait for user input

def display_menu():
    print("Menu:")
    print("1. Bleach Mode: Move data from a dirty drive")
    print("2. Pre-soak: Delete Prohibited Files")
    print("3. Wash: Scan Bleached Drive with ClamAV")
    print("4. Dry: Write Protect Destination Folders")
    print("5. Fold: Upload to GDrive")
    print("6. Tidy up: Compress Destination Folders. (Run After Folding) NOT YET IMPLEMENTED")
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

def delete_prohibited_files(destination_dir, prohibited_file):
    # Delete prohibited files recursively
    print("Deleting prohibited files...")
    num_deleted_files = 0
    for root, dirs, files in os.walk(destination_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file_in_prohibited_list(file_path, prohibited_file):
                #debug#print(f"Deleting: {file_path}")
                os.remove(file_path)
                num_deleted_files += 1

    # Delete empty directories recursively
#    print("Cleaning up empty directories...")
#    num_deleted_dirs = 0
#    for root, dirs, files in os.walk(destination_dir, topdown=False):
#        for dir in dirs:
#            dir_path = os.path.join(root, dir)
#            if not os.listdir(dir_path):
                #debug#print(f"Deleting empty directory: {dir_path}")
#                try:
#                    os.rmdir(dir_path)
#                    num_deleted_dirs += 1
#                except NotADirectoryError:
#                    print(f"Error: {dir_path} is not a directory.")

#    print(f"Number of files deleted: {num_deleted_files}")
#    print(f"Number of empty directories deleted: {num_deleted_dirs}")

def file_in_prohibited_list(file_path, prohibited_file):
    with open(prohibited_file) as f:
        for pattern in f:
            pattern = pattern.strip()
            if pattern and fnmatch.fnmatch(os.path.basename(file_path), pattern):
                return True
    return False


#def clean_empty_directories(destination_dir):
    # Clean up empty directories in the destination directory
#    print(f"Cleaning up empty directories in {destination_dir}...")
#    subprocess.run(["find", destination_dir, "-empty", "-type", "d", "-delete"])

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
    else:
        config = configparser.ConfigParser()
        config.read(script_dir / 'config.ini')

    # Fetch source directory from config
    source_dir = config.get('Directories', 'SourceDirectory', fallback='/media/cleaner/Windows/Users')
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/media/cleaner/Passport')

    while True:
        # Clear the screen
        subprocess.run("clear", shell=True)

        # Color codes
        dark_orange = "\033[38;5;202m"
        dark_red = "\033[38;5;160m"
        green = "\033[38;5;40m]"
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
    {dark_orange}|{reset_color}{' ' * 84}{dark_orange}|{reset_color}
    {dark_orange}|{reset_color}{' ' * 84}{dark_orange}|{reset_color}
    {dark_orange}|{reset_color}{'Drive Sanitizer Script'.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{reset_color}{'Created by Samuel Presgraves, Security Engineer'.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{reset_color}{'LIXIL HQ, Digital Group, Security & IAM Team'.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{reset_color}{'Version 1.3, Feb 2024'.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{reset_color}{' ' * 84}{dark_orange}|{reset_color}
    {dark_orange}+{'-' * 84}+{reset_color}
    \n
            {dark_red}+{'-' * 32}[{reset_color}+{reset_color}{green}{'-' * 32}+{reset_color}
            {dark_red}|{'Source Directory:'.ljust(32)}[{reset_color}|{reset_color}{green}{'Destination Directory:'.ljust(32)}|{reset_color}
            {dark_red}|{source_dir.ljust(32)}[{reset_color}|{reset_color}{green}{destination_dir.ljust(32)}|{reset_color}
            {dark_red}+{'-' * 32}[{reset_color}+{reset_color}{green}{'-' * 32}+{reset_color}

        """

        # Print centered banner
        print(banner_text)

        # Display menu
        display_menu()

        choice = input("Enter your choice (1/2/3/4/5/C/I/Q): ").upper()
        if choice == '1':
            bleach_mode()
        elif choice == '2':
            pre_soak(config)  # Pass config object to pre_soak function
        elif choice == '3':
            wash_drive()
        elif choice == '4':
            dry(config)  # Pass config object to dry function
        elif choice == '5':
            upload_to_gdrive()
        elif choice == 'C':
            configure_directories()
        elif choice == 'I':
            install_prerequisites()
        elif choice == 'Q':
            print("Quitting script...")
            exit()
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, C, I, or Q.")

if __name__ == "__main__":
    main()
