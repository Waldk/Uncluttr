"""Configuration module for Uncluttr."""

import os
import sys
import configparser
import multiprocessing

def get_base_app_files_path():
    """Get the base path for configuration files."""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.getcwd()

def update_directory_to_watch(new_directory:str):
    """Update the directory to watch in the configuration file."""
    try:
        config = configparser.ConfigParser()
        base_path = get_base_app_files_path()
        config_path = os.path.join(base_path, 'configuration', 'conf.ini')
        config.read(config_path)
        config['settings']['directory_to_watch'] = new_directory
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        print(f"Updated directory to watch to: {new_directory}")
    except Exception as e:
        print(f"An error occurred while updating the directory to watch: {e}")
        

def update_directory_order(new_order:str):
    """Update the directory to watch in the configuration file."""
    try:
        config = configparser.ConfigParser()
        base_path = get_base_app_files_path()
        config_path = os.path.join(base_path, 'configuration', 'conf.ini')
        config.read(config_path)
        config['settings']['ordre_rangement'] = new_order
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        print(f"Updated order: {new_order}")
    except Exception as e:
        print(f"An error occurred while updating the order: {e}")
        

def update_storage_directory(new_directory:str):
    """Update the directory for storage in the configuration file."""
    try:
        config = configparser.ConfigParser()
        base_path = get_base_app_files_path()
        config_path = os.path.join(base_path, 'configuration', 'conf.ini')
        config.read(config_path)
        config['settings']['storage_path'] = new_directory
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        print(f"Updated storage directory to: {new_directory}")
    except Exception as e:
        print(f"An error occurred while updating the storage directory: {e}")

def update_daemon_path(new_directory_to_watch:str,
                        daemon_process: multiprocessing.Process) -> multiprocessing.Process:
    """Restart the daemon with a new directory to watch."""
    from uncluttr.daemon.daemon import start_daemon  # Import local to avoid circular import
    if daemon_process is not None:
        print("Restarting daemon...", daemon_process)
        daemon_process.terminate()
        daemon_process.join()
        print("Daemon stopped, normalemnt r", daemon_process)

    update_directory_to_watch(new_directory_to_watch)
    daemon_process = multiprocessing.Process(target=start_daemon)
    daemon_process.start()
    print("new daemon", daemon_process)
    return daemon_process