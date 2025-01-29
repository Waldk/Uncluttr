""" Module to move files to a new directory based on their metadata. """

import os
import shutil
import configparser
from uncluttr.core.configuration import get_base_app_files_path
from uncluttr.file_treatement.metadata_custom import read_custom_metadata_from_pdf

def rangement_fichier(file_path):
    """Move the file to a new directory based on its metadata."""
    def create_directory_if_not_exists(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def find_or_create_subdirectory(base_directory, tags):
        for tag in tags:
            subdirectory = os.path.join(base_directory, tag)
            if not os.path.exists(subdirectory):
                os.makedirs(subdirectory)
            return subdirectory
        return base_directory

    try:
        config = configparser.ConfigParser()
        base_path = get_base_app_files_path()
        config_path = os.path.join(base_path, 'configuration', 'conf.ini')
        config.read(config_path)
        base_directory = config['settings']['storage_path']

        create_directory_if_not_exists(base_directory)

        metadata = read_custom_metadata_from_pdf(file_path)
        print(metadata)
        tags = []
        if 'document_type' in metadata and metadata['document_type']: # pouvoir changer l'ordre / configurer le path / trouver un moyen de respecter une autre arborescence déjà présente
            tags.append(metadata['document_type'])
        if 'document_date' in metadata and metadata['document_date']:
            tags.append(metadata['document_date'])
        if 'document_theme' in metadata and metadata['document_theme']:
            tags.extend([theme for theme in metadata['document_theme'] if theme != 'None'])

        target_directory = find_or_create_subdirectory(base_directory, tags)
        shutil.move(file_path, os.path.join(target_directory, os.path.basename(file_path)))

        print(f"File moved to {target_directory}")
    except Exception as e:
        print(f"An error occurred during the moving of the file: {e}")
