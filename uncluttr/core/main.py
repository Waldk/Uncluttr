from uncluttr.daemon.daemon import start_daemon
from uncluttr.gui.gui import start_gui

if __name__ == "__main__":
    # Start the daemon
    start_daemon()
    
    # Start the GUI
    start_gui()