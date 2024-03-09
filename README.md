# CSIRT Laundry Services

This utility script provides various functions to clean, sanitize, and manage data on recovered and infected drives. It's particularly useful for maintaining the cleanliness and security of data stored on drives.

## Features

- **Bleach Mode:** Moves data from a dirty drive to a specified destination directory, while also deleting prohibited files and directories.
- **Pre-soak:** Deletes prohibited files from the destination directory.
- **Wash:** Scans the bleached drive with ClamAV antivirus.
- **Dry:** Write-protects destination folders.
- **Fold:** Uploads data to Google Drive.
- **Tidy Up:** Compresses destination folders and deletes the original folders.

## Installation

1. Clone the repository to your local machine.
2. Ensure you have Python 3.x installed.
3. Install the required dependencies:

   ### Debian-based Systems (Debian, Ubuntu)
   ```bash
   sudo apt update
   sudo apt install clamav p7zip python3 python3-pip python3-tk -y
   ```
   ### Arch-based Systems (Arch Linux, Manjaro)
   ```bash
   sudo pacman -Syu clamav p7zip python python-pip tk --noconfirm
   ```
   ### RHEL-based Systems (CentOS, Fedora)
   ```bash
   sudo yum update
   sudo yum install epel-release -y
   sudo yum install clamav p7zip python3 python3-pip tkinter -y
   ```

### Apple macOS
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   brew install clamav p7zip python3
   ```

4. Configure the script by editing the `sample.config.ini` file in the `cfg` directory.
   Save the file as `config.ini` once complete.

## Usage

1. Run the script by executing `./csirt`.
2. Follow the on-screen menu to choose the desired operation.
3. Enter the necessary inputs when prompted.
4. View the logs in the `log` directory for detailed information about each operation.

## Configuration

The `config.ini` file in the `cfg` directory allows you to configure the following settings:

- Source directory: The directory from which data will be copied.
- Destination directory: The directory where data will be moved or uploaded.
- Google Drive folder ID: The ID for the folder in Google Drive you want to upload to.

The `extensions.list`, `prohibited.files`, and `prohibited.dirs` files can also be configured and tailored as necessary based on your own findings, policies, or preferences.

## Requirements

- Python 3.x
- Python Tkinter
- Pip
- 7-Zip
- ClamAV
- Dependencies listed in `requirements.txt`

## Credits

This script was created by Captain ASIC.

## Version History

- 1.0: Initial release (Feb 2024)
- 1.1: Added pre-soak function (Feb 2024)
- 1.2: Added dry function (Feb 2024)
- 1.3: Added fold function (Feb 2024)
- 1.4: Added tidy up function (Feb 2024)
- 1.5: Improved error handling and logging (Feb 2024)
- 1.6: Added configuration option and prerequisites installation (Mar 2024)
- 2.0.0: Started GUI Project and optimized CLI version (Mar 2024)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
