# source : https://pypi.org/project/watchdog/

import os, sys, time, configparser

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from uncluttr.fileTreatement.fileTreatement import folderAnalysis


class Watcher:
    def __init__(self, directory_to_watch):
        self.DIRECTORY_TO_WATCH = directory_to_watch
        self.observer = Observer()

    def run(self):
        print(self.DIRECTORY_TO_WATCH)
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_created(event):
        if event.is_directory:
            return None
        else:
            print(f"Received created event - {event.src_path}")
            sys.stdout.flush()
            folderAnalysis()
            

def start_daemon():
    try:
        config = configparser.ConfigParser()

        if getattr(sys, 'frozen', False):
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        else:
            base_path = os.getcwd()
        
        config_path = os.path.join(base_path, 'configuration', 'conf.ini')
        config.read(config_path)
        directory_to_watch = config['settings']['directory_to_watch']
        
        w = Watcher(directory_to_watch)
        print("Daemon started")
        sys.stdout.flush()
        
        w.run()
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    start_daemon()