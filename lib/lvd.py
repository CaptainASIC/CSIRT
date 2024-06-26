import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, Toplevel, Label, Button
from PIL import Image, ImageTk
from tkinter.font import Font
import configparser
import csv
import os
from datetime import datetime
from collections import Counter

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
        text_bg = self.canvas.create_rectangle(100, 100, 1180, 150, fill='black', outline='black')
        self.canvas.create_text(640, 125, text=legend_text, font=Font(family="Helvetica", size=30, weight="bold"), fill="magenta2")

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
        self.pattern_file_entry.insert(0, self.config.get('Settings', 'patterns_file', fallback='patterns.txt'))
        tk.Button(self.pattern_counter_window, text="Browse", command=self.browse_pattern_file).grid(row=0, column=2, padx=10, pady=10)

        # Log directory entry
        tk.Label(self.pattern_counter_window, text="Log Directory:").grid(row=1, column=0, padx=10, pady=10)
        self.log_dir_entry = tk.Entry(self.pattern_counter_window)
        self.log_dir_entry.grid(row=1, column=1, padx=10, pady=10)
        self.log_dir_entry.insert(0, self.config.get('Settings', 'log_directory', fallback=''))
        tk.Button(self.pattern_counter_window, text="Browse", command=self.browse_log_directory).grid(row=1, column=2, padx=10, pady=10)

        # Count button
        count_button = tk.Button(self.pattern_counter_window, text="Count", command=self.count_patterns)
        count_button.grid(row=2, columnspan=3, pady=10)

        # Status label for feedback
        self.status_label = tk.Label(self.pattern_counter_window, text="")
        self.status_label.grid(row=3, columnspan=3, pady=10)

    def browse_pattern_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if filename:
            self.pattern_file_entry.delete(0, tk.END)
            self.pattern_file_entry.insert(0, filename)

    def browse_log_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.log_dir_entry.delete(0, tk.END)
            self.log_dir_entry.insert(0, directory)

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
        unique_patterns_matched = set()
        date_counter = Counter()
        source_counter = Counter()
        destination_counter = Counter()
        pattern_counter = Counter()

        # Process log files
        for root, _, files in os.walk(log_dir):
            for file in files:
                if file.endswith(".log"):
                    file_path = os.path.join(root, file)
                    self.status_label.config(text=f"Processing {file}...")
                    self.pattern_counter_window.update_idletasks()
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            self.process_log_file(f, patterns, results, date_counter, source_counter, destination_counter, pattern_counter, unique_patterns_matched)
                    except UnicodeDecodeError:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            self.process_log_file(f, patterns, results, date_counter, source_counter, destination_counter, pattern_counter, unique_patterns_matched)
                    self.status_label.config(text=f"Completed {file}")
                    self.pattern_counter_window.update_idletasks()

        # Write results to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"log/voodoo_{timestamp}.csv"
        os.makedirs("log", exist_ok=True)
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['Pattern', 'Date', 'Source IP', 'Destination IP', 'Count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for pattern, dates in results.items():
                for date, ips in dates.items():
                    for ip, count in ips.items():
                        writer.writerow({'Pattern': pattern, 'Date': date.strftime("%Y-%m-%d"), 'Source IP': ip[0], 'Destination IP': ip[1], 'Count': count})

        # Analyze the results
        total_pattern_matches = sum(pattern_counter.values())
        total_unique_pattern_matches = len(unique_patterns_matched)
        highest_match_date, highest_match_count = date_counter.most_common(1)[0]
        most_common_source, source_count = source_counter.most_common(1)[0]
        most_common_destination, destination_count = destination_counter.most_common(1)[0]
        most_common_pattern, pattern_match_count = pattern_counter.most_common(1)[0]

        self.status_label.config(text="Pattern count completed.")
        self.show_success_dialog(
            output_file,
            total_pattern_matches,
            total_unique_pattern_matches,
            highest_match_date,
            highest_match_count,
            most_common_source,
            source_count,
            most_common_destination,
            destination_count,
            most_common_pattern,
            pattern_match_count
        )

    def process_log_file(self, file, patterns, results, date_counter, source_counter, destination_counter, pattern_counter, unique_patterns_matched):
        for line in file:
            date_str = line[1:12]  # Assuming the date is in the format [dd/Mon/yyyy]
            try:
                date = datetime.strptime(date_str, "%d/%b/%Y")
            except ValueError:
                continue

            # Extract source and destination IP addresses
            parts = line.split()
            if len(parts) < 3:
                continue
            source_ip = parts[2]
            destination_ip = parts[3]

            for pattern in patterns:
                if pattern in line:
                    unique_patterns_matched.add(pattern)
                    if date not in results[pattern]:
                        results[pattern][date] = {}
                    if (source_ip, destination_ip) not in results[pattern][date]:
                        results[pattern][date][(source_ip, destination_ip)] = 0
                    results[pattern][date][(source_ip, destination_ip)] += 1

                    date_counter[date] += 1
                    source_counter[source_ip] += 1
                    destination_counter[destination_ip] += 1
                    pattern_counter[pattern] += 1

    def show_success_dialog(self, output_file, total_pattern_matches, total_unique_pattern_matches, highest_match_date, highest_match_count, most_common_source, source_count, most_common_destination, destination_count, most_common_pattern, pattern_match_count):
        success_dialog = Toplevel(self)
        success_dialog.title("Results")
        success_dialog.geometry("400x350")

        message = (
            f"Pattern count completed.\nResults saved to {output_file}\n\n"
            f"Total Pattern Matches: {total_pattern_matches}\n"
            f"Total Unique Pattern Matches: {total_unique_pattern_matches}\n\n"
            f"Highest Match Date: {highest_match_date.strftime('%Y-%m-%d')}\n({highest_match_count} matches)\n\n"
            f"Most common Source: {most_common_source} ({source_count} entries)\n"
            f"Most common Destination: {most_common_destination} ({destination_count} entries)\n\n"
            f"Most common Pattern matched: {most_common_pattern}\n({pattern_match_count} hits)"
        )

        Label(success_dialog, text=message, wraplength=280, justify="left").pack(pady=20)
        Button(success_dialog, text="OK", command=success_dialog.destroy).pack(pady=10)

    def setup_control_buttons(self):
        text_font = Font(family="Helvetica", size=16)
        # "Back" button
        back_btn = tk.Button(self, text="← Back", font=text_font, bg='steelblue4', fg='white', command=lambda: self.controller.show_frame("StartPage"))
        self.canvas.create_window(120, 760, window=back_btn)

        # "Exit" button
        exit_btn = tk.Button(self, text="Exit", font=text_font, bg='steelblue4', fg='white', command=self.controller.quit)
        self.canvas.create_window(1160, 760, window=exit_btn)

        # "Configure" button
        configure_btn = tk.Button(self, text="Configure", font=text_font, bg='steelblue4', fg='white', command=lambda: self.controller.show_frame("ConfigPage"))
        self.canvas.create_window(640, 700, window=configure_btn)  # Adjusted position

# Main application setup for testing purposes
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Log Voodoo")

    # Define and configure the controller
    controller = root
    controller.frames = {}

    for F in (LogVoodooPage, ConfigPage):
        page_name = F.__name__
        frame = F(parent=controller, controller=controller)
        controller.frames[page_name] = frame
        frame.grid(row=0, column=0, sticky="nsew")

    controller.show_frame = lambda name: controller.frames[name].tkraise()

    # Show the initial frame
    controller.show_frame("LogVoodooPage")

    root.mainloop()
