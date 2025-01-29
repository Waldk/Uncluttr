import os
import shutil
from uncluttr.file_treatement.metadata_custom import read_custom_metadata_from_pdf
import configparser
from uncluttr.core.configuration import get_base_app_files_path

ordre = " 123"

def changemtn_rangement_fichier(x):
    global ordre
    print("il y a un changement d'ordre de rangement")
    ordre = x

def rangement_fichier(file_path):
    print("\n\n ",ordre,"\n\n")
    config = configparser.ConfigParser()
    base_path = get_base_app_files_path()
    config_path = os.path.join(base_path, 'configuration', 'conf.ini')
    config.read(config_path)
    path_storage = config['settings']['storage_path']
   
    print("\n\n vous ête au sein du rangement fichier\n\n")
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

    base_directory = os.path.join(os.path.dirname(path_storage), "uncluttr")
    create_directory_if_not_exists(base_directory)

    metadata = read_custom_metadata_from_pdf(file_path)
    tags = []
    
    if ordre == "type -> date -> theme":
        if 'document_type' in metadata and metadata['document_type']: # pouvoir changer l'ordre / configurer le path / trouver un moyen de respecter une autre arborescence déjà présente
            tags.append(metadata['document_type'])
        if 'document_date' in metadata and metadata['document_date']:
            tags.append(metadata['document_date'])
        if 'document_theme' in metadata and metadata['document_theme']:
            tags.extend([theme for theme in metadata['document_theme'] if theme != 'None'])
    elif ordre == "theme -> type -> date":
        if 'document_theme' in metadata and metadata['document_theme']:
            tags.extend([theme for theme in metadata['document_theme'] if theme != 'None'])
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
            tags.extend([theme for theme in metadata['document_theme'] if theme != 'None'])
    
    target_directory = find_or_create_subdirectory(base_directory, tags)
    shutil.move(file_path, os.path.join(target_directory, os.path.basename(file_path)))

    print(f"File moved to {target_directory}")