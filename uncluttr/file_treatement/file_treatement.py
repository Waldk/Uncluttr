""" This module contains functions to treat files. """

import configparser
import zipfile
import os
import sys
import fitz
from uncluttr.core.configuration import get_base_app_files_path


def is_structured_pdf(file_path: str) -> bool:
    """Check if the file is a structured PDF.

    :param str file_path: The path to the file.
    :return bool: _description_
    """
    with fitz.open(file_path) as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                return True
    return False

def folder_analysis(path:str=None):
    """Analyzing files in a folder.

    :param str path: path to the folder to analyse, defaults to None
    """
    try:
        if path is None:
            config = configparser.ConfigParser()
            base_path = get_base_app_files_path()
            config_path = os.path.join(base_path, 'configuration', 'conf.ini')
            config.read(config_path)
            path = config['settings']['directory_to_watch']

        print(f"Analyzing files in {path}...")
        sys.stdout.flush()
        for root, dirs, files in os.walk(path):
            for file in files:
                try:
                    file_analysis(os.path.join(root, file))
                except PermissionError as e:
                    print(f"Permission error: {e}")
                except FileNotFoundError as e:
                    print(f"File not found: {e}")
                except Exception as e:
                    print(f"An error occurred during file analysis: {e}")
    except NotADirectoryError as e:
        print(f"{path} is not a directory.")
    except PermissionError as e:
        print(f"Permission error: {e}")
    except Exception as e:
        print(f"An error occurred during folder analysis: {e}")


def file_analysis(file_path: str = None):
    """Analyse a file.

    :param str file_path: path to the file to analyse, defaults to None
    """
    try:
        root, file = os.path.split(file_path)
        file_type = os.path.splitext(file_path)[1]
        match file_type:
            case '.zip':
                extract_path = os.path.join(root, os.path.splitext(file)[0])
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
                os.remove(file_path)

                print(file_path, "extracted.")
                sys.stdout.flush()
                folder_analysis(extract_path)

            case '.pdf':
                print(f"Analyzing {file_path} ...")
                if is_structured_pdf(file_path):
                    print(f"{file_path} is a structured PDF.\n")
                else:
                    print(f"{file_path} is an unstructured PDF.\n")
                sys.stdout.flush()
            case _:
                print(f"{file_path} is not a file type we currently handle.")
                sys.stdout.flush()
    except zipfile.BadZipFile as e:
        print(f"Bad zip file: {e}")
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except PermissionError as e:
        print(f"Permission error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during file analysis: {e}")
