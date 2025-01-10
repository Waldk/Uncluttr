# import threading, signal, sys
import multiprocessing, signal, sys
from uncluttr.daemon.daemon import start_daemon
from uncluttr.gui.gui import start_gui

def signal_handler(sig, frame):
    print("Exiting...")
    daemon_process.terminate()
    gui_process.terminate()
    daemon_process.join()
    gui_process.join()
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    # daemon_thread = threading.Thread(target=start_daemon, daemon=True)
    # gui_thread = threading.Thread(target=start_gui, daemon=True)

    # daemon_thread.start()
    # gui_thread.start()

    # daemon_thread.join()
    # gui_thread.join()

    daemon_process = multiprocessing.Process(target=start_daemon)
    gui_process = multiprocessing.Process(target=start_gui)

    daemon_process.start()
    gui_process.start()

    daemon_process.join()
    gui_process.join()