"""This module contains functions to handle metadata."""
# Source: https://pymupdf.readthedocs.io/en/latest/recipes-low-level-interfaces.html#how-to-extend-pdf-metadata

import os
import sys
import shutil
import pymupdf
from PIL import Image
from PIL.ExifTags import TAGS


# Option 2: Ajouter des métadonnées personnalisées
def append_custom_metadata_to_pdf(file_path:str, metadata:dict):
    """Append metadata to a PDF file.

    :param str file_path: The path to the file.
    :param dict metadata : The metadata to append to the file.
    """
    print("\nAppending metadata to the PDF file...")
    doc = pymupdf.open(file_path)
    current_metadata = doc.metadata
    print("\nOld metadata:", current_metadata)

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

    print("\nNew metadata:", read_custom_metadata_from_pdf(file_path))
    sys.stdout.flush()

def read_custom_metadata_from_pdf(file_path:str) -> dict:
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

def append_custom_metadata_to_image(file_path:str, metadata:dict):
    """Append metadata to a image file.

    :param str file_path: The path to the file.
    :param dict metadata : The metadata to append to the file.
    """

    image = Image.open(file_path)
    exif_data = image.info.get("exif", b"")

    exif_dict = {TAGS.get(tag, tag): value for tag, value in image.getexif().items()}
    for key, value in metadata.items():
        if isinstance(value, list):
            value = ", ".join(map(str, value))
        exif_dict[key] = value

    temp_file_path = file_path.replace(".jpg", "_temp.jpg")
    image.save(temp_file_path, exif=exif_data)
    image.close()

    original_stat = os.stat(file_path)
    shutil.copy2(temp_file_path, file_path)
    os.utime(file_path, (original_stat.st_atime, original_stat.st_mtime))
    os.remove(temp_file_path)

    print("New metadata:", read_custom_metadata_from_image(file_path))
    sys.stdout.flush()

def read_custom_metadata_from_image(file_path:str) -> dict:
    """Read metadata from a image file.

    :param str file_path: The path to the file.
    :return dict: The metadata of the file.
    """
    with Image.open(file_path) as image:
        exif_data = image.getexif()
        metadata = {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
    return metadata

# Exemple d'utilisation
if __name__ == "__main__":
    print("\nTry append metadata to pdf\n")
    PDF_PATH = os.path.join(os.getcwd(), 'assets', 'example', 'test_custom_metadata.pdf')
    append_custom_metadata_to_pdf(PDF_PATH, {"document_type": "Lettre de motivation",
                                        "document_date": None,
                                        "document_theme": ["example", "test"]})
    print("\nCustom metadata appended successfully to the pdf.")
    print("Test reading custom metadata from PDF: ", read_custom_metadata_from_pdf(PDF_PATH))

    print("\nTry append metadata to jpeg\n")
    JPEG_PATH = os.path.join(os.getcwd(), 'assets', 'example', 'test_custom_metadata.jpg')
    append_custom_metadata_to_image(JPEG_PATH, {
        "document_type": "Facture",
        "document_date": "2024-04-03",
        "document_theme": ["example", "test"]
    })
    print("\nCustom metadata appended successfully to the jpg.")
    print("Test reading custom metadata from jpeg: ", read_custom_metadata_from_image(JPEG_PATH))
