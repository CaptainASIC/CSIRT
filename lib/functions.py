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

APP_VERSION = "2.0.5"
BUILD_DATE = "Mar 2024"

script_dir = Path(__file__).resolve().parent

# Function to play start sound
def play_start_sound():
    sound_file = script_dir / "../snd/start.mp3"
    pygame.mixer.music.load(str(sound_file))
    pygame.mixer.music.play()

def configure_directories():
    # Read current configuration
    config = configparser.ConfigParser()
    config.read(script_dir / '../cfg/config.ini')

    source_dir = config.get('Directories', 'SourceDirectory', fallback='/dev/null')
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/dev/null')

    print(f"Current source directory: {source_dir}")
    change_source_dir = input("Do you want to change the source directory? (y/n): ").lower()

    if change_source_dir == 'y':
        new_source_dir = input("Enter the new source directory: ")
        config.set('Directories', 'SourceDirectory', new_source_dir)
        with open(script_dir / '../cfg/config.ini', 'w') as configfile:
            config.write(configfile)
        print("Source directory updated successfully.")
    else:
        print("Keeping the current source directory.")

    print(f"Current destination directory: {destination_dir}")
    change_dest_dir = input("Do you want to change the destination directory? (y/n): ").lower()

    if change_dest_dir == 'y':
        new_dest_dir = input("Enter the new destination directory: ")
        config.set('Directories', 'DestinationDirectory', new_dest_dir)
        with open(script_dir / '../cfg/config.ini', 'w') as configfile:
            config.write(configfile)
        print("Destination directory updated successfully.")
    else:
        print("Keeping the current destination directory.")

    input("Press Enter to return to the main menu...")  # Wait for user input

def compress_with_7zip(source_folder, archive_path):
    try:
        # Construct the 7-Zip command. Adjust the path to 7z if necessary.
        cmd = ['7z', 'a', '-t7z', archive_path, source_folder, '-bsp1']

        # Run the command and capture output.
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, text=True, universal_newlines=True) as p:
            for line in p.stdout:
                if '%' in line:  # This is a naive check; adjust based on actual 7z output.
                    print(f"\r{line.strip()}", end='')  # Update progress in place.
            p.stdout.close()
            return_code = p.wait()
            if return_code != 0:
                print(f"7-Zip command failed with return code: {return_code}")
            else:
                print("\nCompression completed successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_directory_size(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def convert_bytes(bytes):
    """Convert bytes to a more readable format."""
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024

def convert_seconds(sec):
    days = sec // 86400
    hours = (sec // 3600) % 24
    minutes = (sec // 60) % 60
    seconds = sec % 60
    return f"{days} days, {hours:02}:{minutes:02}:{seconds:02}"

def delete_prohibited_items(destination_dir, prohibited_files_list, prohibited_dirs_list, log_file):
    print("Deleting prohibited directories and files...")
    num_deleted_files = 0
    num_deleted_dirs = 0

    with open(prohibited_files_list) as f:
        prohibited_file_patterns = [line.strip() for line in f if line.strip()]
    with open(prohibited_dirs_list) as f:
        prohibited_dir_patterns = [line.strip() for line in f if line.strip()]

    destination_dir_path = Path(destination_dir)

    for dir_path in destination_dir_path.rglob('*'):
        if dir_path.is_dir():
            relative_dir_path = dir_path.relative_to(destination_dir_path)
            for pattern in prohibited_dir_patterns:
                if fnmatch.fnmatch(str(relative_dir_path), pattern):
                    shutil.rmtree(dir_path, ignore_errors=True)
                    num_deleted_dirs += 1
                    log_message = f"Deleted directory: {dir_path}"
                    #print(log_message)
                    log_file.write(log_message + "\n")

    for file_path in destination_dir_path.rglob('*'):
        if file_path.is_file():
            for pattern in prohibited_file_patterns:
                if fnmatch.fnmatch(file_path.name, pattern):
                    file_path.unlink(missing_ok=True)
                    num_deleted_files += 1
                    log_message = f"Deleted file: {file_path}"
                    #print(log_message)
                    log_file.write(log_message + "\n")

    print(f"Number of directories deleted: {num_deleted_dirs}")
    print(f"Number of files deleted: {num_deleted_files}")
    log_file.write(f"Summary: {num_deleted_dirs} directories and {num_deleted_files} files deleted.\n")


def file_in_prohibited_list(file_path, prohibited_file):
    with open(prohibited_file) as f:
        for pattern in f:
            pattern = pattern.strip()
            if pattern and fnmatch.fnmatch(os.path.basename(file_path), pattern):
                return True
    return False

def finish_task(message):
    # Play finish sound
    pygame.mixer.music.load(str(script_dir / "../snd/ffvii.mp3"))
    pygame.mixer.music.play()

    # Print message
    print(message)

    # Wait for user input
    input("Press Enter to return to the main menu...")

def download_and_install_gdrive(callback=None):
    # Define paths
    download_url = "https://github.com/glotlabs/gdrive/releases/download/3.9.1/gdrive_linux-x64.tar.gz"
    download_path = "/tmp/gdrive.tar.gz"
    extract_dir = "/tmp/gdrive"

    # Check if gdrive already exists in /usr/local/bin
    if os.path.exists("/usr/local/bin/gdrive"):
        message = "gdrive is already installed."
        if callback: callback(message)
        else: print(message)
        return

    steps = [
        ("Downloading gdrive...", lambda: urllib.request.urlretrieve(download_url, download_path)),
        ("Extracting gdrive...", lambda: tarfile.open(download_path, "r:gz").extractall(path=extract_dir)),
        ("Moving gdrive to /usr/local/bin...", lambda: subprocess.run(["sudo", "mv", os.path.join(extract_dir, "gdrive"), "/usr/local/bin"])),
        ("Changing permissions...", lambda: subprocess.run(["sudo", "chmod", "755", "/usr/local/bin/gdrive"])),
        ("Cleaning up...", lambda: os.remove(download_path) or shutil.rmtree(extract_dir)),
        ("Verifying installation...", lambda: subprocess.run(["gdrive", "account", "add"]))
    ]

    for step_message, step_action in steps:
        if callback: callback(step_message)
        else: print(step_message)
        step_action()

    message = "gdrive installed successfully."
    if callback: callback(message)
    else: print(message)
