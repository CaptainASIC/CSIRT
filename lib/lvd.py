import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from PIL import Image, ImageTk
from tkinter.font import Font
import configparser
import csv
import os
from datetime import datetime

class LogVoodooPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read('cfg/config.ini')

        # Setting up the background
        self.canvas = tk.Canvas(self, width=1280, height=800)
        self.canvas.pack(fill="both", expand=True)
        image_path = "img/lvd.png"  # Placeholder image path
        self.bg_image = ImageTk.PhotoImage(Image.open(image_path).resize((1280, 800), Image.Resampling.LANCZOS))
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)

        # Add legend text
        self.add_legend_text()

        # Setup "Pattern Counter" button
        self.setup_pattern_counter_button()

        # Placement for "Configure", "Back", and "Exit" buttons
        self.setup_control_buttons()

    def add_legend_text(self):
        # Adding legend text
        legend_text = "What do you want the Witch Doctor to Do?"
        text_bg = self.canvas.create_rectangle(100, 110, 1180, 150, fill='black', outline='black')
        self.canvas.create_text(640, 110, text=legend_text, font=Font(family="Helvetica", size=30, weight="bold"), fill="magenta2")

    def setup_pattern_counter_button(self):
        button_font = Font(family="Helvetica", size=16)  # Adjust font size to fit the button
        button_dimensions = {'width': 18, 'height': 2}  # Adjusted for text units, not pixels
        button = tk.Button(self, text="Pattern Counter", font=button_font, bg='steelblue4', fg='white', command=self.open_pattern_counter_window, **button_dimensions)
        self.canvas.create_window(640, 400, window=button)

    def open_pattern_counter_window(self):
        # Create a new window for pattern counter
        self.pattern_counter_window = tk.Toplevel(self)
        self.pattern_counter_window.title("Pattern Counter")

        # Pattern file entry
        tk.Label(self.pattern_counter_window, text="Pattern File:").grid(row=0, column=0, padx=10, pady=10)
        self.pattern_file_entry = tk.Entry(self.pattern_counter_window)
        self.pattern_file_entry.grid(row=0, column=1, padx=10, pady=10)
        self.pattern_file_entry.insert(0, "patterns.txt")

        # Log directory entry
        tk.Label(self.pattern_counter_window, text="Log Directory:").grid(row=1, column=0, padx=10, pady=10)
        self.log_dir_entry = tk.Entry(self.pattern_counter_window)
        self.log_dir_entry.grid(row=1, column=1, padx=10, pady=10)

        # Count button
        count_button = tk.Button(self.pattern_counter_window, text="Count", command=self.count_patterns)
        count_button.grid(row=2, columnspan=2, pady=10)

    def count_patterns(self):
        pattern_file = self.pattern_file_entry.get()
        log_dir = self.log_dir_entry.get()
        if not os.path.isfile(pattern_file) or not os.path.isdir(log_dir):
            messagebox.showerror("Error", "Invalid pattern file or log directory.")
            return

        # Read patterns
        with open(pattern_file, 'r') as f:
            patterns = [line.strip() for line in f]

        results = {pattern: {} for pattern in patterns}
        total_matches = 0

        # Process log files
        for root, _, files in os.walk(log_dir):
            for file in files:
                if file.endswith(".log"):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        for line in f:
                            date_str = line[:10]  # Assuming the date is in the first 10 characters
                            try:
                                date = datetime.strptime(date_str, "%Y-%m-%d")
                            except ValueError:
                                continue

                            for pattern in patterns:
                                if pattern in line:
                                    if date not in results[pattern]:
                                        results[pattern][date] = 0
                                    results[pattern][date] += 1
                                    total_matches += 1

        # Write results to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"outputs/voodoo_{timestamp}.csv"
        os.makedirs("outputs", exist_ok=True)
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['Pattern', 'Date', 'Count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for pattern, dates in results.items():
                for date, count in dates.items():
                    writer.writerow({'Pattern': pattern, 'Date': date.strftime("%Y-%m-%d"), 'Count': count})
            writer.writerow({'Pattern': 'Total', 'Date': '', 'Count': total_matches})

        messagebox.showinfo("Success", f"Pattern count completed. Results saved to {output_file}")

    def setup_control_buttons(self):
        text_font = Font(family="Helvetica", size=16)
        # "Back" button
        back_btn = tk.Button(self, text="← Back", font=text_font, bg='steelblue4', fg='white', command=lambda: self.controller.show_frame("StartPage"))
        self.canvas.create_window(120, 760, window=back_btn)

        # "Exit" button
        exit_btn = tk.Button(self, text="Exit", font=text_font, bg='steelblue4', fg='white', command=self.controller.quit)
        self.canvas.create_window(1160, 760, window=exit_btn)

        # "Configure" button
        configure_btn = tk.Button(self, text="Configure", font=text_font, bg='steelblue4', fg='white', command=self.configure_service)
        self.canvas.create_window(640, 700, window=configure_btn)  # Adjusted position

    def configure_service(self):
        # Placeholder for configure service logic
        messagebox.showinfo("Configure", "Configuration window would appear here.")

# Main application setup for testing purposes
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Log Voodoo")
    LogVoodooPage(root, None).pack(fill="both", expand=True)
    root.mainloop()
