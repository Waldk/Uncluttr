""" This module contains functions to extract text from PDF files using OCR. """

import os
import pymupdf
import easyocr

def extract_pdf_text_ocr(pdf_path: str) -> str:
    """Extract text from a PDF file using OCR with EasyOCR.
    :param str pdf_path: The path to the PDF file.
    :return str: The extracted text.
    """
    try:
        text = []
        reader = easyocr.Reader(["fr"])
        output_folder = os.path.join(os.path.dirname(pdf_path), 'temp_images')
        image_paths = convert_pdf_to_images(pdf_path, output_folder)

        for image_page in image_paths:
            page_text = extract_image_text_ocr(image_page, reader)
            text.append(page_text)

        for image_page in image_paths:
            os.remove(image_page)
        os.rmdir(output_folder)

        return "\n".join(text)
    except Exception as e:
        print(f"An error occurred during the treatment of the unstructured PDF: {e}")
        return None

def extract_image_text_ocr(image_path: str, reader=None) -> str:
    """Extract text from an image using OCR with EasyOCR.

    :param str image_path: The path to the image file.
    :return str: The extracted text.
    """
    print(f"Extracting text from {os.path.basename(image_path)}")

    if reader is None:
        reader = easyocr.Reader(["fr"])

    results = reader.readtext(image_path, detail=0)
    return " ".join(results)

def convert_pdf_to_images(pdf_path: str, output_folder: str, zoom: float = 3.0) -> list:
    """Convert a PDF file to images.

    :param str pdf_path: The path to the PDF file.
    :param str output_folder: The folder to save the images.
    :param float zoom: The zoom factor for the images (default is 3.0).
    :return list: A list of paths to the generated images.
    """
    try:
        pdf_document = pymupdf.open(pdf_path)
        image_paths = []

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        with pymupdf.open(pdf_path) as pdf_document:
            for i, page in enumerate(pdf_document):
                mat = pymupdf.Matrix(zoom, zoom)
                pixmap = page.get_pixmap(matrix=mat)

                output_path = os.path.join(output_folder, f"page_{i + 1}.png")

                pixmap.save(output_path)
                image_paths.append(output_path)
                print(f"Page {i + 1} saved as {output_path}")

        return image_paths
    except Exception as e:
        print(f"An error occurred during PDF to image conversion: {e}")
        return []

if __name__ == "__main__":
    PDF_PATH = os.path.join(os.getcwd(), 'assets', 'example', 'test_ocr.pdf')
    print("Contenu du document :", extract_pdf_text_ocr(PDF_PATH))

    JPEG_PATH = os.path.join(os.getcwd(), 'assets', 'example', 'test_image.jpg')
    print("Contenu du document :", extract_image_text_ocr(JPEG_PATH))
