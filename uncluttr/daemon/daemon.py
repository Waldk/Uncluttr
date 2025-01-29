"""This module contains the daemon that watches the directory to watch for new files.
source : https://pypi.org/project/watchdog/
"""

import os
import sys
import time
import configparser
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from uncluttr.file_treatement.file_treatement import file_analysis
from uncluttr.core.configuration import get_base_app_files_path


class Watcher:
    """Class to watch a directory for new files."""

    def __init__(self, directory_to_watch):
        self.directory_to_watch = directory_to_watch
        self.observer = Observer()

    def run(self):
        """Start the observer."""

        print("Folder to watch: ", self.directory_to_watch)
        event_handler = Handler()
        self.observer.schedule(event_handler, self.directory_to_watch, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    """Class to handle file system events."""
    @staticmethod
    def on_created(event):
        if event.is_directory:
            return None
        else:
            print(f"Received created event - {event.src_path}")
            sys.stdout.flush()

            try:
                wait_for_file(event.src_path)
                file_analysis(event.src_path)
            except Exception as e:
                print(f"An error occurred : {e}")

def start_daemon():
    """Start the daemon."""
    try:
        config = configparser.ConfigParser()

        base_path = get_base_app_files_path()
        config_path = os.path.join(base_path, 'configuration', 'conf.ini')
        config.read(config_path)
        directory_to_watch = config['settings']['directory_to_watch']

        w = Watcher(directory_to_watch)
        print("Daemon started")
        sys.stdout.flush()
        w.run()
    except configparser.Error as e:
        print(f"Configuration error: {e}")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except PermissionError as e:
        print(f"Permission error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def wait_for_file(file_path:str, timeout=10):
    """Wait for a file to be completely copied."""
    start_time = time.time()
    while True:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            try:
                with open(file_path, 'rb') as f:
                    f.read()
                break
            except IOError:
                pass
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Timeout waiting for file {file_path} to be ready.")
        time.sleep(1)

if __name__ == '__main__':
    start_daemon()
