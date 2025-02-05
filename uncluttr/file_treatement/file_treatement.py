""" This module contains functions to treat files. """

import os
import re
import itertools
import sys
import time
import zipfile
import configparser
import multiprocessing
from collections import Counter
import nltk
import joblib
import pymupdf
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from uncluttr.core.configuration import get_base_app_files_path
from uncluttr.file_treatement.rangement import rangement_fichier
from uncluttr.file_treatement.text_preprocessing import preprocess_text, refine_words
from uncluttr.file_treatement.metadata_custom import append_custom_metadata_to_pdf, append_custom_metadata_to_image
from uncluttr.file_treatement.character_recognition import extract_pdf_text_ocr, extract_image_text_ocr


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
    try :
        with pymupdf.open(file_path) as doc:
            texte = ""
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                texte += page.get_text("text")
        return texte
    except Exception as e:
        print(f"An error occurred during folder analysis: {e}")

def extraire_mots_cles(texte: str) -> list:
    """Extract keywords from a text.

    :param str texte: text to extract keywords from
    :return list: extracted keywords
    """
    try:
        stopwords_fr = stopwords.words('french')
    except LookupError:
        nltk.download('stopwords')
        stopwords_fr = stopwords.words('french')

    # Ajout de stopwords
    stopwords_plus = ['d', 'l', 'avoir', 'etre', 'mettre', 'c', 's', 'a', 'b', 'e', 'f', 'g', 'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q', 'r', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    stopwords_final = stopwords_fr + stopwords_plus

    vectorizer = TfidfVectorizer(
        max_features=15,
        stop_words=stopwords_final,
        ngram_range=(1, 2)
    )
    tfidf_matrix = vectorizer.fit_transform([texte])
    mots_cles = vectorizer.get_feature_names_out()

    return mots_cles

def generate_ngrams(words, n=2):
    """Generate n-grams from a list of words.

    This function creates n-grams (sequences of `n` consecutive words) from a given list of words.

    :param list words: The list of words to generate n-grams from
    :param int n: The size of the n-grams (default is 2 for bigrams)
    :return: A list of n-grams
    :rtype: list
    """
    ngrams = list(itertools.zip_longest(*[words[i:] for i in range(n)], fillvalue=""))
    return [" ".join(gram).strip() for gram in ngrams if "" not in gram]

def generate_theme_from_text(text):
    """Generate a theme from a text by extracting the most frequent keywords and phrases.

    This function preprocesses the text, removes short words, refines words for consistency, 
    generates bigrams and trigrams, and selects the most frequently occurring terms.

    :param str text: The input text to analyze
    :return: A list of the top 5 most frequent words, bigrams, or trigrams
    :rtype: list
    """
    words = text.split()
    words = [word for word in words if len(word) > 3]

    refined_words = refine_words(words)

    bigrams = generate_ngrams(refined_words, 2)
    trigrams = generate_ngrams(refined_words, 3)

    word_counts = Counter(refined_words)
    bigram_counts = Counter(bigrams)
    trigram_counts = Counter(trigrams)

    all_counts = word_counts + bigram_counts + trigram_counts

    return [word for word, _ in all_counts.most_common(5)]

def classifier_document(texte):
    """Classify a document based on pre-trained model.

    :param texte: text to classify
    :return: classification label
    """
    try:
        base_path = get_base_app_files_path()
        model_path = os.path.join(base_path, 'models', 'model_svm.joblib')
        vectorizer_path = os.path.join(base_path, 'models', 'vectorizer_tfidf.joblib')

        start_time = time.time()
        classifier = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        print(f"Model loaded in {time.time() - start_time:.2f} seconds")

        texte_nettoye = preprocess_text(texte)
        vecteur = vectorizer.transform([texte_nettoye])
        prediction_type = classifier.predict(vecteur)
        prediction_theme = generate_theme_from_text(texte_nettoye)
        return [prediction_type[0], prediction_theme]

    except FileNotFoundError:
        return "Modèle ou vectoriseur introuvable. Veuillez entraîner le modèle."
    except Exception as e:
        return f"Erreur lors de la classification : {str(e)}"

def file_analysis(file_path: str = None, processes: list = []):
    """Analyse a file.

    :param str file_path: path to the file to analyse, defaults to None
    :param list processes: list of running processes, defaults to []
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
                print(f"Analyzing pdf {file_path} ...")
                if is_structured_pdf(file_path):
                    print(f"{file_path} is a structured PDF.\n")
                    process = multiprocessing.Process(target=treat_structured_pdf, args=(file_path,), name=f"Process-Structured-{file}")
                else:
                    print(f"{file_path} is an unstructured PDF.\n")
                    process = multiprocessing.Process(target=treat_unstructured_pdf, args=(file_path,), name=f"Process-Unstructured-{file}")
                process.start()
                processes.append((process, time.time()))
                sys.stdout.flush()
            case '.png' | '.jpg' | '.jpeg':
                print(f"Analyzing image {file_path} ...")
                process = multiprocessing.Process(target=treat_image, args=(file_path,), name=f"Process-Image-{file}")
                process.start()
                processes.append((process, time.time()))
                sys.stdout.flush()
            case _:
                print(f"{file_type} is not a file type we currently handle.")
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
    texte_pdf = extract_text_from_pdf(file_path)

    texte_nettoye = preprocess_text(texte_pdf)

    document_date = extract_date(texte_pdf)
    print("Date :", document_date)

    mots_cles = extraire_mots_cles(texte_nettoye)
    print(f"Mots-cles du PDF: {mots_cles}\n")

    type_document, theme_document = classifier_document(texte_pdf)
    print(f"Type de document : {type_document}\n")
    print(f"Theme du document : {theme_document}\n")
    sys.stdout.flush()

    append_custom_metadata_to_pdf(file_path, {"document_type": type_document,
                                        "document_date": document_date,
                                        "document_theme": theme_document})
    rangement_fichier(file_path)

def treat_unstructured_pdf(file_path: str):
    """Treat an unstructured pdf.

    :param str file_path: path to the file to treat
    """
    pdf_text= extract_pdf_text_ocr(file_path)
    document_date = extract_date(pdf_text)
    print("Date :", document_date)
    cleaned_text = preprocess_text(pdf_text)
    keywords = extraire_mots_cles(cleaned_text)
    print(f"Keywords: {keywords}")

    type_document, theme_document = classifier_document(pdf_text)
    print(f"Document type: {type_document}")
    print(f"Document theme: {theme_document}")
    sys.stdout.flush()

    append_custom_metadata_to_pdf(file_path, {"document_type": type_document,
                                        "document_date": document_date,
                                        "document_theme": theme_document})
    rangement_fichier(file_path)

def treat_image(file_path: str):
    """Treat an image.

    :param str file_path: path to the image to treat
    """
    try:
        image_text= extract_image_text_ocr(file_path)
        cleaned_text = preprocess_text(image_text)
        keywords = extraire_mots_cles(cleaned_text)
        print(f"Keywords: {keywords}")

        type_document, theme_document = classifier_document(image_text)
        print(f"Document type: {type_document}")
        print(f"Document theme: {theme_document}")
        sys.stdout.flush()

        append_custom_metadata_to_image(file_path, {"document_type": type_document,
                                            "document_date": None,
                                            "document_theme": theme_document})
        rangement_fichier(file_path)
    except Exception as e:
        print(f"An error occurred during image treatment: {e}")

# Deuxième Version : Extraction de la date pour tout doc
# Problème à régler : ne prends pas en compte les mois écris en majuscule
def extract_date(text):
    """Extract dates from a given text using predefined regex patterns.

    The function normalizes extracted dates to the format "DD/MM/YYYY" and 
    handles century correction for two-digit years.

    :param str text: The input text to analyze
    :return: A list of extracted dates in "DD/MM/YYYY" format
    :rtype: list
    """
    date_patterns1 = [
        r'\b(?<!\bn[ée]\s)le\s(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})\b',                    # Formats JJ/MM/AAAA ou JJ-MM-AAAA
        r'\b(?<!\bn[ée]\s)le\s(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b',                      # Formats AAAA/MM/JJ ou AAAA-MM-JJ
        r'\b(?<!\bn[ée]\s)le\s(\d{1,2})\s(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s(\d{4})\b',      # Formats JJ mois AAAA
        r'\b(?<!\bn[ée]\s)le\s(\d{1,2})\s(janv.|fév.|mars|avr.|mai|juin|juil.|août|sept.|oct.|nov.|déc.)\s(\d{4})\b',       # Formats JJ abréviation mois AAAA
    ]

    date_patterns2 = [                                                 # Pattern de date seule si aucune signature n'a été vérifié auparavant
        r'\b(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})\b',                    # Formats JJ/MM/AAAA ou JJ-MM-AAAA
        r'\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b',                      # Formats AAAA/MM/JJ ou AAAA-MM-JJ
        r'\b(\d{1,2})\s(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s(\d{4})\b',      # Formats JJ mois AAAA
        r'\b(\d{1,2})\s(janv.|fév.|mars|avr.|mai|juin|juil.|août|sept.|oct.|nov.|déc.)\s(\d{4})\b',       # Formats JJ abréviation mois AAAA
    ]

    date_patterns3 = [                                    # Pattern de date seule si aucune signature n'a été vérifié auparavant
        r'\b(\d{1,2})[-/](\d{2,4})\b',                    # Formats MM/AAAA ou MM-AAAA
        r'\b(\d{4})[-/](\d{1,2})\b',                      # Formats AAAA/MM ou AAAA-MM
        r'\b(janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s(\d{4})\b',      # Formats mois AAAA
        r'\b(janv.|fév.|mars|avr.|mai|juin|juil.|août|sept.|oct.|nov.|déc.)\s(\d{4})\b',       # Formats abréviation mois AAAA
    ]

    months = {
        "janvier": "01", "février": "02", "mars": "03", "avril": "04",
        "mai": "05", "juin": "06", "juillet": "07", "août": "08",
        "septembre": "09", "octobre": "10", "novembre": "11", "décembre": "12",
        "janv.": "01", "fév.": "02", "mar": "03", "avr.": "04",
        "mai.": "05", "juin": "06", "juil.": "07", "aout": "08",
        "sept.": "09", "oct.": "10", "nov.": "11", "déc.": "12"
    }

    dates = []

    for pattern in itertools.chain(date_patterns1,date_patterns2):
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match) == 3:  # Dates classiques
                print("TEST MATCH a 3 item : ", match[0], match[1], match[2])
                if match[2].isdigit() and len(match[2]) == 2:  # Corriger les années sur deux chiffres
                    year = f"20{match[2]}" if int(match[2]) < 50 else f"19{match[2]}"
                else:
                    year = match[2]

                if match[1].lower() in months:  # Mois en lettres -> Numéro
                    month = months[match[1].lower()]
                else:
                    month = match[1].zfill(2)

                day = match[0].zfill(2)

                month_word = [k for k, v in months.items() if v == month][0]
                dates.append(f"{year}/{month_word}")

                extracted_dates = list(set(dates)) # Retirer les doublons

                return extracted_dates

    for pattern in date_patterns3:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match) == 2:  # Dates MM/AAAA ou AAAA/MM
                print("TEST MATCH a 2 item : ", match[0], match[1])
                if match[1].isdigit() and len(match[1]) == 2:  # Corriger les années sur deux chiffres
                    year = f"20{match[1]}" if int(match[1]) < 50 else f"19{match[1]}"
                else:
                    year = match[1]

                if match[0].lower() in months:  # Mois en lettres -> Numéro
                    month = months[match[0].lower()]
                else:
                    month = match[0].zfill(2)

                day = 1

                dates.append(f"{day}/{month}/{year}")

                extracted_dates = list(set(dates)) # Retirer les doublons

                return extracted_dates

#pour la récupération des mots clés
def analyse_fichier(file_path: str = None):
    """Analyse a file and return the keywords.

    :param str file_path: path to the file to analyse, defaults to None
    :return: List of keywords extracted from the file
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
                return []  # No keywords to return for zip files

            case '.pdf':
                print(f"Analyzing pdf {file_path} ...")
                if is_structured_pdf(file_path):
                    print(f"{file_path} is a structured PDF.\n")
                    return treat_structured_pdf2(file_path)  # Return keywords from structured PDF
                else:
                    print(f"{file_path} is an unstructured PDF.\n")
                    return treat_unstructured_pdf2(file_path)  # Return keywords from unstructured PDF

            case '.png' | '.jpg' | '.jpeg':
                print(f"Analyzing image {file_path} ...")
                return treat_image2(file_path)  # Return keywords from image

            case _:
                print(f"{file_type} is not a file type we currently handle.")
                sys.stdout.flush()
                return []  # Return empty list for unsupported file types

    except zipfile.BadZipFile as e:
        print(f"Bad zip file: {e}")
        return []
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return []
    except PermissionError as e:
        print(f"Permission error: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during file analysis: {e}")
        return []

def treat_structured_pdf2(file_path: str) -> list:
    """Treat a structured PDF file.

    :param str file_path: path to the file to treat
    :return list: extracted keywords
    """
    texte_pdf = extract_text_from_pdf(file_path)

    texte_nettoye = preprocess_text(texte_pdf)

    mots_cles = extraire_mots_cles2(texte_nettoye)

    sys.stdout.flush()
    # Retourner les mots-clés
    return mots_cles

def treat_unstructured_pdf2(file_path: str) -> list:
    """Treat an unstructured PDF file.

    :param str file_path: path to the file to treat
    :return list: extracted keywords
    """
    pdf_text = extract_pdf_text_ocr(file_path)
    cleaned_text = preprocess_text(pdf_text)
    keywords = extraire_mots_cles2(cleaned_text)

    sys.stdout.flush()

    # Retourner les mots-clés
    return keywords

def treat_image2(file_path: str) -> list:
    """Treat an image file.

    :param str file_path: path to the image to treat
    :return list: extracted keywords
    """
    try:
        image_text = extract_image_text_ocr(file_path)
        cleaned_text = preprocess_text(image_text)
        keywords = extraire_mots_cles2(cleaned_text)

        sys.stdout.flush()

        # Retourner les mots-clés
        return keywords
    except Exception as e:
        print(f"An error occurred during image treatment: {e}")
        return []

def extraire_mots_cles2(texte: str) -> list:
    """Extract keywords from a text.

    :param str texte: text to extract keywords from
    :return list: extracted keywords
    """
    try:
        stopwords_fr = stopwords.words('french')
    except LookupError:
        nltk.download('stopwords')
        stopwords_fr = stopwords.words('french')

    # Ajout de stopwords
    stopwords_plus = ['d', 'l', 'avoir', 'etre', 'mettre', 'c', 's', 'a', 'b', 'e', 'f', 'g', 'i', 'j', 'k', 'm', 'n', 'o', 'p', 'q', 'r', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    stopwords_final = stopwords_fr + stopwords_plus

    vectorizer = TfidfVectorizer(
        max_features=50,
        stop_words=stopwords_final,
        ngram_range=(1, 2)
    )
    tfidf_matrix = vectorizer.fit_transform([texte])
    mots_cles = vectorizer.get_feature_names_out()

    return ", ".join(mots_cles)
