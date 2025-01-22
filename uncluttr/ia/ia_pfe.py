""" IA pour la classification de documents PDF en utilisant spaCy et EasyOCR """

import re
import os
import json
from collections import Counter
import easyocr  # OCR sans Tesseract
import spacy
import pymupdf  # fitz = l'ancienne version de PyMuPDF pour lire les PDF (jsp pk on uitlise pas PyMuPDF directement)
from uncluttr.file_treatement.file_treatement import get_base_app_files_path

nlp = spacy.load("fr_core_news_sm")


# Télécharger le modèle spacy si nécessaire
# def check_and_download_dependencies():
#     try:
#         spacy.cli.download("fr_core_news_sm")
#         print("Spacy model downloaded successfully.")
#     except Exception as e:
#         print("Erreur lors du téléchargement du modèle spacy :", e)

# check_and_download_dependencies()
# nlp = spacy.load("fr_core_news_sm")

# Fonction pour extraire le texte d'un PDF avec PyMuPDF
def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Le fichier spécifié n'existe pas : {pdf_path}")
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()  # Extraire le texte de chaque page
    doc.close()
    return text

# OCR avec EasyOCR pour les PDF contenant des images
def ocr_with_easyocr(pdf_path):
    reader = easyocr.Reader(["fr"])  # Supporte le français
    results = reader.readtext(pdf_path, detail=0)
    return " ".join(results)

def ajout_stopwords():
    custom_stop_words = ["d", "l", "avoir", "etre", "mettre", "c", "s", "a", "b", "e", "f", "g", "i", "j", "k", "m", "n", "o", "p", "q", "r", "t", "u", "v", "w", "x", "y", "z"]

    # Ajout de chaque mot à la liste de stop words de spacy
    for word in custom_stop_words:
        nlp.Defaults.stop_words.add(word)
        lexeme = nlp.vocab[word]
        lexeme.is_stop = True

# Prétraitement du texte
def preprocess_text(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())  # Nettoyer les caractères inutiles
    doc = nlp(text)
    lemmatized_text = ' '.join([token.lemma_ for token in doc if not token.is_stop])
    return lemmatized_text

# Extraction des mots les plus fréquents
def get_most_frequent_words(text, top_n=10):
    words = text.split()
    word_counts = Counter(words)
    return word_counts.most_common(top_n)

# Identification de la catégorie de document
def choose_document_tag(frequent_words):
    document_tags = []


    base_path = get_base_app_files_path()
    document_keywords_path = os.path.join(base_path, 'configuration', 'document_keywords.json')

    # Lire le fichier JSON et créer un dictionnaire
    with open(document_keywords_path, 'r', encoding='utf-8') as json_file:
        document_keywords = json.load(json_file)

    for tag, keywords in document_keywords.items():
        common_keywords = [word for word in frequent_words if word in keywords]
        if common_keywords:
            document_tags.append((tag, len(common_keywords)))
    print ("common_keywords : ")
    print (common_keywords)
    if document_tags:
        document_tags.sort(key=lambda x: x[1], reverse=True)
        print ("document_tags : ")
        print (document_tags)
        return document_tags[0][0]
    return "Document inconnu"

# Première version : Extraction de la date pour document non structuré
def extract_date_unstructuredfile(text):
    # Expression régulière pour capturer les dates

    date_pattern = r'\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b'
    matches = re.findall(date_pattern, text)

    if matches:
        # Reformater la date trouvée
        for match in matches:
            day, month, year = match
            formatted_date = f"{int(day):02d}-{int(month):02d}-{year}"
            return formatted_date  # Retourne la première date trouvée
    return "Aucune date trouvée"

# Pipeline principal
def process_document(pdf_path):
    try:
        extracted_text = extract_text_from_pdf(pdf_path)

        if not extracted_text.strip():
            # Si aucun texte n'est trouvé, utiliser l'OCR
            extracted_text = ocr_with_easyocr(pdf_path)

        # Extraction de la date - TEST
        date = extract_date_unstructuredfile(extracted_text)
        
        cleaned_text = preprocess_text(extracted_text)
        frequent_words = get_most_frequent_words(cleaned_text)
        print (frequent_words)
        tag = choose_document_tag([word[0] for word in frequent_words])
        return tag, date
    except Exception as e:
        return f"Erreur lors du traitement du document : {e}"

# Exemple d'utilisation
if __name__ == "__main__":
    ajout_stopwords()

    # check_and_download_dependencies()
    PDF_PATH = os.path.join(os.getcwd(), 'assets', 'example', 'Motivation.pdf')
    document_tag = process_document(PDF_PATH)
    

    # Remplacez ce chemin par le chemin de votre fichier PDF
    #pdf_path = "C:/Users/supio/Documents/ECE ING5/uncluttr - Copie/Faire le mail en Linux.pdf"
    print("Le document appartient à la catégorie :", document_tag)
