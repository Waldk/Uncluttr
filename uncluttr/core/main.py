"""Main entry point for the Uncluttr application."""

import multiprocessing
import signal
import sys
from uncluttr.daemon.daemon import start_daemon
from uncluttr.gui.gui import start_gui

DAEMON_PROCESS = None
GUI_PROCESS = None


def signal_handler(sig, frame):
    """This function is called when the user presses Ctrl+C to end the application."""
    print("Exiting...")
    if DAEMON_PROCESS is not None:
        DAEMON_PROCESS.terminate()
        DAEMON_PROCESS.join()
    if GUI_PROCESS is not None:
        GUI_PROCESS.terminate()
        GUI_PROCESS.join()
    sys.exit(0)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    signal.signal(signal.SIGINT, signal_handler)

    try:
        DAEMON_PROCESS = multiprocessing.Process(target=start_daemon)
        DAEMON_PROCESS.start()

        GUI_PROCESS = multiprocessing.Process(target=start_gui(DAEMON_PROCESS))
        GUI_PROCESS.start()

        DAEMON_PROCESS.join()
        GUI_PROCESS.join()
    except (KeyboardInterrupt, SystemExit):
        print("Interrupted by user")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if DAEMON_PROCESS is not None:
            DAEMON_PROCESS.terminate()
            DAEMON_PROCESS.join()
        if GUI_PROCESS is not None:
            GUI_PROCESS.terminate()
            GUI_PROCESS.join()
