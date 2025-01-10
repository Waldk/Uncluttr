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
    multiprocessing.freeze_support()
    signal.signal(signal.SIGINT, signal_handler)

    daemon_process = multiprocessing.Process(target=start_daemon)
    gui_process = multiprocessing.Process(target=start_gui)

    try:
        daemon_process.start()
        gui_process.start()
        daemon_process.join()
        gui_process.join()
    finally:
        daemon_process.terminate()
        gui_process.terminate()
        daemon_process.join()
        gui_process.join()