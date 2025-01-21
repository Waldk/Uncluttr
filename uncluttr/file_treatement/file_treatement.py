""" This module contains functions to treat files. """

import configparser
import zipfile
import os
import sys
import pymupdf # fitz = Ancienne version de PyMuPDF pour lire les PDF (jsp pk on uitlise pas PyMuPDF)
import joblib  # Pour sauvegarder et charger le modèle ML
from sklearn.feature_extraction.text import TfidfVectorizer
from uncluttr.core.configuration import get_base_app_files_path
from uncluttr.file_treatement.text_preprocessing import preprocess_text
# from uncluttr.file_treatement.metadata import append_metadata_to_pdf
from uncluttr.file_treatement.metadata_custom import append_custom_metadata_to_pdf

def is_structured_pdf(file_path: str) -> bool:
    """Check if the file is a structured PDF.

    :param str file_path: The path to the file.
    :return bool: _description_
    """
    with pymupdf.open(file_path) as doc:
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

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file.

    :param str file_path: path to the file to extract text from
    :return str: extracted text
    """
    with pymupdf.open(file_path) as doc:
        texte = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            texte += page.get_text("text")
    return texte

def extraire_mots_cles(texte: str) -> list:
    """Extract keywords from a text.

    :param str texte: text to extract keywords from
    :return list: extracted keywords
    """
    vectorizer = TfidfVectorizer(max_features=10)
    tfidf_matrix = vectorizer.fit_transform([texte])
    mots_cles = vectorizer.get_feature_names_out()

    return mots_cles

def classifier_document(texte):
    """Classify a document."""
    base_path = get_base_app_files_path()
    model_path = os.path.join(base_path, 'models', 'model_svm.joblib')
    vectorizer_path = os.path.join(base_path, 'models', 'vectorizer_tfidf.joblib')

    if os.path.exists(model_path) and os.path.exists(vectorizer_path):
        classifier = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
    else:
        print("Modele de classification ou vectoriseur introuvable. Veuillez entrainer le modèle\n")
        return "Inconnu"

    texte_nettoye = preprocess_text(texte)
    vecteur = vectorizer.transform([texte_nettoye])
    prediction = classifier.predict(vecteur)
    return prediction[0]

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
                    treat_structured_pdf(file_path)
                else:
                    print(f"{file_path} is an unstructured PDF.\n")
                    treat_unstructured_pdf(file_path)
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

def treat_structured_pdf(file_path: str):
    """Treat a file.

    :param str file_path: path to the file to treat
    """

    print(f"\n{file_path.encode('utf-8', errors='replace').decode('utf-8')} is a structured PDF.\n")
    texte_pdf = extract_text_from_pdf(file_path)

    texte_nettoye = preprocess_text(texte_pdf)
    print("Nettoyage du texte termine.\n")

    mots_cles = extraire_mots_cles(texte_nettoye)
    print(f"Mots-cles du PDF: {mots_cles}\n")

    type_document = classifier_document(texte_pdf)
    print(f"Type de document : {type_document}\n")
    sys.stdout.flush()
    # append_metadata_to_pdf(file_path, {"document_type": type_document,
    #                                     "document_date": None,
    #                                     "document_theme": [None, None]})
    
    append_custom_metadata_to_pdf(file_path, {"document_type": type_document,
                                        "document_date": None,
                                        "document_theme": [None, None]})

    # Ajouter le fichier dans l'arborescence
    # ALBAN

def treat_unstructured_pdf(file_path: str):
    """Treat a file.

    :param str file_path: path to the file to treat
    """

    print(f"{file_path} is unstructured, treatment to be implemented.")
