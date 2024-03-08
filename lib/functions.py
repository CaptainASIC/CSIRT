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

# Get the directory where the script is located
script_dir = Path(__file__).resolve().parent

# Initialize pygame audio mixer
pygame.mixer.init()

# Function to play start sound
def play_start_sound():
    sound_file = script_dir / "../snd/start.mp3"
    pygame.mixer.music.load(str(sound_file))
    pygame.mixer.music.play()

# Function to wash the drive
def bleach_mode():
    config = configparser.ConfigParser()
    config.read(script_dir / '../cfg/config.ini')
    source_dir = config.get('Directories', 'SourceDirectory', fallback='/dev/null')
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/dev/null')

    destination_name = input("Enter the User's Real Name as Last.First: ")
    if not destination_name:
        print("Error: Destination directory name is required.")
        return

    destination_dir = f'{destination_dir}/{destination_name}'
    print("Destination directory:", destination_dir)

    log_filename = f"bleach_{destination_name.lower().replace(' ', '_')}.log"
    log_path = script_dir / "log" / log_filename
    log_file = open(log_path, "w")

    start_time = time.time()
    print("Starting file copy...")

    extensions_file = script_dir / "../cfg/extensions.list"
    with open(extensions_file) as f:
        extensions = [f'"--include={line.strip()}"' for line in f]

    rsync_command = f'rsync -av --stats {" ".join(extensions)} --exclude="*.*" --exclude="/administrator/" --exclude="/Default/" --exclude="/Public/" {source_dir}/ {destination_dir}'
    subprocess.run(rsync_command, shell=True, text=True, stdout=log_file, stderr=subprocess.STDOUT)

    print("File copy completed.")

    # Call delete_prohibited_items with logging
    delete_prohibited_items(destination_dir, "../cfg/prohibited.files", "../cfg/prohibited.dirs", log_file)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Total time taken:", convert_seconds(int(elapsed_time)))
    log_file.write(f"\nTotal time taken: {convert_seconds(int(elapsed_time))}\n")

    log_file.close()

    # Play finish sound and wait for user input
    finish_task("File copy and cleanup completed.")

def pre_soak(config):
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/dev/null')
    
    current_datetime = datetime.datetime.now()
    log_filename = f"pre-soak_{current_datetime.strftime('%Y-%m-%d-%H-%M-%S')}.log"
    log_path = script_dir / "../log" / log_filename
    
    with open(log_path, "w") as log_file:
        log_file.write(f"Pre-soak process started at {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Enhanced directory matching and logging
        delete_prohibited_items(destination_dir, "../cfg/prohibited.files", "../cfg/prohibited.dirs", log_file)
        
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
    finish_task("Pre-soak completed.")

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
    
    # Play finish sound and wait for user input
    finish_task("Wash cycle completed.")

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

def dry(config):
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
    finish_task("Drying cycle completed.")


def upload_to_gdrive():
    # Read current configuration
    config = configparser.ConfigParser()
    config.read(script_dir / '../cfg/config.ini')

    # Get the current date and time for the log filename
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/dev/null')
    current_datetime = datetime.datetime.now()
    log_filename = "fold_" + current_datetime.strftime("%Y-%m-%d-%H-%M-%S") + ".log"
    log_path = script_dir / "../log" / log_filename

    # Open log file to append
    with open(log_path, "a") as log_file:
        # Get a list of folders in the destination directory
        folders = [folder for folder in os.listdir(destination_dir) if os.path.isdir(os.path.join(destination_dir, folder))]

        # Iterate over each folder and upload to Google Drive
        for folder in folders:
            folder_path = os.path.join(destination_dir, folder)
            # Ask the user for confirmation before uploading each folder
            user_decision = input(f"Do you want to upload \"{folder}\" to Google Drive? (y/n): ")
            if user_decision.lower() == 'y':
                # Construct the gdrive command for the current folder
                gdrive_command = f"gdrive files upload --recursive --parent 1kVostcz6mavBkCSxVF3ndKmp0m8jRBDn \"{folder_path}\""
                print(f"Uploading \"{folder}\" to Google Drive.")
                # Run the gdrive command and write the output to the log file
                try:
                    result = subprocess.run(gdrive_command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    # Log success
                    log_file.write(f"Upload successful for {folder_path}\n")
                    log_file.write(result.stdout + "\n")
                except subprocess.CalledProcessError as e:
                    # Log errors
                    log_file.write(f"Error uploading {folder_path}: {e.stderr}\n")
            else:
                print(f"Skipping \"{folder}\".")

        print("Upload to Google Drive completed.")
    
    # Play finish sound and wait for user input
    finish_task("Folding has been completed.")

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

def tidy_up():
    # Read current configuration
    config = configparser.ConfigParser()
    config.read(script_dir / '../cfg/config.ini')
    print("Collecting Statistics:")
    destination_dir = config.get('Directories', 'DestinationDirectory', fallback='/dev/null')
    current_datetime = datetime.datetime.now()
    log_filename = "tidy_" + current_datetime.strftime("%Y-%m-%d-%H-%M-%S") + ".log"
    log_path = script_dir / "../log" / log_filename

    with open(log_path, "w") as log_file:
        # Record initial destination size
        initial_destination_size = get_directory_size(destination_dir)
        log_file.write("Destination size at start: " + convert_bytes(initial_destination_size) + "\n")

        # List only top-level directories in the destination directory
        dirs = [d for d in os.listdir(destination_dir) if os.path.isdir(os.path.join(destination_dir, d))]

        for d in dirs:
            folder_path = os.path.join(destination_dir, d)
            print("\nFolder:", folder_path)

            user_decision = input(f"Do you want to tidy up \"{d}\"? (y/n): ")
            if user_decision.lower() == 'y':
                # Record folder size
                folder_size = get_directory_size(folder_path)
                print("Folder size:", convert_bytes(folder_size))

                # Compress folder into an archive, here using .csirt as requested
                archive_name = f"{d}.csirt"
                archive_path = os.path.join(destination_dir, archive_name)
                print("Compressing folder into archive:", archive_path)
                compress_with_7zip(folder_path, archive_path)
                
                # Record archive size
                archive_size = os.path.getsize(archive_path)
                log_file.write(f"Compressed \"{d}\" into \"{archive_name}\". Size: {convert_bytes(archive_size)}\n")

                # Delete the original folder
                shutil.rmtree(folder_path)
                print("Deleted original folder:", folder_path)
                log_file.write(f"Deleted original folder: {folder_path}\n")
            else:
                print(f"Skipping \"{d}\".")

        # Record final destination size
        final_destination_size = get_directory_size(destination_dir)
        log_file.write("Final destination size: " + convert_bytes(final_destination_size) + "\n")

    # Play finish sound and wait for user input
    finish_task("Everything is neat & Tidy.")

def get_directory_size(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def display_menu():
    print("Menu:")
    print("1. Bleach Mode: Move data from a dirty drive")
    print("2. Pre-soak: Delete Prohibited Files")
    print("3. Wash: Scan Bleached Drive with ClamAV")
    print("4. Dry: Write Protect Destination Folders")
    print("5. Fold: Upload to GDrive")
    print("6. Tidy up: Compress Destination Folders")
    print("C. Configure Directories")
    print("I. Install Prerequisites")
    print("Q. Quit Script")

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
    {dark_orange}|{reset_color}{'Version 2.0.0, Mar 2024'.center(84)}{dark_orange}|{reset_color}
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

        choice = input("Enter your choice (1-6, C, I, or Q): ").upper()
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
        elif choice == '6':
            tidy_up()
        elif choice == 'C':
            configure_directories()
        elif choice == 'Q':
            print("Quitting script...")
            exit()
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, 5, C, or Q.")

if __name__ == "__main__":
    main()
