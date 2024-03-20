# CSIRT Toolbox

The CSIRT Toolbox is a comprehensive suite of tools designed for Computer Security Incident Response Teams (CSIRTs) to aid in the clean-up, analysis, and management of data on recovered and infected drives, as well as network monitoring and analysis.

## Tools

### Laundry Services
Provides various functions to clean, sanitize, and manage data on drives.

- **Bleach Mode:** Moves data from a dirty drive to a specified destination directory, while also deleting prohibited files and directories.
- **Pre-soak:** Deletes prohibited files from the destination directory.
- **Wash:** Scans the bleached drive with ClamAV antivirus.
- **Dry:** Write-protects destination folders.
- **Fold:** Uploads data to Google Drive.
- **Tidy Up:** Compresses destination folders and deletes the original folders.

### Wifi Shark
A network monitoring and analysis tool for observing data flows and detecting anomalies in network traffic.

## Installation

1. Clone the repository to your local machine.
2. Ensure you have Python 3.x installed.
3. Install the required dependencies:

   ### Debian-based Systems (Debian, Ubuntu)
   ```bash
   sudo apt update
   sudo apt install clamav p7zip python3 python3-pip python3-tk policykit-1 -y
   ```
   ### Arch-based Systems (Arch Linux, Manjaro)
   ```bash
   sudo pacman -Syu clamav p7zip python python-pip tk polkit --noconfirm
   ```
   ### RHEL-based Systems (CentOS, Fedora)
   ```bash
   sudo yum update
   sudo yum install epel-release -y
   sudo yum install clamav p7zip python3 python3-pip tkinter polkit -y
   ```

### Apple macOS (may not work)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   brew install clamav p7zip python3
   ```

4. Configure the script by editing the `sample.config.ini` file in the `cfg` directory.
   Save the file as `config.ini` once complete.

## Usage

1. Run the script by executing `./csirt` or `./csirt --cli` if you want to force CLI mode.
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
- GDrive
   - CLI will automatically Install this package when you call the "Tidy up" task.
   - GUI has an "Install G-Drive" option on the Configure Page.
- Dependencies listed in `requirements.txt`

## Credits

This script was created by Captain ASIC.
Other packages and repositories used:
- gdrive - https://github.com/glotlabs/gdrive
- ClamAV - https://github.com/Cisco-Talos/clamav
- 7-Zip - https://www.7-zip.org
- rsync - https://rsync.samba.org
- pygame - https://www.pygame.org


## Version History

- 1.0: Initial release (Feb 2024)
- 1.1: Added pre-soak function (Feb 2024)
- 1.2: Added dry function (Feb 2024)
- 1.3: Added fold function (Feb 2024)
- 1.4: Added tidy up function (Feb 2024)
- 1.5: Improved error handling and logging (Feb 2024)
- 1.6: Added configuration option and prerequisites installation (Mar 2024)
- 2.0.0: Started GUI Project and optimized CLI version (Mar 2024)
- 2.0.4: All tasks should be functional in the GUI. (Mar 2024)
- 2.0.5: Tested operational, also added G-Drive installation to the GUI. (Mar 2024)
- 3.0.0: Adds Wifi Shark to the GUI (Apr 2024)


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
