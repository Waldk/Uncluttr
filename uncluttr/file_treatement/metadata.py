"""This module contains functions to handle metadata."""

import os
import shutil
import pymupdf

# Option 1: Utiliser PyMuPDF et sauvegarder dans la metadata qui existe déjà : "subject"
def append_metadata_to_pdf(file_path, metadata):
    """Append metadata to a file.

    :param str file_path: The path to the file.
    :param dict metadata : The metadata to append to the file.
    """

    doc = pymupdf.open(file_path)
    current_metadata = doc.metadata
    print("Old metadata: ", current_metadata)

    for key, value in metadata.items():
        if key in ["title", "author", "keywords", "creator",
                   "producer", "creationDate", "modDate", "trapped"]:
            current_metadata[key] = value
        else:
            # au cas où vous envoyez des listes
            if isinstance(value, list):
                value = ", ".join(map(str, value))

            subject = current_metadata.get("subject", "")
            new_subject = []
            key_exists = False
            for part in subject.split(" | "):
                if part.startswith(f"{key}:"):
                    new_subject.append(f"{key}:{value}")
                    key_exists = True
                else:
                    new_subject.append(part)
            if not key_exists:
                new_subject.append(f"{key}:{value}")
            current_metadata["subject"] = " | ".join(filter(None, new_subject))

    doc.set_metadata(current_metadata)
    temp_file_path = file_path.replace(".pdf", "_temp.pdf")
    doc.save(temp_file_path)
    doc.close()

    # Remplacer l'ancien fichier par le nouveau
    original_stat = os.stat(file_path)
    shutil.copy2(temp_file_path, file_path)
    os.utime(file_path, (original_stat.st_atime, original_stat.st_mtime))
    os.remove(temp_file_path)

    print("New metadata:", read_metadata_from_pdf(file_path))

# Option 1: Utiliser PyMuPDF pour lire les métadonnées donc reconstruire en puisant dans "subject"
def read_metadata_from_pdf(file_path):
    """Read metadata from a PDF file.

    :param str file_path: The path to the file.
    :return dict: The metadata of the file.
    """

    doc = pymupdf.open(file_path)
    metadata = doc.metadata
    doc.close()
    reconstructed_metadata = {}
    for key, value in metadata.items():
        if key == "subject":
            subject_parts = value.split(" | ")
            for part in subject_parts:
                sub_key, sub_value = part.split(":", 1)
                if sub_key == "document_theme":
                    sub_value = sub_value.split(", ")
                reconstructed_metadata[sub_key] = sub_value
        else:
            reconstructed_metadata[key] = value

    return reconstructed_metadata

# Exemple d'utilisation
if __name__ == "__main__":
    PDF_PATH = os.path.join(os.getcwd(), 'assets', 'example', 'test_metadata.pdf')
    append_metadata_to_pdf(PDF_PATH, {"document_type": "Lettre de motivation",
                                        "document_date": None,
                                        "document_theme": ["example", "test"]})
    print("\nMetadata appended successfully.\n")

    print("Test reading metadata from PDF: ", read_metadata_from_pdf(PDF_PATH))
