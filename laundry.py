import sys
import os

# Function to check for graphical environment
def is_graphical_environment():
    return os.environ.get('DISPLAY', None) is not None or os.environ.get('WAYLAND_DISPLAY', None) is not None

if __name__ == "__main__":
    # Check for '--cli' argument
    cli_mode = '--cli' in sys.argv

    # Decide whether to run in CLI mode or GUI mode
    if cli_mode or not is_graphical_environment():
        from lib import functions as cli_functions
        cli_functions.main()
    else:
        from lib import gui as gui_application
        gui_application.run_gui()
