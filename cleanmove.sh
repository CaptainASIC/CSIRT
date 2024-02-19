#!/bin/bash

# Clear the screen
clear

# Splash image with ASCII art
echo ""
echo "                      ██╗     ██╗██╗  ██╗██╗██╗     ";
echo "                      ██║     ██║╚██╗██╔╝██║██║     ";
echo "                      ██║     ██║ ╚███╔╝ ██║██║     ";
echo "                      ██║     ██║ ██╔██╗ ██║██║     ";
echo "                      ███████╗██║██╔╝ ██╗██║███████╗";
echo "                      ╚══════╝╚═╝╚═╝  ╚═╝╚═╝╚══════╝";
echo "                          Drive Sanitizer Script                          "
echo "              Created by Samuel Presgraves, Security Engineer"
echo "               LIXIL HQ, Digital Group, Security & IAM Team"
echo "                          Version 1.0, Feb 2024"
echo ""

# Initialize variables
source_dir="/media/cleaner/Windows/Users"
destination_dir=""
extensions_file="extensions.bsd"
prohibited_file="prohibited.bsd"
copied_files=0
total_size=0

# Function to display script usage
usage() {
    echo "Usage: $0"
    exit 1
}

# Function to convert bytes to a human-readable format
convert_bytes() {
    local bytes=$1
    if (( bytes < 1024 )); then
        echo "${bytes} bytes"
    elif (( bytes < 1024**2 )); then
        echo "$((bytes / 1024)) KB"
    elif (( bytes < 1024**3 )); then
        echo "$((bytes / 1024**2)) MB"
    else
        echo "$((bytes / 1024**3)) GB"
    fi
}

# Function to convert seconds to a human-readable format
convert_seconds() {
    local sec=$1
    local days=$((sec / 86400))
    local hours=$((sec / 3600 % 24))
    local minutes=$((sec / 60 % 60))
    local seconds=$((sec % 60))
    printf "%d days, %02d:%02d:%02d" $days $hours $minutes $seconds
}

# Function to produce a system beep
system_beep() {
    echo -en "\007"
}

# Prompt the user for the destination directory
read -p "Enter the User's Real Name as Last.First: " destination_name

# Check if destination name is provided
if [ -z "$destination_name" ]; then
    echo "Error: Destination directory name is required."
    usage
fi

# Construct the full destination directory path
destination_dir="/media/cleaner/My Passport/$destination_name"

# Record start time
start_time=$(date +%s)
echo "Starting file copy..."

# Read extensions from the reference file and format them for rsync
extensions=$(awk '{printf "--include '\''*%s'\'' ", $0}' "$extensions_file")

# Perform the file copy using rsync
rsync_output=$(rsync -av --stats $extensions --exclude='*.*' --exclude='desktop.ini' --exclude='/administrator/' --exclude="/Default/" --exclude='/Public/' "$source_dir/" "$destination_dir")
echo "File copy completed."

# Extract the number of files copied
copied_files=$(echo "$rsync_output" | grep 'Number of regular files transferred' | awk '{print $5}')
echo "Number of files copied: $copied_files"

# Extract the total file size
total_size=$(echo "$rsync_output" | grep 'Total transferred file size' | awk '{print $5}')
echo -n "Total file size: "
convert_bytes "$total_size"

# Delete prohibited files
echo "Deleting prohibited files..."
while IFS= read -r file; do
    rm -f "$destination_dir/$file"
done < "$prohibited_file"

# Clean up empty directories in the destination directory
echo "Cleaning up empty directories in $destination_dir..."
find "$destination_dir" -empty -type d -delete

# Calculate elapsed time
end_time=$(date +%s)
elapsed_time=$((end_time - start_time))

# Convert elapsed time to human-readable format
elapsed_time_readable=$(convert_seconds $elapsed_time)

# Output the elapsed time
echo "Total time taken: $elapsed_time_readable"

# Finish
timidity ffvii.midi > /dev/null 2>&1
