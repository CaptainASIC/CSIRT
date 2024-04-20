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
import sys
from functions import compress_with_7zip, configure_directories, finish_task, play_start_sound, delete_prohibited_items, convert_seconds, APP_VERSION, BUILD_DATE, get_directory_size, convert_bytes
from tkinter import messagebox

# Get the directory where the script is located
script_dir = Path(__file__).resolve().parent

# Initialize pygame audio mixer
pygame.mixer.init()


def bleach_mode(destination_name, source_dir, destination_dir, callback=None):
    if not destination_name:
        return "Error: Destination directory name is required."
    
    full_destination_dir = f'{destination_dir}/{destination_name}'
    log_filename = f"bleach_{destination_name.lower().replace(' ', '_')}.log"
    log_path = script_dir / "../log" / log_filename
    
    with open(log_path, "w") as log_file:
        start_time = time.time()

        extensions_file = script_dir / "../cfg/extensions.list"
        with open(extensions_file) as f:
            extensions = [f'--include={line.strip()}' for line in f]

        rsync_command = f'rsync -av --stats {" ".join(extensions)} --exclude="*.*" --exclude="/administrator/" --exclude="/Default/" --exclude="/Public/" {source_dir} {full_destination_dir}'
        subprocess.run(rsync_command, shell=True, text=True, stdout=log_file, stderr=subprocess.STDOUT)

        delete_prohibited_items(full_destination_dir, "cfg/prohibited.files", "cfg/prohibited.dirs", log_file)

        end_time = time.time()
        elapsed_time = end_time - start_time

        finish_message = f"File copy and cleanup completed.\nTotal time taken: {convert_seconds(int(elapsed_time))}"

        # Check if a callback function is provided for GUI use
        if callback and callable(callback):
            callback(finish_message)
        else:
            return finish_message

def run_bleach_mode_cli():
    config = configparser.ConfigParser()
    config.read(script_dir / '../cfg/config.ini')
    source_dir = config.get('Directories', 'SourceDirectory', fallback='/dev/null')
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/dev/null')
    
    destination_name = input("Enter the User's Real Name as Last.First: ")
    if destination_name:
        result_message = bleach_mode(destination_name, source_dir, destination_dir)
        print(result_message)
    else:
        print("Operation canceled, destination name was not provided.")


def pre_soak(config, callback=None):
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/dev/null')
    
    current_datetime = datetime.datetime.now()
    log_filename = f"pre-soak_{current_datetime.strftime('%Y-%m-%d-%H-%M-%S')}.log"
    log_path = script_dir / "../log" / log_filename
    
    with open(log_path, "w") as log_file:
        log_file.write(f"Pre-soak process started at {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Enhanced directory matching and logging
        delete_prohibited_items(destination_dir, "cfg/prohibited.files", "cfg/prohibited.dirs", log_file)
        
        # Delete symbolic link files before uploading
        print("Deleting symbolic link files...")
        for root, dirs, files in os.walk(destination_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.islink(file_path) or stat.S_ISFIFO(os.stat(file_path).st_mode):
                    log_file.write(f"Deleted File: {file_path}\n")
                    os.unlink(file_path)

        log_file.write(f"Pre-soak process completed.\n")
    
    # Play finish sound and wait for user input
    finish_message = f"Pre-soak completed successfully."

    if callback and callable(callback):
        callback(finish_message)
    else:
        return finish_message

def can_use_pkexec():
    # Simple check for graphical session; may need adjustment for accuracy
    return "DISPLAY" in os.environ or "WAYLAND_DISPLAY" in os.environ

def run_command_with_privileges(command):
    if can_use_pkexec():
        run_command = ["pkexec"] + command
    else:
        run_command = ["sudo"] + command
    
    try:
        subprocess.run(run_command, check=True)
        print(f"Command executed successfully: {' '.join(command)}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to execute command: {' '.join(command)}")

def wash_drive(config, callback=None):
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/dev/null')
    
    # Commands requiring elevated privileges
    commands = [
        ["service", "clamav-freshclam", "stop"], # Stop clamav-freshclam service
        ["freshclam"], # Update ClamAV signatures
        ["service", "clamav-freshclam", "start"] # Start clamav-freshclam service
    ]
    
    for command in commands:
        run_command_with_privileges(command)
    
    # Run ClamAV scan on the specified folder and its subfolders
    print("Running ClamAV scan on the folder and its subfolders...")
    try:
        subprocess.run(["clamscan", "-r", destination_dir], check=True)
        print("ClamAV scan completed successfully.")
    except subprocess.CalledProcessError:
        print("ClamAV scan failed.")
        return
    
    # Play finish sound and wait for user input
    finish_message = f"Wash cycle completed."

    if callback and callable(callback):
        callback(finish_message)
    else:
        return finish_message

def dry(config, callback=None):
    # Read current configuration
    config = configparser.ConfigParser()
    config.read(script_dir / '../cfg/config.ini')
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/dev/null')
    print("Making Drive Read-Only.")
    for root, dirs, files in os.walk(destination_dir):
        for d in dirs:
            d_path = os.path.join(root, d)
            os.chmod(d_path, 0o555)  # Make the directory read-only
    
    # Play finish sound and wait for user input
    finish_message = f"Drying cycle completed."

    if callback and callable(callback):
        callback(finish_message)
    else:
        return finish_message


def upload_to_cloud(config, log_path, is_gui=False, callback=None):
    # Retrieve remote drive name and folder path from the configuration
    remote_name = config.get('RemoteDrive', 'RemoteName')
    base_remote_path = config.get('RemoteDrive', 'BasePath', fallback='')

    # Open log file to append
    with open(log_path, "a") as log_file:
        # Get a list of folders in the local destination directory
        destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/dev/null')
        folders = [folder for folder in os.listdir(destination_dir) if os.path.isdir(os.path.join(destination_dir, folder))]

        for folder in folders:
            folder_path = os.path.join(destination_dir, folder)
            remote_folder_path = os.path.join(base_remote_path, folder) if base_remote_path else folder

            if is_gui:
                # Use dialog box for GUI
                user_decision = messagebox.askyesno("Confirm Upload", f"Do you want to upload \"{folder}\" to Drive?")
            else:
                # Use CLI input
                user_decision = input(f"Do you want to upload \"{folder}\" to Drive? (y/n): ").lower() == 'y'
            
            if user_decision:
                rclone_command = f"rclone copy \"{folder_path}\" \"{remote_name}:{remote_folder_path}\""
                try:
                    result = subprocess.run(rclone_command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    log_file.write(f"Upload successful for {folder_path}\n")
                    log_file.write(result.stdout + "\n")
                    if is_gui:
                        # Log success with GUI message
                        messagebox.showinfo("Upload Successful", f"Upload successful for {folder_path}")
                    else:
                        # Log success in CLI
                        print(f"Upload successful for {folder_path}")
                except subprocess.CalledProcessError as e:
                    log_file.write(f"Error uploading {folder_path}: {e.stderr}\n")
                    if is_gui:
                        messagebox.showerror("Error", f"Error uploading {folder_path}: {e.stderr}")
                    else:
                        print(f"Error uploading {folder_path}: {e.stderr}")
                        input("Press Enter to continue...") 
    if callback:
        callback("Upload process has been completed.")

# Function to generate log paths could also be here or imported if defined elsewhere
def generate_log_path(service_name):
    current_datetime = datetime.datetime.now()
    log_filename = f"{service_name}_{current_datetime.strftime('%Y-%m-%d-%H-%M-%S')}.log"
    return Path(script_dir) / "../log" / log_filename


def tidy_up(config, log_file, is_gui=False, callback=None):
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/dev/null')
    
    with open(log_file, "w") as log_file:
        # Record initial destination size
        initial_destination_size = get_directory_size(destination_dir)
        log_file.write(f"Destination size at start: " + convert_bytes(initial_destination_size) + "\n")

        # Iterate through directories for tidying
        dirs = [d for d in os.listdir(destination_dir) if os.path.isdir(os.path.join(destination_dir, d))]
        for d in dirs:
            folder_path = os.path.join(destination_dir, d)
            
            # Decide on action based on the interface mode
            if is_gui:
                user_decision = messagebox.askyesno("Confirm", f"Do you want to tidy up \"{d}\"?")
            else:
                print("\nFolder:", folder_path)
                user_decision = input(f"Do you want to tidy up \"{d}\"? (y/n): ").lower() == 'y'

            if user_decision:
                folder_size = get_directory_size(folder_path)
                archive_name = f"{d}.csirt"
                archive_path = os.path.join(destination_dir, archive_name)
                
                compress_with_7zip(folder_path, archive_path)
                
                # Log the operation
                archive_size = os.path.getsize(archive_path)
                log_file.write(f"Compressed \"{d}\" into \"{archive_name}\". Size: {convert_bytes(archive_size)}\n")
                
                shutil.rmtree(folder_path)
                log_file.write(f"Deleted original folder: {folder_path}\n")
                
        final_destination_size = get_directory_size(destination_dir)
        log_file.write("Final destination size: " + convert_bytes(final_destination_size) + "\n")

    # Play finish sound and wait for user input
    finish_message = f"Tidying up completed successfully."

    if callback and callable(callback):
        callback(finish_message)
    else:
        return finish_message


def display_menu():
    print("Menu:")
    print("1. Bleach Mode: Move data from a dirty drive")
    print("2. Pre-soak: Delete Prohibited Files")
    print("3. Wash: Scan Bleached Drive with ClamAV")
    print("4. Dry: Write Protect Destination Folders")
    print("5. Fold: Upload to Cloud Storage")
    print("6. Tidy up: Compress Destination Folders")
    print("C. Configure Directories")
    print("Q. Quit Script")

def main():
    # Play start sound
    play_start_sound()

    # Load configuration
    if not os.path.exists(script_dir / '../cfg/config.ini'):
        # Create default configuration
        config = configparser.ConfigParser()
        config['Directories'] = {'SourceDirectory': '/dev/null', 'DestinationDirectory': '/dev/null'}
        with open(script_dir / '../cfg/config.ini', 'w') as configfile:
            config.write(configfile)
    else:
        config = configparser.ConfigParser()
        config.read(script_dir / '../cfg/config.ini')

    # Fetch source directory from config
    source_dir = config.get('Directories', 'SourceDirectory', fallback='/dev/null')
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/dev/null')

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
    {dark_orange}|{' ██████╗███████╗██╗██████╗ ████████╗'.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{'██╔════╝██╔════╝██║██╔══██╗╚══██╔══╝'.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{'██║     ███████╗██║██████╔╝   ██║   '.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{'██║     ╚════██║██║██╔══██╗   ██║   '.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{'╚██████╗███████║██║██║  ██║   ██║   '.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{' ╚═════╝╚══════╝╚═╝╚═╝  ╚═╝   ╚═╝   '.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{reset_color}{' ' * 84}{dark_orange}|{reset_color}
    {dark_orange}|{'██╗      █████╗ ██╗   ██╗███╗   ██╗██████╗ ██████╗ ██╗   ██╗'.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{'██║     ██╔══██╗██║   ██║████╗  ██║██╔══██╗██╔══██╗╚██╗ ██╔╝'.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{'██║     ███████║██║   ██║██╔██╗ ██║██║  ██║██████╔╝ ╚████╔╝ '.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{'██║     ██╔══██║██║   ██║██║╚██╗██║██║  ██║██╔══██╗  ╚██╔╝  '.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{'███████╗██║  ██║╚██████╔╝██║ ╚████║██████╔╝██║  ██║   ██║   '.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{'╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝   ╚═╝   '.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{reset_color}{' ' * 84}{dark_orange}|{reset_color}
    {dark_orange}|{reset_color}{' ' * 84}{dark_orange}|{reset_color}
    {dark_orange}|{reset_color}{'Created by Captain ASIC'.center(84)}{dark_orange}|{reset_color}
    {dark_orange}|{reset_color}{f'Version {APP_VERSION}, {BUILD_DATE}'.center(84)}{dark_orange}|{reset_color}
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

        choice = input("Enter your choice (1-6, C, or Q): ").upper()
        if choice == '1':
            run_bleach_mode_cli()
        elif choice == '2':
            pre_soak(config)  # Pass config object to pre_soak function
        elif choice == '3':
            wash_drive(config) # Pass config object to wash function
        elif choice == '4':
            dry(config)  # Pass config object to dry function
        elif choice == '5':
            log_path = generate_log_path("fold")
            upload_to_cloud(config, log_path, is_gui=False, callback=None)
        elif choice == '6':
            log_path = generate_log_path("tidy")
            tidy_up(config, log_path, is_gui=False, callback=None)
        elif choice == 'C':
            configure_directories()
        elif choice == 'Q':
            print("Quitting script...")
            exit()
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, 6, C, or Q.")

if __name__ == "__main__":
    main()
