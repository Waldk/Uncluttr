"""This module contains functions to handle metadata."""
# Source: https://pymupdf.readthedocs.io/en/latest/recipes-low-level-interfaces.html#how-to-extend-pdf-metadata

import os
import shutil
import pymupdf

# Option 2: Ajouter des métadonnées personnalisées
def append_custom_metadata_to_pdf(file_path, metadata):
    """Append metadata to a PDF file.

    :param str file_path: The path to the file.
    :param dict metadata : The metadata to append to the file.
    """

    doc = pymupdf.open(file_path)
    current_metadata = doc.metadata
    print("Old metadata:", current_metadata)

    # Obtenir la référence des métadonnées
    what, value = doc.xref_get_key(-1, "Info")
    if what != "xref":
        raise ValueError("PDF has no metadata")

    xref = int(value.replace("0 R", ""))

    for key, value in metadata.items():
        if key in ["title", "author", "subject", "keywords",
                   "creator", "producer", "creationDate", "modDate", "trapped"]:
            current_metadata[key] = value
        else:
            if isinstance(value, list):
                value = ", ".join(map(str, value))
            doc.xref_set_key(xref, key, pymupdf.get_pdf_str(value))

    doc.set_metadata(current_metadata)

    # Enregistrer les modifications sous un nouveau nom
    temp_file_path = file_path.replace(".pdf", "_temp.pdf")
    doc.save(temp_file_path)
    doc.close()

    # Remplacer l'ancien fichier par le nouveau
    original_stat = os.stat(file_path)
    shutil.copy2(temp_file_path, file_path)
    os.utime(file_path, (original_stat.st_atime, original_stat.st_mtime))
    os.remove(temp_file_path)
    
    print("New metadata:", read_custom_metadata_from_pdf(file_path))

def read_custom_metadata_from_pdf(file_path):
    """Read metadata from a PDF file.

    :param str file_path: The path to the file.
    :return dict: The metadata of the file.
    """

    doc = pymupdf.open(file_path)
    metadata = doc.metadata

    what, value = doc.xref_get_key(-1, "Info")
    if what != "xref":
        raise ValueError("PDF has no metadata")

    xref = int(value.replace("0 R", ""))
    custom_metadata = {}
    for key in doc.xref_get_keys(xref):
        if key not in ["Title", "Author", "Subject", "Keywords",
                       "Creator", "Producer", "CreationDate", "ModDate", "Trapped"]:
            custom_metadata[key] = doc.xref_get_key(xref, key)[1]

    doc.close()

    reconstructed_metadata = {**metadata, **custom_metadata}
    for key, value in reconstructed_metadata.items():
        if key == "document_theme":
            value = value.split(", ")
        reconstructed_metadata[key] = value

    return reconstructed_metadata

# Exemple d'utilisation
if __name__ == "__main__":
    PDF_PATH = os.path.join(os.getcwd(), 'assets', 'example', 'test_custom_metadata.pdf')
    append_custom_metadata_to_pdf(PDF_PATH, {"document_type": "Lettre de motivation",
                                        "document_date": None,
                                        "document_theme": ["example", "test"]})
    print("\nCustom metadata appended successfully.\n")

    print("Test reading custom metadata from PDF: ", read_custom_metadata_from_pdf(PDF_PATH))
