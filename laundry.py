import sys
import os
from pathlib import Path

# Modify the Python path to include the 'lib' directory
script_dir = Path(__file__).resolve().parent
lib_dir = script_dir / 'lib'
sys.path.append(str(lib_dir))

# Import the GUI or CLI module from the 'lib' directory
from main import MainApp as GUIApp
from lndcli import main as cli_main

def is_graphical_environment():
    return os.environ.get('DISPLAY', None) is not None or os.environ.get('WAYLAND_DISPLAY', None) is not None

if __name__ == "__main__":
    # Decide whether to run in CLI mode or GUI mode based on environment and arguments
    if '--cli' in sys.argv or not is_graphical_environment():
        cli_main()
    else:
        app = GUIApp()
        app.mainloop()
