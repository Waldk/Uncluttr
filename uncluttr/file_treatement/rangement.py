import os
import shutil
from uncluttr.file_treatement.metadata_custom import read_custom_metadata_from_pdf


def rangement_fichier(file_path):
    
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

    base_directory = os.path.join(os.path.dirname(file_path), "uncluttr")
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