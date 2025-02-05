""" Module to move files to a new directory based on their metadata. """

import os
import shutil
import configparser
from uncluttr.core.configuration import get_base_app_files_path
from uncluttr.file_treatement.metadata_custom import read_custom_metadata_from_pdf,read_custom_metadata_from_image


def changement_rangement_fichier(x):
    """ Change the order of the file storage."""
    global ordre
    print('changement ordre')
    ordre = x

def rangement_fichier(file_path: str):
    """ Move a file to a new directory based on its metadata.
    :param str file_path: The path to the file.
    """
    config = configparser.ConfigParser()
    base_path = get_base_app_files_path()
    config_path = os.path.join(base_path, 'configuration', 'conf.ini')
    config.read(config_path)

    def create_directory_if_not_exists(directory: str):
        """Create a directory if it does not exist.
        :param str directory: The path to the directory.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)

    def find_or_create_subdirectory(base_directory: str, tags: list) -> str:
        """Find or create a subdirectory based on the tags.
        :param str base_directory: The base directory.
        :param list tags: The tags to use.
        :return str: The path to the subdirectory.
        """
        print(tags)
        for tag in tags:
            subdirectory = os.path.join(base_directory, tag)
            if not os.path.exists(subdirectory):
                os.makedirs(subdirectory)
            base_directory += f"/{tag}"
        return base_directory

    try:
        config = configparser.ConfigParser()
        base_path = get_base_app_files_path()
        config_path = os.path.join(base_path, 'configuration', 'conf.ini')
        config.read(config_path)
        base_directory = config['settings']['storage_path']
        ordre = config['settings']['ordre_rangement']
        print(ordre)
        create_directory_if_not_exists(base_directory)
        print("Reading metadata from the file...")
        file_type = os.path.splitext(file_path)[1]
        match file_type:
            case '.pdf':
                metadata = read_custom_metadata_from_pdf(file_path)
            case '.jpg':
                metadata = read_custom_metadata_from_image(file_path)
                metadata['document_theme'] = metadata['document_theme'].split(", ")

        tags = []
        print("Metadata read:", metadata)
        if ordre == "type -> date -> theme":
            if 'document_type' in metadata and metadata['document_type']:
                tags.append(metadata['document_type'])
            if 'document_date' in metadata and metadata['document_date']:
                tags.append(metadata['document_date'])
            if 'document_theme' in metadata and metadata['document_theme']:
                tags.append( metadata['document_theme'][0])
                tags.append( metadata['document_theme'][1])
        elif ordre == "theme -> type -> date":
            if 'document_theme' in metadata and metadata['document_theme']:
                tags.append( metadata['document_theme'][0])
                tags.append( metadata['document_theme'][1])
            if 'document_type' in metadata and metadata['document_type']:
                tags.append(metadata['document_type'])
            if 'document_date' in metadata and metadata['document_date']:
                tags.append(metadata['document_date'])
        elif ordre == "date -> type -> theme":
            if 'document_date' in metadata and metadata['document_date']:
                tags.append(metadata['document_date'])
            if 'document_type' in metadata and metadata['document_type']:
                tags.append(metadata['document_type'])
            if 'document_theme' in metadata and metadata['document_theme']:
                tags.append( metadata['document_theme'][0])
                tags.append( metadata['document_theme'][1])

        print("Tags:", tags)
        target_directory = find_or_create_subdirectory(base_directory, tags)
        print(f"Moving file to {target_directory}")
        shutil.move(file_path, target_directory)
        print(f"File moved to {target_directory}")
    except Exception as e:
        print(f"An error occurred during the moving of the file: {e}")
