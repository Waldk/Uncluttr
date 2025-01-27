import os
import shutil
# idée pour l'instant de comment cela pourrait fonctionner 
# Exemple de liste de fichiers avec leurs tags
files_with_tags = [
    ("file1.txt", ["tag1", "tag2"]),
    ("file2.txt", ["tag2", "tag3"]),
    ("file3.txt", ["tag1", "tag3"]),
]

# Répertoire de base où les fichiers seront organisés
base_directory = "tagged_files"

# Créer le répertoire de base s'il n'existe pas
if not os.path.exists(base_directory):
    os.makedirs(base_directory)

# Parcourir chaque fichier et ses tags
for file, tags in files_with_tags:
    # Pour chaque tag, créer le répertoire correspondant et copier le fichier
    for tag in tags:
        tag_directory = os.path.join(base_directory, tag)
        if not os.path.exists(tag_directory):
            os.makedirs(tag_directory)
        # Copier le fichier dans le répertoire du tag
        shutil.copy(file, os.path.join(tag_directory, file))

print("Arborescence de fichiers créée avec succès.")
