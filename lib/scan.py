import subprocess
import configparser
from threading import Thread

class WiFiScanner:
    def __init__(self, update_dropdown_callback):
        self.scan_process = None  # Reference to the scanning subprocess
        self.update_dropdown_callback = update_dropdown_callback
        self.is_scanning = False

        # Load interface from config.ini
        self.config = configparser.ConfigParser()
        self.config.read('cfg/config.ini')
        self.interface = self.config.get('WiFi', 'Interface', fallback='wlan0')

    def start_scan(self):
        if self.is_scanning:
            print("Scan is already running.")
            return

        self.is_scanning = True

        # Adjusted command to use interface from config and write output to log
        cmd = ["sudo", "airodump-ng", self.interface, "-w", "log/scan_results", "--output-format", "csv"]

        try:
            self.scan_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)
            # Process the scan output in a separate thread
            Thread(target=self.process_scan_output, daemon=True).start()
            print("Scanning started...")
        except Exception as e:
            print(f"Failed to start scan: {str(e)}")
            self.is_scanning = False

    def stop_scan(self):
        if self.scan_process:
            self.scan_process.terminate()
            self.scan_process = None
            self.is_scanning = False
            print("Scanning stopped.")
            # Optional: Callback to update UI after stopping the scan
            self.update_dropdown_callback()

    def process_scan_output(self):
        # This method should handle real-time output processing, if necessary
        # For example, parse the airodump-ng CSV files to extract SSID information
        pass
